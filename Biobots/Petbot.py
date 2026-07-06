"""
COBOT - MicroPython ESP32 Servo Controller
Servo layout:
                Back
  ----- --------     --------- -----
    27 |  B_LEFT |   | B_RIGHT | 12
       | SERVO 3 |   | SERVO 4 |
        --------     --------
       | F_LEFT  |  | F_RIGHT  |
    14 | SERVO 1 |  |  SERVO 2 | 13
  ----- --------    --------- -----
                Front

Pin assignments:
  GPIO 14 -> servo1 (Right leg / F_LEFT)
  GPIO 13 -> servo2 (Left leg  / F_RIGHT)
  GPIO 27 -> servo3 (Right arm / B_LEFT)
  GPIO 12 -> servo4 (Left arm  / B_RIGHT)
"""

from machine import Pin, PWM
import utime


# ---------------------------------------------------------------------------
# Servo helper
# ---------------------------------------------------------------------------
class Servo:
    """
    Simple servo wrapper for MicroPython / ESP32.
    Converts an angle (0-180) to a PWM duty cycle.

    Standard servo pulse range:
      0.5 ms (0°)  -> 1.0 ms (90°) -> 2.5 ms (180°)
    at 50 Hz the period is 20 ms, so duty is expressed as a fraction of 65535
    (16-bit resolution used by machine.PWM on ESP32).
    """

    FREQ      = 50          # 50 Hz standard servo frequency
    MIN_US    = 500         # pulse width in µs for 0°
    MAX_US    = 2500        # pulse width in µs for 180°
    PERIOD_US = 1_000_000 // FREQ   # = 20 000 µs

    def __init__(self, pin: int):
        self._pwm = PWM(Pin(pin), freq=self.FREQ)
        self._angle = None

    def write(self, angle: int):
        """Set servo to angle (0-180 degrees)."""
        angle = max(0, min(180, angle))
        if angle == self._angle:
            return
        self._angle = angle
        pulse_us = self.MIN_US + (self.MAX_US - self.MIN_US) * angle // 180
        duty = pulse_us * 65535 // self.PERIOD_US
        self._pwm.duty_u16(duty)

    def deinit(self):
        self._pwm.deinit()


# ---------------------------------------------------------------------------
# Servo instances
# ---------------------------------------------------------------------------
servo1 = Servo(2)   # Right leg
servo2 = Servo(4)   # Left leg
servo3 = Servo(3)   # Right arm
servo4 = Servo(5)   # Left arm

# ---------------------------------------------------------------------------
# Home angles
# ---------------------------------------------------------------------------
home1 = 120
home2 = 60
home3 = 60
home4 = 120
home  = 90


def delay(ms: int):
    utime.sleep_ms(ms)


# ---------------------------------------------------------------------------
# Pose helpers
# ---------------------------------------------------------------------------
def standhome():
    servo1.write(home1)
    servo2.write(home2)
    servo3.write(home3)
    servo4.write(home4)


def sithome():
    servo1.write(180)
    servo2.write(0)
    servo3.write(0)
    servo4.write(180)


# ---------------------------------------------------------------------------
# Movements
# ---------------------------------------------------------------------------
def walkForward(steps: int):
    for _ in range(steps):
        servo1.write(home1 + 20)
        servo4.write(home4 - 20)
        delay(100)
        servo1.write(home1 + 40)
        servo4.write(home4 - 40)
        servo2.write(home2 + 20)
        servo3.write(home3 - 20)
        delay(100)
        standhome()
        delay(100)
        servo2.write(home2 - 20)
        servo3.write(home3 + 20)
        delay(100)
        servo1.write(home1 - 20)
        servo4.write(home4 + 20)
        servo2.write(home2 - 40)
        servo3.write(home3 + 40)
        delay(100)
        standhome()


def walkBackward(steps: int):
    for _ in range(steps):
        servo1.write(home1 - 20)
        servo4.write(home4 + 20)
        delay(100)
        servo1.write(home1 - 40)
        servo4.write(home4 + 40)
        servo2.write(home2 - 20)
        servo3.write(home3 + 20)
        delay(100)
        standhome()
        delay(100)
        servo2.write(home2 + 20)
        servo3.write(home3 - 20)
        delay(100)
        servo1.write(home1 + 20)
        servo4.write(home4 - 20)
        servo2.write(home2 + 40)
        servo3.write(home3 - 40)
        delay(100)
        standhome()


def turnLeft(steps: int):
    for _ in range(steps):
        servo2.write(home + 20)
        servo3.write(home + 20)
        delay(100)
        servo1.write(home - 20)
        servo4.write(home - 20)
        servo2.write(home + 40)
        servo3.write(home + 40)
        delay(100)
        servo1.write(home - 20)
        servo4.write(home - 20)
        servo2.write(home + 20)
        servo3.write(home + 20)
        delay(100)
        standhome()
        delay(100)
        servo1.write(home + 20)
        servo4.write(home + 20)
        delay(100)
        servo1.write(home + 40)
        servo4.write(home + 40)
        servo2.write(home - 20)
        servo3.write(home - 20)
        delay(100)
        servo1.write(home + 20)
        servo4.write(home + 20)
        servo2.write(home - 20)
        servo3.write(home - 20)
        delay(100)
        standhome()


def turnRight(steps: int):
    for _ in range(steps):
        servo1.write(home - 20)
        servo4.write(home - 20)
        delay(100)
        servo1.write(home - 40)
        servo4.write(home - 40)
        servo2.write(home + 20)
        servo3.write(home + 20)
        delay(100)
        servo1.write(home - 20)
        servo4.write(home - 20)
        servo2.write(home + 20)
        servo3.write(home + 20)
        delay(100)
        standhome()
        delay(100)
        servo2.write(home - 20)
        servo3.write(home - 20)
        delay(100)
        servo1.write(home + 20)
        servo4.write(home + 20)
        servo2.write(home - 40)
        servo3.write(home - 40)
        delay(100)
        servo1.write(home + 20)
        servo4.write(home + 20)
        servo2.write(home - 20)
        servo3.write(home - 20)
        delay(100)
        standhome()


def wink(times: int):
    servo3.write(0)
    delay(200)
    for _ in range(times):
        servo2.write(home - 90)
        delay(200)
        servo2.write(home - 30)
        delay(200)
    standhome()


def handshake(times: int):
    servo4.write(180)
    delay(200)
    for _ in range(times):
        servo1.write(home + 90)
        delay(200)
        servo1.write(home + 30)
        delay(200)
    standhome()


def twist():
    for _ in range(2):
        servo1.write(home1 + 20)
        servo2.write(home2 - 20)
        delay(150)
        servo1.write(home1 - 20)
        servo2.write(home2 + 20)
        delay(150)
    standhome()


def shakeL(steps: int):
    for _ in range(steps):
        servo1.write(home1 + 40)
        servo2.write(home2 + 40)
        servo3.write(home3 + 40)
        servo4.write(home4 + 40)
        delay(100)
        standhome()
        delay(100)


def shakeR(steps: int):
    for _ in range(steps):
        servo1.write(home1 - 40)
        servo2.write(home2 - 40)
        servo3.write(home3 - 40)
        servo4.write(home4 - 40)
        delay(100)
        standhome()
        delay(100)


def downaction(step: int):
    for _ in range(step):
        sithome()
        delay(100)
        standhome()
        delay(100)


def RUN(steps: int):
    for _ in range(steps):
        servo1.write(home1 + 60)
        servo4.write(home4 - 60)
        servo2.write(home2 - 60)
        servo3.write(home3 + 60)
        standhome()
        delay(100)
        servo1.write(home1 - 60)
        servo4.write(home4 + 60)
        servo2.write(home2 + 60)
        servo3.write(home3 - 60)
        standhome()
        servo1.write(home1 + 60)
        servo4.write(home4 - 60)
        servo2.write(home2 - 60)
        servo3.write(home3 + 60)
        delay(100)
        standhome()


def RUNBACK(steps: int):
    for _ in range(steps):
        servo1.write(home1 - 60)
        servo4.write(home4 + 60)
        servo2.write(home2 + 60)
        servo3.write(home3 - 60)
        standhome()
        delay(100)
        servo1.write(home1 + 60)
        servo4.write(home4 - 60)
        servo2.write(home2 - 60)
        servo3.write(home3 + 60)
        standhome()
        servo1.write(home1 - 60)
        servo4.write(home4 + 60)
        servo2.write(home2 + 60)
        servo3.write(home3 - 60)
        delay(100)
        standhome()


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
print("COBOT DEMO START")
standhome()
delay(1000)

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
while True:
    standhome()
    delay(4000)

    sithome()
    delay(2000)
    
    walkForward(5)
    delay(2000)

    walkBackward(5)
    delay(2000)

    turnLeft(5)
    delay(2000)

    turnRight(5)
    delay(2000)

    wink(4)
    delay(2000)

    handshake(4)
    delay(2000)

    twist()
    delay(2000)

    shakeL(4)
    delay(2000)

    shakeR(4)
    delay(2000)

    sithome()
    delay(2000)

    standhome()
    delay(2000)