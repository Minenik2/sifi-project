import time
import numpy as np
import matplotlib.pyplot as plt
import sifi_bridge_py as sbp
import pickle
import os
import time
from pythonosc import udp_client


# Create an OSC client to send messages to Pure Data
pd_client = udp_client.SimpleUDPClient("192.168.1.171", 7777)  # Adjust host and port accordingly


#Function to send OSC messages to Pure Data
def send_pd_message(parameter, value):
    address = f"/biopoint/{parameter}"  # Define OSC address pattern
    pd_client.send_message(address, value)

#Send data to Pure Data
#for index, row in df_filtered.iterrows():
 #   send_pd_message("emg", row["Duration"])

def stream_data(bridge, number_of_seconds_to_stream=10, device_type=sbp.DeviceType.BIOPOINT_V1_3, output_file='collected_data.pkl'):
    """
    Streams data from a BioPoint device for a specified duration.

    Parameters:
    bridge (sbp.SifiBridge): The SifiBridge object to communicate with the BioPoint device.
    number_of_seconds_to_stream (int): Duration in seconds to stream data.
    device_type: The type of BioPoint device to connect to.
    output_file (str): Filename to save the collected data.
    """
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
                data["EMG"].extend(emg)
                # Sends the emg data to max
                send_pd_message("emg", data["EMG"][-1])
            elif packet["packet_type"] == "eda":
                eda = packet["data"]["eda"]
                data["EDA"].extend(eda)
            elif packet["packet_type"] == "imu":
                imu = packet["data"]
                for k, v in imu.items():
                    print(k)
                    if "a" in k and data["IMU"][k]:
                        send_pd_message(k, data["IMU"][k][-1])
                    data["IMU"][k].extend(v)
                    
            elif packet["packet_type"] == "ppg":
                ppg = packet["data"]
                for k, v in ppg.items():
                    data["PPG"][k].extend(v)

            

            #if data["EMG"]:
            #    send_pd_message("emg", data["EMG"][-1])
            #    print("Data sent!")
            #    print(data["EMG"][-1])
            #    print()
            #else:
            #    print("No EMG data available.")
    except KeyboardInterrupt:
        print("Data streaming interrupted by user.")
    except Exception as e:
        print(f"An error occurred during data streaming: {e}")
    finally:
        # Stop data streaming and disconnect the bridge.
        bridge.stop()
        bridge.disconnect()
        print("Data streaming stopped and bridge disconnected.")

    # Save the collected data to a file.
    with open(output_file, 'wb') as f:
        pickle.dump(data, f)
    print(f"Data saved to {output_file}")

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
    EXECUTABLE_PATH = "C:/Users/thomaseo/Desktop/sifi/gitproject/sifi-project/BridgeScriptExamples/sifibridge.exe"
    # Initialize the SifiBridge with the path to the executable.
    bridge = sbp.SifiBridge(EXECUTABLE_PATH)
    # Call the stream_data function with the bridge instance.
    stream_data(bridge=bridge)