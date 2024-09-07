import asyncio
import websockets
import json
from pymongo import MongoClient

async def handler(websocket, path):
    try:
        async for message in websocket:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['ninjas_database']
            collection = db['attacks_patterns_collection']

            results = list(collection.find(
                {'description': {'$regex': message, '$options': 'i'}},
                {'_id': 0, 'name': 1, 'description': 1, 'id': 1, 'x_mitre_platforms': 1, 'x_mitre_detection': 1, 'phase_name': 1}
            ))

            if results:
                back = results
            else:
                back = []
            
            with open('file.json', 'w') as file:
                json.dump(back, file, indent=3)

            await websocket.send(json.dumps(back))

    except Exception as e:
        print(f"Error: {e}")

start_server = websockets.serve(handler, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
