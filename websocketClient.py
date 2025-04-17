import asyncio
import websockets
import time

async def connect_to_websocket():
    uri = "ws://192.168.1.68:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected")
        await websocket.send("Hello Server!")
        time.sleep(10)
        await websocket.send("message 2")
        
        response = await websocket.recv()
        print(f"Received: {response}")
        
asyncio.run(connect_to_websocket())