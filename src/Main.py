import usb.core
import usb.util
import time
import usb.core

# Find all connected devices
devices = usb.core.find(find_all=True)

# Print details for each device
mouse_VID = 0
mouse_PID = 0
name = "Razer DeathAdder Elite"

for device in devices:
    try:
        # Get device descriptors
        try:
            manufacturer = usb.util.get_string(device, device.iManufacturer)
            product = usb.util.get_string(device, device.iProduct)
            serial_number = usb.util.get_string(device, device.iSerialNumber)

            print(f"Device Found:")
            print(f"  Manufacturer: {manufacturer}")
            print(f"  Product: {product}")
            if product == name:
                mouse_PID = device.idProduct
                mouse_VID = device.idVendor
                break
            print(f"  Serial Number: {serial_number}")
            print(f"  VID:PID = {hex(device.idVendor)}:{hex(device.idProduct)}")
        except Exception as e: 
            print(f"Could not access device descriptors: {e}")
            print(f"  VID:PID = {hex(device.idVendor)}:{hex(device.idProduct)}")
    except usb.core.USBError as e:
        print(f"Could not access device descriptors: {e}")
        print(f"  VID:PID = {hex(device.idVendor)}:{hex(device.idProduct)}")

# place dll into windows system 32
# https://libusb.info/ 

# Replace with your device's VID and PIDs
# Find the USB device
device = usb.core.find(idVendor=mouse_VID, idProduct=mouse_PID)
if device is None:
    raise ValueError("Mouse not found. Check VID and PID.")

print(f"Mouse found: VID={hex(mouse_VID)}, PID={hex(mouse_PID)}")

backend = usb.backend.libusb1.get_backend()
if backend is None:
    print("No libusb backend found. Ensure libusb is installed and accessible.")
else:
    print("libusb backend is available.")

# Set the active configuration
device.set_configuration()

# Get the first endpoint (IN type)
cfg = device.get_active_configuration()
intf = cfg[(0, 0)]  # Interface 0, Alternate Setting 0
endpoint = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
)

if endpoint is None:
    raise ValueError("IN endpoint not found on the mouse.")

print("Found endpoint:", endpoint)#
print("Endpoint Address:", hex(endpoint.bEndpointAddress))
print("Max Packet Size:", endpoint.wMaxPacketSize)

print("Reading mouse data...")
try:
    while True:
        try:
            # Read data from the endpoint with a smaller timeout (e.g., 5000 ms or 5 seconds)
            data = endpoint.read(8, timeout=5000)  # 8 bytes, typical for mouse packets
            print("Raw Data:", list(data))  # Mouse sends binary data packets
        except usb.core.USBError as e:
            print(e)
            if e.errno == usb.core.USBError.TIMEOUT:
                print("USB Timeout Error. Retrying...")
                time.sleep(1)  # Retry after a small delay
            else:
                print(f"USB Error: {e}")
                break
except KeyboardInterrupt:
    print("Stopped by user.")