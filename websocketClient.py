import asyncio
import websockets
import time

async def connect_to_websocket():
    uri = "ws://192.168.1.68:8080"
    async with websockets.connect(uri) as websocket:
        print("Connected")
        # await websocket.send("Hello Server!")
        # time.sleep(10)
        # await websocket.send("message 2")
        
        # response = await websocket.recv()
        # print(f"Received: {response}")
        moves = ["e2e4", "e7e5",
"g1f3", "b8c6",
"f1b5", "a7a6",
"b5a4", "g8f6",
"e1g1", "f6e4",
"d2d4", "b7b5",
"a4b3", "d7d5",
"d4e5", "c8e6",
"c2c3", "e4c5",
"b3c2", "d5d4",
"c3d4", "c5d3",
"c2d3", "e6d5",
"b1c3", "d5d3",
"d1d3", "c6e5",
"d3e4", "e5d3",
"e4d3", "d8d3",
"f1d1", "d3c2",
"d1d7", "f8e7",
"d7a7", "e7d6",
"a7a6", "c2b3",
"a6a1", "e8g8",
"a1b1", "b3c4",
"b1b2", "f8e8",
"a1e1", "e8e1",
"f3e1", "c4f1",
"g1f1", "g8f8",
"b2b5", "f8e7",
"b5c5", "d6e5",
"c5c7", "e7d6",
"c7c6", "d6e7",
"c3e4", "h7h6",
"e4g5", "h6g5",
"e1g2", "f7f6",
"g2e3", "e7f7",
"f1e2", "f7e6",
"e3c4", "e5d4",
"c4d6", "e6e5",
"d6f7", "e5d5",
"e2d3", "d5e5",
"f7e5", "f6e5",
"d3e4"]
        for move in moves:
            websocket.send(move)
            await websocket.recv()
            asyncio.sleep(10)
        
asyncio.run(connect_to_websocket())