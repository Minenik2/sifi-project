import asyncio
import websockets
import json

dataEMG = []

# define a function to handle incoming messages from clients
async def handle_data(websocket, path):
    global dataEMG
    data = await websocket.recv()
    if data != "ping":
        if data == "javascript":
            print("p5.js connected")
            if dataEMG:
                await websocket.send(dataEMG[-1])
        else:
            dataEMG.append(data)
            #send confimation to bioarm client
            print(data)
            await websocket.send("data send!")
    

# start the websocket server
async def start_server():
    async with websockets.serve(handle_data, "localhost", 8765):
        print('websockets server starterd')
        await asyncio.Future()
        
# run the server
asyncio.run(start_server())