from machine import Pin, PWM, time_pulse_us
import time

# ---------------- PIN SETUP ----------------
TRIG = Pin(26, Pin.OUT)
ECHO = Pin(27, Pin.IN)

servo = PWM(Pin(14), freq=50)  # 50Hz for servo

# ---------------- SERVO FUNCTION ----------------
def set_angle(angle):
    # Convert angle (0–180) to duty
    duty = int(40 + (angle / 180) * 75)
    servo.duty(duty)
    time.sleep(0.4)

# ---------------- ULTRASONIC FUNCTION ----------------
def get_distance():
    TRIG.off()
    time.sleep_us(2)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()

    try:
        duration = time_pulse_us(ECHO, 1, 30000)
        distance = (duration * 0.0343) / 2
        return distance
    except OSError:
        return 999  # no object detected

# ---------------- MAIN LOOP ----------------
while True:

    # FRONT
    set_angle(90)
    front = get_distance()
    print("Front Distance:", front, "cm")

    # LEFT
    set_angle(150)
    left = get_distance()
    print("Left Distance:", left, "cm")

    # RIGHT
    set_angle(30)
    right = get_distance()
    print("Right Distance:", right, "cm")

    print("--------------------------")

    # Decision logic
    if front < 20:   # object detected in front
        if left > right:
            print("➡️ TURN LEFT")
        else:
            print("⬅️ TURN RIGHT")
    else:
        print("⬆️ PATH CLEAR (FORWARD)")

    print("\n")
    time.sleep(1)