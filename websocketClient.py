import asyncio
import websockets

async def connect_to_websocket():
    uri = "ws://192.168.1.68:8080"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello Server!")
        
        response = await websocket.recv()
        print(f"Received: {response}")
        
asyncio.run(connect_to_websocket())