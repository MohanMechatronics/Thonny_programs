from machine import Pin, PWM
from time import sleep

# Use a PWM-capable pin (e.g., GPIO 13)
servo_pin = PWM(Pin(1), freq=50)

# Helper function to set angle (0° to 180°)
def set_servo_angle(angle):
    # Convert angle to duty cycle (approx 0.5ms to 2.5ms pulse width)
    duty = int((angle / 180 * 100) + 25)  # Range ~25 to ~125 for 0° to 180°
    servo_pin.duty(duty)

# Test sweep from 0° to 180° and back
while True:
    for angle in range(0, 181, 10):
        set_servo_angle(angle)
        sleep(0.3)
    for angle in range(180, -1, -10):
        set_servo_angle(angle)
        sleep(0.3)
        
# from machine import Pin, PWM
# from time import sleep
# 
# # Set up PWM on GPIO13 (adjust if needed), 50Hz for servo
# servo = PWM(Pin(21), freq=50)
# led = Pin(27, Pin.OUT)
# 
# # Function to set servo angle
# def set_angle(angle):
#     min_duty = 40   # for 0 degrees (~0.5 ms pulse)
#     max_duty = 115  # for 180 degrees (~2.5 ms pulse)
#     duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
#     servo.duty(duty)
# 
# # Run servo through 0 → 90 → 180 → 180 → 90 → 0
# while True:
#     led.on()
#     for angle in [0, 90, 180, 180, 90, 0]:
#         set_angle(angle)
#         sleep(1)
