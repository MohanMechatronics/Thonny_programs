import time
import random
from machine import Pin, time_pulse_us, PWM
from Wheels import Wheels
import Subu

# --- Pin Setup ---
TRIG_PIN = 38
ECHO_PIN = 13
SERVO_PIN = Subu.IO2

# --- Ultrasonic Sensor Class ---
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

        duration = time_pulse_us(self.echo, 1, 30000)
        if duration < 0:
            return 999  # timeout
        distance = (duration / 2) / 29.1  # cm
        return distance

# --- Servo Class ---
class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)

    def write_angle(self, angle):
        duty = int((angle / 180) * 8000 + 1000)
        self.pwm.duty_u16(duty)

    def detach(self):
        self.pwm.deinit()

# --- Movement Functions ---
def move_forward(wheels):
    wheels.drive_motors(1000, 0, 1000, 0)

def move_backward(wheels):
    wheels.drive_motors(0, 1000, 0, 1000)

def turn_left(wheels):
    wheels.drive_motors(1000, 0, 0, 1000)

def turn_right(wheels):
    wheels.drive_motors(0, 1000, 1000, 0)

def stop_wheels(wheels):
    wheels.drive_motors(0, 0, 0, 0)

# --- Main Logic ---
def main():
    wheels = Wheels("LMESMP")
    wheels.start_motors()
    sonar = Ultrasonic(TRIG_PIN, ECHO_PIN)
    servo = Servo(SERVO_PIN)

    print("Starting robot with intelligent obstacle sensing...")

    while True:
        distance = sonar.read_distance()
        print(f"Distance: {distance:.2f} cm")

        if distance < 25:
            print("Obstacle detected! Stopping...")
            stop_wheels(wheels)
            time.sleep(0.5)

            print("Reversing...")
            move_backward(wheels)
            time.sleep(1.2)
            stop_wheels(wheels)
            time.sleep(0.5)

            # Scan Left
            print("Scanning left...")
            servo.write_angle(150)
            time.sleep(0.7)
            left_distance = sonar.read_distance()
            print(f"Left distance: {left_distance:.2f} cm")

            # Scan Right
            print("Scanning right...")
            servo.write_angle(30)
            time.sleep(0.7)
            right_distance = sonar.read_distance()
            print(f"Right distance: {right_distance:.2f} cm")

            # Reset servo to center
            servo.write_angle(90)
            time.sleep(0.3)

            # Decide direction
            if right_distance > left_distance:
                print("Turning right...")
                turn_right(wheels)
            else:
                print("Turning left...")
                turn_left(wheels)

            time.sleep(1.2)
            stop_wheels(wheels)
            time.sleep(0.4)

            print("Moving forward again...")

        move_forward(wheels)
        time.sleep(0.1)

try:
    main()
except Exception as e:
    print("Error:", e)

