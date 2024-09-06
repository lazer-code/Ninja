import asyncio
import websockets

async def handler(websocket, path):
    async for message in websocket:
        # Process message and send response
        await websocket.send(f"{message}")

start_server = websockets.serve(handler, "localhost", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
