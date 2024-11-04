from pythonosc import osc_server, dispatcher
import time
from pynput.keyboard import Key, Controller

# Configuration
ipAddress = '193.157.192.121'  # Your IP address
port_Num = 31000  # Your port number
run_duration = 60  # Duration in seconds to run the server

# Create an OSC dispatcher
dispatcher = dispatcher.Dispatcher()
keyboard = Controller()

current_keys = set()  # To track currently pressed keys

# Define thresholds
PITCH_THRESHOLD = 0.05 # Pitch thresholdwss
YAW_THRESHOLD = 0.1  # Yaw threshold

# Variables to store initial pitch and yaw values
initial_pitch = None
initial_yaw = None

def handler(address, *args):
    global initial_pitch, initial_yaw
    
    if len(args) == 3:
        pitch, _, yaw = args  # Ignore roll
        
        # Initialize the zero point based on the first received values
        if initial_pitch is None or initial_yaw is None:
            initial_pitch = pitch
            initial_yaw = yaw
            print("Initial pitch and yaw set to: {}, {}".format(initial_pitch, initial_yaw))
            return
        
        # Calculate the relative pitch and yaw
        relative_pitch = pitch - initial_pitch
        relative_yaw = yaw - initial_yaw
        
        # Print the received data for debugging
        #print("Receiving data: Relative Pitch: {}, Relative Yaw: {}".format(relative_pitch, relative_yaw))

        # Control logic based on relative pitch for W and S keys
        if relative_pitch > PITCH_THRESHOLD:
            press_key('w')  # Move up
        elif relative_pitch < -PITCH_THRESHOLD:
            press_key('s')  # Move down
        else:
            release_key('w')
            release_key('s')

        # Inverted control logic based on relative yaw for A and D keys
        if relative_yaw > YAW_THRESHOLD:
            press_key('a')  # Move left (inverted)
        elif relative_yaw < -YAW_THRESHOLD:
            press_key('d')  # Move right (inverted)
        else:
            release_key('a')
            release_key('d')

def press_key(key):
    if key not in current_keys:
        current_keys.add(key)
        print(f"Pressing key: {key}")  # Debugging print
        keyboard.press(key)

def release_key(key):
    if key in current_keys:
        print(f"Releasing key: {key}")  # Debugging print
        current_keys.remove(key)
        keyboard.release(key)

def reset_keys():
    # Release all currently pressed keys
    for key in current_keys.copy():
        keyboard.release(key)
    current_keys.clear()

# Map the OSC address to the handler
dispatcher.map("/gyrosc/gyro", handler)
server = osc_server.ThreadingOSCUDPServer((ipAddress, port_Num), dispatcher)
print("Serving on {}".format(server.server_address))

start_time = time.time()
try:
    while True:
        server.handle_request()
        
        # Check if the run duration has elapsed
        if time.time() - start_time > run_duration:
            print("Run duration reached. Stopping server.")
            break
            
except KeyboardInterrupt:
    print("Server manually closed.")
finally:
    server.server_close()
    reset_keys()  # Release all keys before closing
    print("Server closed after {} seconds.".format(run_duration))