import Subu
from machine import Pin, PWM, time_pulse_us
import time

# Pin configuration
TRIG_PIN = Subu.IO3
ECHO_PIN = Subu.IO4
SERVO_PIN = Subu.IO1  # Define your servo pin

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
            return 999
        distance = (duration / 2) / 29.1
        return distance

def set_servo_angle(angle):
    duty = int((angle / 180) * 102 + 26)  # for 0.5ms to 2.5ms pulse
    servo.duty(duty)

# === Main Toll Gate Logic ===
def main():
    global servo
    ultrasonic = Ultrasonic(TRIG_PIN, ECHO_PIN)
    servo = PWM(Pin(SERVO_PIN), freq=50)
    set_servo_angle(0)
    print("Toll gate system ready...")

    while True:
        dist = ultrasonic.read_distance()
        print(f"Distance: {dist:.1f} cm")

        if dist < 10:
            print("Vehicle detected! Opening gate...")
            set_servo_angle(90)
            time.sleep(5)
            print("Closing gate...")
            set_servo_angle(0)

        time.sleep(0.5)

try:
    main()
except Exception as e:
    print("Error:", e)
