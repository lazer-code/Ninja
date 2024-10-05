import os, asyncio, websockets, json, requests, mimetypes, time
from pymongo import MongoClient

attack_keys = {'id', 'description', 'phase name', 'name', 'platform', 'detection'}
encryption_types = {'md5', 'sha1', 'sha256', 'sha512', 'bcrypt', 'aes', 'rsa'}
url_like_words = {'url', 'website', 'link'}
ip_address_like_words = {'ip', 'ipaddress'}

all_keys = attack_keys | encryption_types | url_like_words | ip_address_like_words

current_filename = ''
apikey = os.environ['VIRUSTOTAL_API_KEY']

class AI:
    @staticmethod
    def extract_key_value(sentence):
        words = sentence.lower().split()

        for i, word in enumerate(words):
            if word in all_keys:
                for j in range(i + 1, len(words)):
                    if words[j] not in {'value', 'is', 'for', 'the', 'with', 'of'}:
                        return {'type': 'database search' if word in attack_keys else 'online search', word: words[j]}
                    
        return 'Invalid request'

    @staticmethod
    def getVirustotalResults(sentence: str):
        res = AI.extract_key_value(sentence)

        if isinstance(res, dict):
            for key, value in res.items():
                if key == 'type':
                    continue

                if key in attack_keys:
                    return f'attack {key},{value}'

                url = ''

                if key in encryption_types:
                    url = 'https://www.virustotal.com/vtapi/v2/file/report'
                    params = {'apikey': apikey, 'resource': value}

                elif key in url_like_words:
                    url = 'https://www.virustotal.com/vtapi/v2/url/report'
                    params = {'apikey': apikey, 'resource': value}

                elif key in ip_address_like_words:
                    url = 'https://www.virustotal.com/vtapi/v2/ip-address/report'
                    params = {'apikey': apikey, 'resource': value}


                req = requests.get(url, params=params)

                if req.status_code != 200:
                    return f'{value} is not a {key}'
                
                response = req.json()

                if key in encryption_types | url_like_words:
                    return 'Malicious' if response['positives'] > 0 else 'Clean'

                elif key in ip_address_like_words:
                    return 'Malicious' if response['detected_urls'] else 'Clean' 
                

                
        return 'Unknown'

collection = MongoClient('mongodb://localhost:27017/')['ninjas_database']['attacks_patterns_collection']


async def upload_file(path, name):
    mime_type, _ = mimetypes.guess_type(name)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    url = "https://www.virustotal.com/api/v3/files"

    files = { "file": (path, open(path, "rb"), mime_type) }
    headers = {"accept": "application/json", "x-apikey": apikey}

    response = requests.post(url, files=files, headers=headers)
    print(f'upload response: {response.text}')

    return response.json()['data']['id']


async def wait_for_upload_completed(id):
    print(id)
    url = f"https://www.virustotal.com/api/v3/files/{id}"
    headers = {"accept": "application/json", "x-apikey": apikey}

    response = requests.get(url, headers=headers)
    print(f'status response: {response.text}')

    while response.status_code == 200 and response.json()['data']['attributes']['status'] == 'queued':
        time.sleep(20)
        response = requests.get(url, headers=headers)
        print(f'status response: {response.text}')

    return response.json()['meta']['file_info']['sha256']


async def get_relations(id):
    relations = ['bundled_files', 'execution_parents', 'contacted_ips', 'contacted_domains', 'dropped_files']

    relations_responses = {'bundled_files': [], 'execution_parents': [], 'contacted_ips': [], 'contacted_domains': [], 'dropped_files': []}

    for relation in relations:
        url = f"https://www.virustotal.com/api/v3/files/{id}/{relation}?limit=40"

        headers = {"accept": "application/json", "X-Apikey": apikey}

        response = requests.get(url, headers=headers)
        response_dict = response.json()
        print(f'relation response: {response.text}')

        names = []

        if relation in ['bundled_files', 'dropped_files', 'execution_parents']:
            for item in response_dict['data']:
                if 'attributes' in item and 'meaningful_name' in item['attributes']:
                    names.append(item['attributes']['meaningful_name'])

        elif relation == 'contacted_ips': 
            for item in response_dict['data']:
                if 'attributes' in item and 'network' in item['attributes']:
                    names.append(item['attributes']['network'])

        elif relation == 'contacted_urls': 
            for item in response_dict['data']:
                if 'attributes' in item and 'network' in item['attributes']:
                    names.append(item['attributes']['network'])

        elif relation == 'contacted_domains': 
            for item in response_dict['data']:
                if 'id' in item:
                    names.append(item['id'])

        relations_responses[relation] = names

    return relations_responses


async def handler(websocket, _):
    async for message in websocket:
        print(f'message: {message}')
        
        if message.startswith('{') and message.endswith('}'):
            data = json.loads(message)
            current_filename = data.get('filename')
            file_path = os.path.join('uploads',current_filename)

            file_content = await websocket.recv()

            while True:
                chunk = await websocket.recv()

                if chunk == 'EOF':
                    break

                file_content += chunk

            if not os.path.exists('uploads'):
                os.makedirs('uploads')

            with open (file_path, 'wb') as file:
                file.write(file_content)
            
            id = await upload_file(file_path, current_filename)

            os.remove(file_path)
            
            sha_id = await wait_for_upload_completed(id)

            result = await get_relations(sha_id)
        
        else:
            msg = message.lower()
            
            if msg.startswith('ai search '):
                result = [AI.getVirustotalResults(msg[10:])]

                if 'attack ' in result[0]:
                    result = result[0].replace('attack ', '').split(',')
                    
                    if 'platform' in result[0].lower():
                        attack_platforms: dict[str, str] = {'windows': 'Windows', 'linux': 'Linux', 'macos': 'macOS', 'mac-os': 'macOS', 'network': 'Network',
                                    'pre': 'PRE', 'containers': 'Containers', 'iaas': 'IaaS', 'azure-ad': 'Azure AD',
                                    'office-365': 'Office 365', 'saas': 'SaaS', 'google-workspace': 'Google Workspace'}                        

                        query = {'x_mitre_platforms': {'$in': [attack_platforms[result[1]]]}}

                    else:
                        query = {} if msg == 'all' else {result[0]: {'$regex': result[1], '$options': 'i'}}

                    result = list(collection.find(query, {'_id': 0}))

            else:
                msg = msg.replace('normal search', '')
                query = {} if msg == 'all' else {'description': {'$regex': msg.replace('normal search ', ''), '$options': 'i'}}
                result = list(collection.find(query, {'_id': 0}))

        await websocket.send(json.dumps(result))

async def main():
    async with websockets.serve(handler, 'localhost', 8000):
        await asyncio.Future()

print('The server is running')
asyncio.run(main())
