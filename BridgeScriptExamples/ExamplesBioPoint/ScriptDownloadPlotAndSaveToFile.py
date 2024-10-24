import time
import sifi_bridge_py as sbp

def download_data_through_USB_C(bridge):
    a=1
def download_data_through_BLE(bridge):
    print(bridge.list_devices(sbp.ListSources.BLE))  # List all BLE device to see the name and id of your BioPoint.

    # Modify this with the version of BioPoint you have if needed
    while not bridge.connect(sbp.DeviceType.BIOPOINT_V1_3):
        print("Failed to connect... retrying")

    print("Connected!")
    time.sleep(1)

    data_downloaded = bridge.start_memory_download()
    while True:
        packet = bridge.get_data_with_key("data")
        if packet["status"] == "MemoryDownloadCompleted":
            break


if __name__ == "__main__":
    EXECUTABLE_PATH = "./sifibridge"
    bridge = sbp.SifiBridge(EXECUTABLE_PATH)

    download_with_USB_C = False
    if download_with_USB_C:
        download_data_through_USB_C(bridge=bridge)
    else:
        download_data_through_BLE(bridge=bridge)