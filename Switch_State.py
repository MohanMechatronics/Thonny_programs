from machine import Pin
import time

# Button pin with internal pull-up
button = Pin(25, Pin.IN, Pin.PULL_UP)

print("Switch State Test Started")

while True:
    if button.value() == 0:   # Button pressed
        print("Button PRESSED")
    else:
        print("Button RELEASED")

    time.sleep(0.2)
