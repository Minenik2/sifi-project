import asyncio
import websockets
import json
import random  # For simulating data; replace with your real data source

async def data_stream(websocket, path):
    while True:
        # Replace this with actual data from your armband
        data = {
            "ECG": random.uniform(-1, 1),  # Example data
            "EMG": random.uniform(-1, 1),
            "EDA": random.uniform(-1, 1)
        }
        await websocket.send(json.dumps(data))
        await asyncio.sleep(0.1)  # Adjust based on the desired update rate

# Start the WebSocket server
start_server = websockets.serve(data_stream, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()