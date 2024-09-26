import hid
import time

# You might need to adjust these values to match your device
VENDOR_ID = 0x0483  # STM32 default vendor ID
PRODUCT_ID = 0x5750  # Replace this with your actual product ID

def find_device():
    device_dict = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    return device_dict

def main():
    device_info = find_device()
    if not device_info:
        print(f"Device with VID:{VENDOR_ID:04x} and PID:{PRODUCT_ID:04x} not found")
        return

    try:
        h = hid.device()
        h.open(VENDOR_ID, PRODUCT_ID)
        
        print(f"Opened device: {h.get_manufacturer_string()} {h.get_product_string()}")
        
        while True:
            try:
                # Read the report
                data = h.read(67, timeout_ms=1000)  # Adjust size if needed
                if data:
                    report_id = data[0]
                    if report_id == 1:
                        print(f"Report 1: {data[1:67]}")  # 2 sets of pickup data
                    elif report_id == 2:
                        print(f"Report 2: {data[1:69]}")  # 3 sets of pickup data
                    else:
                        print(f"Unknown Report ID: {report_id}")
                time.sleep(0.1)  # Small delay to prevent tight looping
                # Read the report
                # data = h.get_input_report(1, 70)  # Adjust size if needed
                # print(f"Report: {data}")
                # time.sleep(1)  # Small delay to prevent tight looping
                # data = h.get_input_report(2, 70)  # Adjust size if needed
                # if data:
                #     report_id = data[0]
                #     if report_id == 1:
                #         print(f"Report 1: {data[1:68]}") # 2 sets of pickup data
                #     elif report_id == 2:
                #         print(f"Report 2: {data[1:70]}")  # 3 sets of pickup data
                #     else:
                #         print(f"Unknown Report ID: {report_id}")
            except IOError as e:
                print(f"IOError: {str(e)}")
                time.sleep(1)  # Wait a bit before retrying
    except IOError as e:
        print(f"Unable to open device: {str(e)}")
    finally:
        h.close()

if __name__ == "__main__":
    main()