from gpiozero import Button

button = Button(23)
print("code started !!")
while True:
    if (button.when_pressed):
        print("Button was pressed")
