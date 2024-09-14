import os
import asyncio
import websockets
import json
import subprocess
from pymongo import MongoClient

async def handler(websocket, path):
    try:
        async for message in websocket:
            message: str = message.lower()

            print (f'Message: {message}')

            client = MongoClient('mongodb://localhost:27017/')
            db = client['ninjas_database']
            collection = db['attacks_patterns_collection']

            if message.startswith('ai search '):
                message = message.replace('ai search ', '')

                result = subprocess.run(['python', 'AI.py', message], capture_output=True, text=True)
                with open ('output.txt', 'r') as file:
                    results: list[dict[str, str]] = [json.load(file)]
                    print(results)
                os.remove('output.txt')
                
                print('ai')


            elif message.startswith('normal search '):
                message = message.replace('normal search ', '')

                results: list[dict[str, str]] = list(collection.find(
                    {'description': {'$regex': message, '$options': 'i'}},
                    {'_id': 0, 'name': 1, 'description': 1, 'id': 1, 'x_mitre_platforms': 1, 'x_mitre_detection': 1, 'phase_name': 1}
                ))

                if message == '':
                    results: list[dict[str, str]] = list(collection.find(
                        {},
                        {'_id': 0, 'name': 1, 'description': 1, 'id': 1, 'x_mitre_platforms': 1, 'x_mitre_detection': 1, 'phase_name': 1}
                    ))
                
                    print('all')

                else:
                    print('normal')

            if message == 'all':
                results: list[dict[str, str]] = list(collection.find(
                    {},
                    {'_id': 0, 'name': 1, 'description': 1, 'id': 1, 'x_mitre_platforms': 1, 'x_mitre_detection': 1, 'phase_name': 1}
                ))
                
                print('all')


            if message.startswith('select '):
                message = message.replace('select ', '')
                results: list[dict[str, str]] = [collection.find_one({'name': message})]

                print('select')
            
            str_results: str = json.dumps(results, default=str)
            await websocket.send(str_results)

    except Exception as e:
        print(f'Error: {e}')

while True:
    start_server = websockets.serve(handler, 'localhost', 8000)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
