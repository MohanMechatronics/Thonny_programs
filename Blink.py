from machine import Pin
from time import sleep

led = Pin(27, Pin.OUT)  # Onboard LED is usually on GPIO 2

while True:
    led.on()      # Turn LED on
    sleep(1)      # Wait 1 second
    led.off()     # Turn LED off
    sleep(1)

    
# from machine import Pin, PWM
# from time import sleep
# 
# led = PWM(Pin(3), freq=1000) # GPIO 2 (usually onboard LED), 1 kHz frequency
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
