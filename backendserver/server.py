import os, asyncio, websockets, json, requests
from pymongo import MongoClient

attack_keys = {"id", "description", "phase_name", "name", "platform", "detection"}
all_keys = attack_keys | {"md5", "sha1", "sha256", "sha512", "bcrypt", "aes", "rsa", "url", "website", "link", "ip", "ipaddress", "hash", "checksum", "filehash"}

current_filename = ''

class AI:
    @staticmethod
    def extract_key_value(sentence):
        words = sentence.lower().split()

        for i, word in enumerate(words):
            if word in all_keys:
                for j in range(i + 1, len(words)):
                    if words[j] not in {"value", "is", "for", "the", "with", "of"}:
                        return {'type': 'database search' if word in attack_keys else 'online search', word: words[j]}
                    
        return "Invalid request"

    @staticmethod
    def getVirustotalResults(sentence: str):
        res = AI.extract_key_value(sentence)

        if isinstance(res, dict):
            apikey = '3704563ee024370204fca6814514fe33d0713f10b4385bbd9d4d8f552fd2fec0'

            for key, value in res.items():
                if key == 'type':
                    continue

                if key in attack_keys:
                    return f'attack {key},{value}'
                
                if key not in attack_keys:
                    r = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params={'apikey': apikey, 'resource': value})
                    return 'Malicious' if r.json().get('positives', 0) > 0 else 'Clean'
                
        return 'Unknown'

collection = MongoClient('mongodb://localhost:27017/')['ninjas_database']['attacks_patterns_collection']

async def handler(websocket, _):
    try:
        async for message in websocket:
            print(message)
            try:
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

                with open(file_path, 'wb') as file:
                    file.write(file_content)

                result: list = ['FILE']
            
            except Exception as e:
                print(f'Error1: {e}')

                if type(message) is str:
                    msg = message.lower()
                    
                    if msg.startswith('ai search '):
                        result = [AI.getVirustotalResults(msg[10:])]
                        
                        if 'attack ' in result[0]:
                            result = result[0].replace('attack ', '').split(',')
                            
                            if 'platform' in result[0].lower():
                                attack_platforms: dict[str, str] = {'windows': 'Windows', 'linux': 'Linux', 'macos': 'macOS', 'mac-os': 'macOS', 'network': 'Network',
                                            'pre': 'PRE', 'containers': 'Containers', 'iaas': 'IaaS', 'azure-ad': 'Azure AD',
                                            'office-365': 'Office 365', 'saas': 'SaaS', 'google-workspace': 'Google Workspace'}                        

                                query = {"x_mitre_platforms": {"$in": [attack_platforms[result[1]]]}}

                            else:
                                query = {} if msg == 'all' else {result[0]: {'$regex': result[1], '$options': 'i'}}

                            result = list(collection.find(query, {'_id': 0}))

                    else:
                        msg = message.replace('normal search', '')
                        query = {} if msg == 'all' else {'description': {'$regex': msg.replace('normal search ', ''), '$options': 'i'}}
                        result = list(collection.find(query, {'_id': 0}))

            print(result)
            await websocket.send(json.dumps(result))

    except Exception as e:
        print(f'Error2: {e}')
        await websocket.close()

async def main():
    async with websockets.serve(handler, 'localhost', 8000):
        await asyncio.Future()

print('The server is running')
asyncio.run(main())
