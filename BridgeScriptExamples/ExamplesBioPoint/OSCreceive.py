from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

# Define handler functions to process incoming OSC messages and print them
def print_pitch(address, *args):
    print(f"{address}: Pitch = {args[0]}")

def print_roll(address, *args):
    print(f"{address}: Roll = {args[0]}")

def print_yaw(address, *args):
    print(f"{address}: Yaw = {args[0]}")

def print_emg(address, *args):
    print(f"{address}: EMG = {args[0]}")

# Set up the dispatcher and bind each OSC address to a handler function
dispatcher = Dispatcher()
dispatcher.map("/pitch", print_pitch)
dispatcher.map("/roll", print_roll)
dispatcher.map("/yaw", print_yaw)
dispatcher.map("/emg", print_emg)

# Define the IP and port to listen on (localhost and port 9000)
IP_ADDRESS = "127.0.0.1"
PORT = 9000

# Create and start the server
server = osc_server.BlockingOSCUDPServer((IP_ADDRESS, PORT), dispatcher)
print(f"Listening for OSC messages on {IP_ADDRESS}:{PORT}...")
server.serve_forever()
