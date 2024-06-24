# import time
# import board
# import digitalio

# # Push buttons setup
# button1 = digitalio.DigitalInOut(board.D22)
# button1.direction = digitalio.Direction.INPUT
# button1.pull = digitalio.Pull.DOWN

# button2 = digitalio.DigitalInOut(board.D23)
# button2.direction = digitalio.Direction.INPUT
# button2.pull = digitalio.Pull.DOWN

# button3 = digitalio.DigitalInOut(board.D24)
# button3.direction = digitalio.Direction.INPUT
# button3.pull = digitalio.Pull.DOWN

# button4 = digitalio.DigitalInOut(board.D25)
# button4.direction = digitalio.Direction.INPUT
# button4.pull = digitalio.Pull.DOWN

# button5 = digitalio.DigitalInOut(board.D26)
# button5.direction = digitalio.Direction.INPUT
# button5.pull = digitalio.Pull.DOWN

# print("Press any button to see the output. Press Ctrl+C to exit.")

# try:
#     while True:
#         if button1.value:
#             print("Button 1 (GPIO22) pressed")
#         if button2.value:
#             print("Button 2 (GPIO23) pressed")
#         if button3.value:
#             print("Button 3 (GPIO24) pressed")
#         if button4.value:
#             print("Button 4 (GPIO25) pressed")
#         if button5.value:
#             print("Button 5 (GPIO26) pressed")
#         time.sleep(0.1)  # Debounce delay
# except KeyboardInterrupt:
#     print("Exiting")

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
def button_callback(channel):
    print("Button was pushed!")
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(22,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up