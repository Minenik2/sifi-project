import time
import math
import sifi_bridge_py as sbp
from pythonosc import udp_client

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

def stream_data(bridge, number_of_seconds_to_stream=1200, device_type=sbp.DeviceType.BIOPOINT_V1_3):
    """
    Streams IMU data from a BioPoint device for a specified duration and sends it over UDP.

    Parameters:
    bridge (sbp.SifiBridge): The SifiBridge object to communicate with the BioPoint device.
    number_of_seconds_to_stream (int): Duration in seconds to stream data.
    device_type: The type of BioPoint device to connect to.
    """
    # Set up UDP client
    pd_client = udp_client.SimpleUDPClient("193.157.252.25", 31000)  # Adjust host and port accordingly

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

    # Enable only the IMU channel for recording data.
    bridge.set_channels(imu=True)
    bridge.set_low_latency_mode(on=True)

    # Start data streaming.
    bridge.start()
    start_time = time.time()
    first_packet_ignored = False
    print(f"Started streaming IMU data for {number_of_seconds_to_stream} seconds...")

    try:
        while time.time() - start_time < number_of_seconds_to_stream:
            # Retrieve data packet from the bridge.
            packet = bridge.get_data_with_key("data")
            # Process only the IMU packet.
            if packet["packet_type"] == "imu":
                # Ignore the first IMU packet.
                if not first_packet_ignored:
                    first_packet_ignored = True
                    print("First IMU packet ignored.")
                    continue  # Skip processing the first packet.

                imu = packet["data"]
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
                    pd_client.send_message("/biopoint/pitch", pitch_list)
                    pd_client.send_message("/biopoint/roll", roll_list)
                    pd_client.send_message("/biopoint/yaw", yaw_list)
                    
                    print(f"Sent pitch, roll, yaw lists via OSC: {pitch_list}, {roll_list}, {yaw_list}")  # Debug print

    except KeyboardInterrupt:
        print("Data streaming interrupted by user.")
    except Exception as e:
        print(f"An error occurred during data streaming: {e}")
    finally:
        # Stop data streaming and disconnect the bridge.
        bridge.stop()
        bridge.disconnect()
        print("Data streaming stopped and bridge disconnected.")

if __name__ == '__main__':
    EXECUTABLE_PATH = "C:/Users/thomaseo/Desktop/sifi/gitproject/sifi-project/BridgeScriptExamples/sifibridge.exe"
    # Initialize the SifiBridge with the path to the executable.
    bridge = sbp.SifiBridge(EXECUTABLE_PATH)
    # Call the stream_data function with the bridge instance.
    stream_data(bridge=bridge)
