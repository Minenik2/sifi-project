import time
import numpy as np
import matplotlib.pyplot as plt
import sifi_bridge_py as sbp
import time
import calculatePosition
import json
# server managment
import asyncio
import websockets
# calculate position
import math

# start the websocket client
async def send_data(tag, data):
    async with websockets.connect("ws://localhost:8735") as websocket:
        print(data)
        await websocket.send(json.dumps([tag, data]))
        message = await websocket.recv()
        print(message)

def processDataEMG(emg):
    return np.sqrt(np.abs(emg)) * 1000

# calculating the pitch jaw and roll from the IMU data
def quaternion_to_euler(qw, qx, qy, qz):
    """
    Convert a quaternion into Euler angles (pitch, roll, yaw).
    
    Parameters:
    qw, qx, qy, qz: Quaternion components.
    
    Returns:
    A tuple of (pitch, roll, yaw) in radians.
    """
    # Roll (X-axis rotation)
    roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    
    # Pitch (Y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)
    
    # Yaw (Z-axis rotation)
    yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
    
    return pitch, roll, yaw


    

#Send data to Pure Data
#for index, row in df_filtered.iterrows():
 #   send_pd_message("emg", row["Duration"])

def stream_data(bridge, number_of_seconds_to_stream=1990, device_type=sbp.DeviceType.BIOPOINT_V1_3, output_file='collected_data.pkl'):
    """
    Streams data from a BioPoint device for a specified duration.

    Parameters:
    bridge (sbp.SifiBridge): The SifiBridge object to communicate with the BioPoint device.
    number_of_seconds_to_stream (int): Duration in seconds to stream data.
    device_type: The type of BioPoint device to connect to.
    output_file (str): Filename to save the collected data.
    """

    emgCounter = 0
    # List all BLE devices to see the name and ID of your BioPoint.
    devices = bridge.list_devices(sbp.ListSources.BLE)
    print("Available devices:")
    print(devices)

    # Attempt to connect to the specified device type.
    print(f"Attempting to connect to device type: {device_type}")
    connected = False
    while not connected:
        try:
            connected = bridge.connect(device_type)
            if not connected:
                print("Failed to connect... retrying")
                time.sleep(1)
        except Exception as e:
            print(f"Exception occurred while trying to connect: {e}")
            time.sleep(1)

    print("Connected to BioPoint device!")
    time.sleep(1)

    # Enable all the channels we want to record data from.
    bridge.set_channels(ecg=True, emg=True, eda=True, imu=True, ppg=True)
    bridge.set_low_latency_mode(on=True)

    
    # Create the structure that will receive the streamed data.
    data = {
        "ECG": [],
        "EMG": [],
        "EDA": [],
        "IMU": {"ax": [], "ay": [], "az": [], "qw": [], "qx": [], "qy": [], "qz": []},
        "PPG": {"b": [], "g": [], "r": [], "ir": []}
    }

    # Start data streaming.
    bridge.start()
    first_packet_ignored = False # packet lock for IMU
    start_time = time.time()
    print(f"Started streaming data for {number_of_seconds_to_stream} seconds...")
    try:
        while time.time() - start_time < number_of_seconds_to_stream:
            # Retrieve data packet from the bridge.
            packet = bridge.get_data_with_key("data")
            # print(packet)
            # Process the packet based on its type.
            if packet["packet_type"] == "ecg":
                ecg = packet["data"]["ecg"]
                data["ECG"].extend(ecg)
            elif packet["packet_type"] == "emg":
                # print(packet["data"]["emg"])
                emg = packet["data"]["emg"]
                emg = processDataEMG(emg)
                #print(emg)
                data["EMG"].extend(emg)
                # Sends the emg data to max
                #send_pd_message("emg", data["EMG"][-1])
            elif packet["packet_type"] == "eda":
                eda = packet["data"]["eda"]
                data["EDA"].extend(eda)
            elif packet["packet_type"] == "imu":
                imu = packet["data"]
                
                # code taken from tom on how to handle IMU data
                # Ignore the first IMU packet.
                if not first_packet_ignored:
                    first_packet_ignored = True
                    print("First IMU packet ignored.")
                    continue  # Skip processing the first packet.
                # Ensure quaternion values are present in the IMU data.
                if all(param in imu and len(imu[param]) == 8 for param in ["qw", "qx", "qy", "qz"]):
                    pitch_list = []
                    roll_list = []
                    yaw_list = []
                    
                    # Process all 8 values in the packet.
                    for i in range(8):
                        qw = imu["qw"][i]
                        qx = imu["qx"][i]
                        qy = imu["qy"][i]
                        qz = imu["qz"][i]
                        
                        # Calculate pitch, roll, and yaw for this set of quaternion values.
                        pitch, roll, yaw = quaternion_to_euler(qw, qx, qy, qz)
                        
                        # Append to the corresponding lists.
                        pitch_list.append(pitch)
                        roll_list.append(roll)
                        yaw_list.append(yaw)
                    
                    # Send the lists of pitch, roll, and yaw values over UDP.
                    asyncio.run(send_data("PITCH", pitch_list))
                    asyncio.run(send_data("ROLL", roll_list))
                    asyncio.run(send_data("YAW", yaw_list))  
                    
                    ## end of toms IMU code ##
                
                
                for k, v in imu.items():
                    ## if its none is in the dataset, set none to 0
                    if v[0] is None:
                        for i in range(len(v)):
                            if v[i] is None:
                                v[i] = 0.0
                    #if "a" in k and data["IMU"][k]:
                        #send_pd_message(k, data["IMU"][k][-1])
                    data["IMU"][k].extend(v)
                    
            elif packet["packet_type"] == "ppg":
                ppg = packet["data"]
                for k, v in ppg.items():
                    data["PPG"][k].extend(v)

            if data["EMG"]:
               asyncio.run(send_data("EMG", data["EMG"][-1]))
               print(data["EMG"][-1])
               print()
            else:
               print("No EMG data available.")
    except KeyboardInterrupt:
        print("Data streaming interrupted by user.")
    except Exception as e:
        print(f"An error occurred during data streaming: {e}")
    finally:
        # Stop data streaming and disconnect the bridge.
        bridge.stop()
        bridge.disconnect()
        print("Data streaming stopped and bridge disconnected.")

    

    # Optionally, process or visualize the data here.
    # For example, plot the ECG data if any was collected.
    #if data["EMG"]:
        # print(data["EMG"])
        # print(len(data["EMG"]))
        # plt.figure()
        # plt.plot(data["EMG"])
        # plt.title("EMG Data")
        # plt.xlabel("Sample")
        # plt.ylabel("Amplitude")
        # plt.show()

if __name__ == '__main__':
    EXECUTABLE_PATH = "./sifibridge.exe"
    # Initialize the SifiBridge with the path to the executable.
    bridge = sbp.SifiBridge(EXECUTABLE_PATH)
    # Call the stream_data function with the bridge instance.
    stream_data(bridge=bridge)
    

    
    
