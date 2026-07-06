from machine import Pin, PWM, UART, time_pulse_us
import time

# ---------------- DFPLAYER ----------------
df = UART(2, baudrate=9600, tx=19, rx=18)

def df_send(cmd, param=0):
    
    packet = bytearray([
        0x7E, 0xFF, 0x06, cmd, 0x00,
        (param >> 8) & 0xFF,
        param & 0xFF,
        0xEF
    ])
    df.write(packet)

def play(num):
    df_send(0x03, num)

def volume(vol=25):
    df_send(0x06, vol)

# ---------------- SERVO ----------------
servo = PWM(Pin(22), freq=50)

def set_angle(angle):
    duty = int(40 + (angle / 180) * 75)   # ~0.5ms–2.5ms
    servo.duty(duty)
    time.sleep(0.6)

# ---------------- ULTRASONIC ----------------
trig = Pin(26, Pin.OUT)
echo = Pin(27, Pin.IN)

def distance_cm():
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

    duration = time_pulse_us(echo, 1, 30000)
    if duration < 0:
        return 999
    return duration / 58

# ---------------- MAIN ----------------
time.sleep(1)
volume(25)

print("System Ready")

while True:
    # Face front
    set_angle(90)
    front_dist = distance_cm()
    print("Front:", front_dist)

    if front_dist < 70:   # object detected
        print("STOP")
        play(6)           # STOP
        time.sleep(2)

        # Check LEFT
        set_angle(0)
        left_dist = distance_cm()
        print("Left:", left_dist)
        time.sleep(0.5)

        # Check RIGHT
        set_angle(180)
        right_dist = distance_cm()
        print("Right:", right_dist)
        time.sleep(0.5)
        

        # Decide direction
        if left_dist > right_dist:
            print("RIGHT")
            play(4)
        else:
            print("LEFT")
            play(5)

        time.sleep(3)     # avoid repeated triggers

    time.sleep(0.3)


