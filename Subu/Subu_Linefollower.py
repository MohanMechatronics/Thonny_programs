import Subu
from machine import Pin
import time
from Wheels import Wheels


# === IR Sensors ===
ir_left = Pin(Subu.IO2, Pin.IN)
ir_right = Pin(Subu.IO3, Pin.IN)

wheels = Wheels("LMES2")
wheels.start_motors()


def move_forward(wheels):
    wheels.drive_motors(512, 0, 512, 0)


def turn_left(wheels):
    wheels.drive_motors(512, 0, 0, 512)


def turn_right(wheels):
    wheels.drive_motors(0, 512, 512, 0)
    
def move_backward(wheels):
    wheels.drive_motors(0,512,0,512)

def stop_wheels(wheels):
    wheels.drive_motors(0,0,0,0)

# === Main Loop ===
def loop():
    print("Line follower starting (SUBU)...")
    while True:
        l = ir_left.value()
        r = ir_right.value()
        print(f"Left IR: {l}, Right IR: {r}")

        if l == 0 and r == 0:
            move_forward(wheels)
        elif l == 0 and r == 1:
            turn_left(wheels)
        elif l == 1 and r == 0:
            turn_right(wheels)
        else:
            stop_wheels(wheels)

        time.sleep(0.05)

try:
    loop()
except Exception as e:
    print("Error:", e)
    stop()
