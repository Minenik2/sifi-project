import asyncio
import websockets
import json

dataEMG = []
dataPITCH = []
dataROLL = []
dataYAW = []

# define a function to handle incoming messages from clients
async def handle_data(websocket, path):
    global dataEMG
    data = await websocket.recv()
    if data != "ping":
        if data == "javascript":
            print("p5.js connected")
            if dataEMG:
                await websocket.send(dataEMG[-1])
            if dataPITCH:
                await websocket.send(dataPITCH[-1])
            if dataROLL:
                await websocket.send(dataROLL[-1])
            if dataYAW:
                await websocket.send(dataYAW[-1]) 
        else:
            dataPacket = json.loads(data)
            if dataPacket[0] == "EMG":
                dataEMG.append(data)
            elif dataPacket[0] == "PITCH":
                dataPITCH.append(data)
            elif dataPacket[0] == "ROLL":
                dataROLL.append(data)
            elif dataPacket[0] == "YAW":
                dataYAW.append(data)
            #send confimation to bioarm client
            print(dataPacket)
            await websocket.send("data send!")
    

# start the websocket server
async def start_server():
    async with websockets.serve(handle_data, "localhost", 8735):
        print('websockets server starterd')
        await asyncio.Future()
        
# run the server
asyncio.run(start_server())