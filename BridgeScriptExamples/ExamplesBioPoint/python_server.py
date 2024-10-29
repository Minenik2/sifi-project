import asyncio
import websockets
import json

# define a function to handle incoming messages from clients
async def handle_data(websocket, path):
    data = await websocket.recv()
    if data:
        # Save the collected data to a file.
        with open('biopoint_data.json', 'w') as f:
            json.dump(data, f)
        print("Data saved! as biopoint_data.json")
    await websocket.send("data recieved!")
    

# start the websocket server
async def start_server():
    async with websockets.serve(handle_data, "localhost", 8765):
        print('websockets server starterd')
        await asyncio.Future()
        
# run the server
asyncio.run(start_server())