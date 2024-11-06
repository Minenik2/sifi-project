import time
import math
import sifi_bridge_py as sbp
from pynput.keyboard import Key, Controller

# Initialize the keyboard controller
keyboard = Controller()

def quaternion_to_euler(qw, qx, qy, qz):
    # Convert quaternion to Euler angles
    roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    sinp = 2 * (qw * qy - qz * qx)
    pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)
    yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
    return pitch, roll, yaw

def control_keys(pitch, yaw, pressed_keys):
    """
    Controls WASD keys based on pitch and yaw values.
    - Pitch > 0 holds 'W', Pitch < 0 holds 'S'.
    - Yaw > 0 holds 'D', Yaw < 0 holds 'A'.
    """
    # Define which keys to press based on pitch and yaw
    if pitch > 0 and 'w' not in pressed_keys:
        keyboard.press('w')
        pressed_keys.add('w')
    elif pitch <= 0 and 'w' in pressed_keys:
        keyboard.release('w')
        pressed_keys.remove('w')

    if pitch < 0 and 's' not in pressed_keys:
        keyboard.press('s')
        pressed_keys.add('s')
    elif pitch >= 0 and 's' in pressed_keys:
        keyboard.release('s')
        pressed_keys.remove('s')

    if yaw > 0 and 'd' not in pressed_keys:
        keyboard.press('d')
        pressed_keys.add('d')
    elif yaw <= 0 and 'd' in pressed_keys:
        keyboard.release('d')
        pressed_keys.remove('d')

    if yaw < 0 and 'a' not in pressed_keys:
        keyboard.press('a')
        pressed_keys.add('a')
    elif yaw >= 0 and 'a' in pressed_keys:
        keyboard.release('a')
        pressed_keys.remove('a')

def stream_data(bridge, number_of_seconds_to_stream=1200, device_type=sbp.DeviceType.BIOPOINT_V1_3):
    devices = bridge.list_devices(sbp.ListSources.BLE)
    print("Available devices:", devices)
    connected = False
    while not connected:
        try:
            connected = bridge.connect(device_type)
            if not connected:
                print("Failed to connect... retrying")
                time.sleep(1)
        except Exception as e:
            print(f"Exception while connecting: {e}")
            time.sleep(1)

    print("Connected to BioPoint device!")
    bridge.set_channels(imu=True)
    bridge.set_low_latency_mode(on=True)
    bridge.start()
    start_time = time.time()
    first_packet_ignored = False
    pressed_keys = set()

    print(f"Streaming IMU data for {number_of_seconds_to_stream} seconds...")
    try:
        while time.time() - start_time < number_of_seconds_to_stream:
            packet = bridge.get_data_with_key("data")
            if packet["packet_type"] == "imu":
                if not first_packet_ignored:
                    first_packet_ignored = True
                    continue

                imu = packet["data"]
                if all(param in imu and len(imu[param]) == 8 for param in ["qw", "qx", "qy", "qz"]):
                    for i in range(8):
                        qw, qx, qy, qz = imu["qw"][i], imu["qx"][i], imu["qy"][i], imu["qz"][i]
                        pitch, roll, yaw = quaternion_to_euler(qw, qx, qy, qz)
                        control_keys(pitch, yaw, pressed_keys)
                        print(f"Pitch: {pitch}, Yaw: {yaw} - Keys pressed: {pressed_keys}")

    except KeyboardInterrupt:
        print("Streaming interrupted by user.")
    except Exception as e:
        print(f"Error during streaming: {e}")
    finally:
        bridge.stop()
        bridge.disconnect()
        # Ensure all keys are released
        for key in list(pressed_keys):
            keyboard.release(key)
        print("Streaming stopped and bridge disconnected.")

if __name__ == '__main__':
    EXECUTABLE_PATH = "C:/Users/thomaseo/Desktop/sifi/gitproject/sifi-project/BridgeScriptExamples/sifibridge.exe"
    bridge = sbp.SifiBridge(EXECUTABLE_PATH)
    stream_data(bridge=bridge)
