import time
import random
from machine import Pin, time_pulse_us
from Wheels import Wheels
import Subu

# Pin configuration for ultrasonic sensor
TRIG_PIN = Subu.IO3
ECHO_PIN = Subu.IO4

class Ultrasonic:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.value(0)

    def read_distance(self):
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

        duration = time_pulse_us(self.echo, 1, 3
                                 0000)
        if duration < 0:
            return 999  # timeout or error
        distance = (duration / 2) / 29.1  # cm
        return distance


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



def main():
    wheels = Wheels("LMES2")
    wheels.start_motors()
    sonar = Ultrasonic(TRIG_PIN, ECHO_PIN)

    print("Starting robot obstacle sensing...")

    while True:
        distance = sonar.read_distance()
        print(f"Distance: {distance:.2f} cm")

        if distance < 25:
            print("Obstacle detected! Stopping...")
            stop_wheels(wheels)
            time.sleep(1.0)

            print("Reversing...")
            move_backward(wheels)
            time.sleep(2.0)
            stop_wheels(wheels)
            time.sleep(0.5)

            # Randomly choose left or right
            if random.choice(["left", "right"]) == "left":
                print("Turning left...")
                turn_left(wheels)
            else:
                print("Turning right...")
                turn_right(wheels)

            time.sleep(1.5)
            stop_wheels(wheels)
            time.sleep(0.5)

            print("Moving forward again...")

        move_forward(wheels)
        time.sleep(0.1)


try:
    main()
except Exception as e:
    print("Error:", e)
