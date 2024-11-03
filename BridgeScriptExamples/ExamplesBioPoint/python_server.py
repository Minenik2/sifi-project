import asyncio
import websockets
import json

# Data storage with a maximum length for each list
MAX_DATA_LENGTH = 100
dataEMG = []
dataPITCH = []
dataROLL = []
dataYAW = []

# Define a function to handle incoming messages from clients
async def handle_data(websocket, path):
    global dataEMG, dataPITCH, dataROLL, dataYAW
    
    try:
        while True:
            data = await websocket.recv()

            if data == "ping":
                continue  # Ignore ping messages

            if data == "javascript":
                print("p5.js connected")

                # Send all available data as JSON to the client in one message
                latest_data = {
                    "EMG": dataEMG[-1] if dataEMG else None,
                    "PITCH": dataPITCH[-1] if dataPITCH else None,
                    "ROLL": dataROLL[-1] if dataROLL else None,
                    "YAW": dataYAW[-1] if dataYAW else None
                }
                await websocket.send(json.dumps(latest_data))
            else:
                # Process incoming data and update corresponding lists
                dataPacket = json.loads(data)
                data_type = dataPacket[0]
                data_value = dataPacket[1]
                
                if data_type == "EMG":
                    dataEMG.append(data_value)
                    dataEMG = dataEMG[-MAX_DATA_LENGTH:]
                elif data_type == "PITCH":
                    dataPITCH.append(data_value)
                    dataPITCH = dataPITCH[-MAX_DATA_LENGTH:]
                elif data_type == "ROLL":
                    dataROLL.append(data_value)
                    dataROLL = dataROLL[-MAX_DATA_LENGTH:]
                elif data_type == "YAW":
                    dataYAW.append(data_value)
                    dataYAW = dataYAW[-MAX_DATA_LENGTH:]

                # Send confirmation to the client that data has been received
                await websocket.send("data received!")
                print(f"Received data: {dataPacket}")

                # Send updated data to p5.js immediately after receiving new data
                latest_data = {
                    "EMG": dataEMG[-1] if dataEMG else None,
                    "PITCH": dataPITCH[-1] if dataPITCH else None,
                    "ROLL": dataROLL[-1] if dataROLL else None,
                    "YAW": dataYAW[-1] if dataYAW else None
                }
                await websocket.send(json.dumps(latest_data))

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client disconnected: {e}")

# Start the WebSocket server
async def start_server():
    async with websockets.serve(handle_data, "localhost", 8735):
        print('WebSocket server started on ws://localhost:8735')
        await asyncio.Future()  # Run forever

# Run the server
asyncio.run(start_server())