import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import pygame
import asyncio
import logging
from bluezero import async_tools
from bluezero import adapter
from bluezero import peripheral

# OLED display setup
i2c = busio.I2C(board.SCL, board.SDA)
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display
disp.fill(0)
disp.show()

# Create blank image for drawing
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image
draw = ImageDraw.Draw(image)

# Load default font
font = ImageFont.load_default()

# Push buttons setup
button1 = digitalio.DigitalInOut(board.D22)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.DOWN

button2 = digitalio.DigitalInOut(board.D23)
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.DOWN

button3 = digitalio.DigitalInOut(board.D24)
button3.direction = digitalio.Direction.INPUT
button3.pull = digitalio.Pull.DOWN

button4 = digitalio.DigitalInOut(board.D25)
button4.direction = digitalio.Direction.INPUT
button4.pull = digitalio.Pull.DOWN

button5 = digitalio.DigitalInOut(board.D26)
button5.direction = digitalio.Direction.INPUT
button5.pull = digitalio.Pull.DOWN

# Initialize Pygame for audio playback
pygame.mixer.init()

# Menu options
menu_items = ["Send Message", "Read Message", "Record Message", "Play Message", "Stop"]
current_item = 0

def display_text(text):
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), text, font=font, fill=255)
    disp.image(image)
    disp.show()

def display_menu():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    for i, item in enumerate(menu_items):
        if i == current_item:
            draw.rectangle((0, i*12, width, (i+1)*12), outline=1, fill=1)
            draw.text((0, i*12), item, font=font, fill=0)
        else:
            draw.text((0, i*12), item, font=font, fill=255)
    disp.image(image)
    disp.show()

display_menu()

# Constants for custom service and characteristic
CUSTOM_SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CUSTOM_CHARACTERISTIC_UUID = '12345678-1234-5678-1234-56789abcdef1'

class BLEPeripheral:
    def __init__(self):
        self.adapter_address = list(adapter.Adapter.available())[0].address
        self.ble_device = peripheral.Peripheral(self.adapter_address, local_name='RaspberryPiBLE')

        # Add custom service
        self.ble_device.add_service(srv_id=1, uuid=CUSTOM_SERVICE_UUID, primary=True)

        # Add custom characteristic
        self.ble_device.add_characteristic(
            srv_id=1,
            chr_id=1,
            uuid=CUSTOM_CHARACTERISTIC_UUID,
            value=[],
            notifying=False,
            flags=['read', 'write']
        )

    def start_advertising(self):
        self.ble_device.publish()
        print("Advertising...")

    def stop_advertising(self):
        self.ble_device.stop_advertise()
        print("Stopped advertising")

ble_peripheral = BLEPeripheral()

# Main loop
async def main():
    ble_peripheral.start_advertising()
    try:
        while True:
            global current_item
            if button1.value:  # Up button
                current_item = (current_item - 1) % len(menu_items)
                display_menu()
                time.sleep(0.2)  # Debounce delay
            if button2.value:  # Down button
                current_item = (current_item + 1) % len(menu_items)
                display_menu()
                time.sleep(0.2)  # Debounce delay
            if button3.value:  # Select button
                selected_option = menu_items[current_item]
                if selected_option == "Send Message":
                    display_text("Sending...")
                    # Add code to send a message via BLE
                elif selected_option == "Read Message":
                    display_text("Reading...")
                    # Add code to read a message via BLE
                elif selected_option == "Record Message":
                    display_text("Recording...")
                    # Add code to record a message
                elif selected_option == "Play Message":
                    display_text("Playing...")
                    # Add code to play a recorded message
                elif selected_option == "Stop":
                    display_text("Stopped")
                    ble_peripheral.stop_advertising()
                time.sleep(1)
                display_menu()
            if button4.value:  # Additional button (optional)
                # Define functionality if needed
                time.sleep(0.2)  # Debounce delay
            if button5.value:  # Additional button (optional)
                # Define functionality if needed
                time.sleep(0.2)  # Debounce delay
    except KeyboardInterrupt:
        display_text("Stopping...")
        ble_peripheral.stop_advertising()

asyncio.run(main())

