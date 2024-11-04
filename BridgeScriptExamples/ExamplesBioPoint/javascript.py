import time
import numpy as np
import sifi_bridge_py as sbp
import calculatePosition
import json
import math
from pythonosc.udp_client import SimpleUDPClient
import asyncio

# Configure OSC client for UDP transmission
IP_ADDRESS = "127.0.0.1"  # Localhost
PORT = 9000  # Set to the port you want to use for receiving program
client = SimpleUDPClient(IP_ADDRESS, PORT)

def processDataEMG(emg):
    return np.sqrt(np.abs(emg)) * 1000

# Calculating pitch, yaw, and roll from quaternion data
def quaternion_to_euler(qw, qx, qy, qz):
     # Roll (X-axis rotation)
    roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    
    # Pitch (Y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)
    
    # Yaw (Z-axis rotation)
    yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
    
    return pitch, roll, yaw

async def send_osc_data(tag, values):
    """
    Sends each value with a 20 ms delay to the specified OSC client.
    """
    for value in values:
        client.send_message(tag, value)
        await asyncio.sleep(0.02)  # 20 ms delay

def stream_data(bridge, number_of_seconds_to_stream=1990, device_type=sbp.DeviceType.BIOPOINT_V1_3):
    emgCounter = 0
    devices = bridge.list_devices(sbp.ListSources.BLE)
    print("Available devices:", devices)

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

    bridge.set_channels(ecg=True, emg=True, eda=True, imu=True, ppg=True)
    bridge.set_low_latency_mode(on=True)

    data = {
        "ECG": [], "EMG": [], "EDA": [],
        "IMU": {"ax": [], "ay": [], "az": [], "qw": [], "qx": [], "qy": [], "qz": []},
        "PPG": {"b": [], "g": [], "r": [], "ir": []}
    }

    bridge.start()
    first_packet_ignored = False
    start_time = time.time()
    print(f"Started streaming data for {number_of_seconds_to_stream} seconds...")

    try:
        while time.time() - start_time < number_of_seconds_to_stream:
            packet = bridge.get_data_with_key("data")
            if packet["packet_type"] == "ecg":
                ecg = packet["data"]["ecg"]
                data["ECG"].extend(ecg)
            elif packet["packet_type"] == "emg":
                emg = processDataEMG(packet["data"]["emg"])
                data["EMG"].extend(emg)
            elif packet["packet_type"] == "eda":
                eda = packet["data"]["eda"]
                data["EDA"].extend(eda)
            elif packet["packet_type"] == "imu":
                imu = packet["data"]
                if not first_packet_ignored:
                    first_packet_ignored = True
                    print("First IMU packet ignored.")
                    continue

                if all(param in imu and len(imu[param]) == 8 for param in ["qw", "qx", "qy", "qz"]):
                    pitch_list, roll_list, yaw_list = [], [], []

                    for i in range(8):
                        qw, qx, qy, qz = imu["qw"][i], imu["qx"][i], imu["qy"][i], imu["qz"][i]
                        pitch, roll, yaw = quaternion_to_euler(qw, qx, qy, qz)
                        pitch_list.append(pitch)
                        roll_list.append(roll)
                        yaw_list.append(yaw)
                    
                    # Send each pitch, roll, and yaw with a 20 ms delay
                    asyncio.run(send_osc_data("/pitch", pitch_list))
                    asyncio.run(send_osc_data("/roll", roll_list))
                    asyncio.run(send_osc_data("/yaw", yaw_list))

                for k, v in imu.items():
                    if v[0] is None:
                        v = [0.0 if i is None else i for i in v]
                    data["IMU"][k].extend(v)
            elif packet["packet_type"] == "ppg":
                ppg = packet["data"]
                for k, v in ppg.items():
                    data["PPG"][k].extend(v)

            if data["EMG"]:
               asyncio.run(send_osc_data("/emg", [data["EMG"][-1]]))
               print(data["EMG"][-1])
            else:
               print("No EMG data available.")

    except KeyboardInterrupt:
        print("Data streaming interrupted by user.")
    except Exception as e:
        print(f"An error occurred during data streaming: {e}")
    finally:
        bridge.stop()
        bridge.disconnect()
        print("Data streaming stopped and bridge disconnected.")

if __name__ == '__main__':
    EXECUTABLE_PATH = "./sifibridge.exe"
    bridge = sbp.SifiBridge(EXECUTABLE_PATH)
    stream_data(bridge=bridge)
