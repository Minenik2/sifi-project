import asyncio
import websockets
import keyboard

# start the websocket client
async def start_client():
    async with websockets.connect("ws://localhost:8765") as websocket:
        done = False
        while not done:
            await websocket.send("buzz")
            message = await websocket.recv()
            print(message)
            done = True

# run the client
asyncio.run(start_client())