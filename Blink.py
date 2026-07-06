from machine import Pin
from time import sleep

led = Pin(25, Pin.OUT)

while True:
    led.value(1)   # ON
    print("ON")
    sleep(1)

    led.value(0)   # OFF
    print("OFF")
    sleep(1)
    
# from machine import Pin, PWM
# from time import sleep
# 
# led = PWM(Pin(2), freq=1000) # GPIO 2 (usually onboard LED), 1 kHz frequency
# 
# while True:
#     # Fade in
#     for duty in range(0, 1024, 10):  # PWM duty from 0 to 1023
#         led.duty(duty)
#         sleep(0.01)
#     
#     # Fade out
#     for duty in range(1023, -1, -10):
#         led.duty(duty)
#         sleep(0.01)
