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
        '''
            This function extructs from a sentence words that may use as search keys

            @param sentence: The sentence
            @return: A dictionary that contains the search type, the search keys and their values
        '''

        words = sentence.lower().split()

        for i, word in enumerate(words):
            if word in all_keys:
                for j in range(i + 1, len(words)):
                    if words[j] not in {'value', 'is', 'for', 'the', 'with', 'of'}:
                        return {'type': 'database search' if word in attack_keys else 'online search', word: words[j]}
                    
        return 'Invalid request'

    @staticmethod
    def getVirustotalResults(sentence: str):
        '''
            This function gets the results from virustotal's api if required (when not searching for attacks in the local database)

            @param sentence: The sentence (Required for getting the search keys and values)
            @return: The status of the file (clean, malicious, unknown) or an error
        '''

        res = AI.extract_key_value(sentence)

        if isinstance(res, dict):
            for key, value in res.items():
                if key == 'type':
                    continue

                # Distinction between a search within the local database or online search
                if key in attack_keys:
                    return f'attack {key},{value}'

                key_type = ''

                # Getting the correct type of searched value
                if key in encryption_types:
                    key_type = 'file'
                    
                elif key in url_like_words:
                    key_type = 'url'

                elif key in ip_address_like_words:
                    key_type = 'ip-address'

                # Initiating request requirements
                url = f'https://www.virustotal.com/vtapi/v2/{key_type}/report'
                params = {'apikey': apikey, 'resource': value}

                # Getting the response
                req = requests.get(url, params=params)

                # Raising value is not a type of "key" error
                if req.status_code != 200:
                    return f'{value} is not a {key}'
                
                response = req.json()

                # Checking whethere the searched data is clean, malicious or unknown
                if key in encryption_types | url_like_words:
                    return 'Malicious' if response['positives'] > 0 else 'Clean'

                elif key in ip_address_like_words:
                    return 'Malicious' if response['detected_urls'] else 'Clean' 
                
        return 'Unknown'


async def upload_file(path, name):
    '''
        This function uploads a file to virustotal using its api

        @param path: The path of the file
        @param name: The name of the file (with its type)
        @return: The id of the file and a link for status check
    '''

    mime_type, _ = mimetypes.guess_type(name)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    url = "https://www.virustotal.com/api/v3/files"
    
    # Checking if the file is larger than 32MB (Part of the protocol of virustotal's api)
    if os.path.getsize(path) >= 32 * 1024 * 1024:
        url += '/upload_url'

    # Initiating all request requirements
    files = { "file": (name, open(path, "rb"), mime_type) }
    headers = {"accept": "application/json", "x-apikey": apikey}

    # Getting the response from virustotal
    response = requests.post(url, files=files, headers=headers)

    return response.json()['data']['id'], response.json()['data']['links']['self']


async def wait_for_upload_completed(id, url):
    '''
        This function waits until the file's scan is complete

        @param id: The id of the file
        @param url: The status url
        @return: The new sha256 base id
    '''

    # Initiating all request requirements
    headers = {"accept": "application/json", "x-apikey": apikey}

    # Getting the server's response
    response = requests.get(url, headers=headers)

    # Waiting until the scan is completed
    while response.status_code == 200 and response.json()['data']['attributes']['status'] != 'completed':
        time.sleep(20)
        response = requests.get(url, headers=headers)

    return response.json()['meta']['file_info']['sha256']


async def get_relations(id):
    '''
        This function gets the 'log' from the sandbox os virustotal

        @param id: The id of the file
        @return: A dictionary of lists that contains the reasons
    '''

    # Initiating a list of all relations types
    relations = ['bundled_files', 'execution_parents', 'contacted_ips', 'contacted_domains', 'dropped_files']

    # Initiating the dictionary to keep the reasons
    relations_responses = {'bundled_files': [], 'execution_parents': [], 'contacted_ips': [], 'contacted_domains': [], 'dropped_files': []}

    # Checking all relation types
    for relation in relations:

        # Initiating all request requirement
        url = f"https://www.virustotal.com/api/v3/files/{id}/{relation}?limit=40"

        headers = {"accept": "application/json", "X-Apikey": apikey}

        # Getting the response from virustotal
        response = requests.get(url, headers=headers)

        response_dict = response.json()

        names = []

        # Checking for all relation types

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

        # Adding the current reasons to the dictionary
        relations_responses[relation] = names

    return relations_responses


async def handler(websocket, _):
    async for message in websocket:
        print(f'message: {message}')
        
        # Checking whethere a file were sent

        if message.startswith('{') and message.endswith('}'):
            data = json.loads(message)
            current_filename = data.get('filename')
            file_path = os.path.join('uploads',current_filename)

            # Waiting until the file is done being sent from the frontend
            file_content = await websocket.recv()

            while True:
                chunk = await websocket.recv()

                if chunk == 'EOF':
                    break

                file_content += chunk

            # Creating a new directory if not exists to store the file
            if not os.path.exists('uploads'):
                os.makedirs('uploads')

            # Writing the file in the directory
            with open (file_path, 'wb') as file:
                file.write(file_content)
            
            # Getting the id and the url of the file from upload_file function
            id, url = await upload_file(file_path, current_filename)

            # Deleting the file
            os.remove(file_path)
            
            # Getting the sha256 base id from wait_for_upload_completed function
            sha_id = await wait_for_upload_completed(id, url)

            # Setting the result to the relations dictionary from get_relations function
            result = await get_relations(sha_id)
        
        # Checking if it is a normal or AI based search
        else:
            msg = message.lower()
            
            # Checking if is an AI search
            if msg.startswith('ai search '):

                # Getting the AI results
                result = [AI.getVirustotalResults(msg[10:])]

                # Checking if a local search is needed
                if 'attack ' in result[0]:
                    result = result[0].replace('attack ', '').split(',')
                    
                    # Fitting possible platforms
                    if 'platform' in result[0].lower():
                        attack_platforms: dict[str, str] = {'windows': 'Windows', 'linux': 'Linux', 'macos': 'macOS', 'mac-os': 'macOS', 'network': 'Network',
                                    'pre': 'PRE', 'containers': 'Containers', 'iaas': 'IaaS', 'azure-ad': 'Azure AD',
                                    'office-365': 'Office 365', 'saas': 'SaaS', 'google-workspace': 'Google Workspace'}                        

                        query = {'x_mitre_platforms': {'$in': [attack_platforms[result[1]]]}}

                    # If is non-platform base search
                    else:
                        query = {} if msg == 'all' else {result[0]: {'$regex': result[1], '$options': 'i'}}

                    # Getting the results from the database
                    result = list(collection.find(query, {'_id': 0}))

            # Checking if is a normal search
            else:
                msg = msg.replace('normal search', '')

                # Question
                query = {} if msg == 'all' else {'description': {'$regex': msg.replace('normal search ', ''), '$options': 'i'}}

                # Getting the results from the database
                result = list(collection.find(query, {'_id': 0}))

        # Sending the result
        await websocket.send(json.dumps(result))

async def main():
    async with websockets.serve(handler, 'localhost', 8000):
        await asyncio.Future()

# Initiating connection with the local mongodb database's collection
collection = MongoClient('mongodb://localhost:27017/')['ninjas_database']['attacks_patterns_collection']

print('The server is running')
asyncio.run(main())
