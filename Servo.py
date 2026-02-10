from machine import Pin, PWM
from time import sleep

# Use a PWM-capable pin (e.g., GPIO 13)
servo_pin = PWM(Pin(26), freq=50)

# Helper function to set angle (0° to 180°)
def set_servo_angle(angle):
    # Convert angle to duty cycle (approx 0.5ms to 2.5ms pulse width)
    duty = int((angle / 180 * 100) + 25)  # Range ~25 to ~125 for 0° to 180°
    servo_pin.duty(duty)

# Test sweep from 0° to 180° and back
while True:
    for angle in range(0, 181, 10):[
        set_servo_angle(angle)
        sleep(0.3)
    for angle in range(180, -1, -10):
        set_servo_angle(angle)
        sleep(0.3)
