from machine import Pin, PWM
import time

# ==============================
# Servo Pin Setup
# ==============================
servo_pin = Pin(2)          # Change pin if needed
servo = PWM(servo_pin, freq=50)   # 50Hz for servo

# ==============================
# Function to set angle
# ==============================
def set_angle(angle):
    # Convert angle (0–180) to duty (for ESP32 0–1023 range)
    duty = int((angle / 180) * 77 + 26)  
    servo.duty(duty)

# ==============================
# Test Loop
# ==============================
while True:
    print("0 degree")
    set_angle(0)
    time.sleep(1)

    print("90 degree")
    set_angle(90)
    time.sleep(1)

    print("180 degree")
    set_angle(180)
    time.sleep(1)