from machine import Pin, UART, PWM, time_pulse_us
import time
import network

# ==================================================
# PIN CONFIG
# ==================================================
# A9G GSM
A9G_PON   = 13
A9G_LOWP  = 12
SOS_BTN   = 25

# DFPLAYER
DF_TX = 19
DF_RX = 18

# SERVO
SERVO_PIN = 22

# ULTRASONIC
TRIG_PIN = 26
ECHO_PIN = 27

# ==================================================
# SETTINGS
# ==================================================
SOS_NUMBER = "+919080216609"
SOS_TIME   = 5       # seconds long press
OBSTACLE_DISTANCE = 70  # cm

# ==================================================
# WIFI OFF
# ==================================================
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

# ==================================================
# UART SETUP
# ==================================================
gsm = UART(1, 115200, tx=17, rx=16)
df  = UART(2, 9600, tx=DF_TX, rx=DF_RX)

# ==================================================
# GPIO
# ==================================================
pon  = Pin(A9G_PON, Pin.OUT)
lowp = Pin(A9G_LOWP, Pin.OUT)
sos  = Pin(SOS_BTN, Pin.IN, Pin.PULL_UP)

# ==================================================
# SERVO
# ==================================================
servo = PWM(Pin(SERVO_PIN), freq=50)

def set_angle(angle):
    duty = int(40 + (angle / 180) * 75)
    servo.duty(duty)
    time.sleep(0.5)

# ==================================================
# ULTRASONIC
# ==================================================
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

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

# ==================================================
# DFPLAYER FUNCTIONS
# ==================================================
def df_send(cmd, param=0):
    packet = bytearray([
        0x7E, 0xFF, 0x06, cmd, 0x00,
        (param >> 8) & 0xFF,
        param & 0xFF,
        0xEF
    ])
    df.write(packet)

def play(track):
    df_send(0x03, track)

def volume(vol=25):
    df_send(0x06, vol)

# ==================================================
# GSM AT COMMAND
# ==================================================
def send_at(cmd, wait=1):
    if isinstance(cmd, str):
        cmd = cmd.encode()

    gsm.write(cmd + b"\r\n")
    time.sleep(wait)

    resp = b""
    while gsm.any():
        resp += gsm.read()

    if resp:
        text = resp.decode("utf-8", "ignore")
        print(text)
        return text
    return ""

# ==================================================
# A9G INIT
# ==================================================
def a9g_init():
    print("Powering A9G...")
    lowp.value(0)
    pon.value(1)
    time.sleep(1)
    pon.value(0)

    time.sleep(10)

    while True:
        if "OK" in send_at("AT", 1):
            break
        print("Waiting for A9G...")
        time.sleep(2)

    send_at("ATE0", 1)
    print("A9G READY")

def call_sos():
    print("Calling SOS...")
    send_at("ATD" + SOS_NUMBER + ";", 1)

# ==================================================
# BOOT
# ==================================================
print("System Booting...")
a9g_init()
volume(25)
set_angle(90)

print("System Ready")

# ==================================================
# MAIN LOOP
# ==================================================
sos_pressed_time = None

while True:

    # ---------------- SOS BUTTON ----------------
    if sos.value() == 0:
        if sos_pressed_time is None:
            sos_pressed_time = time.time()

        elif time.time() - sos_pressed_time >= SOS_TIME:
            print("SOS TRIGGERED")
            play(6)  # optional alert sound
            call_sos()

            while sos.value() == 0:
                time.sleep(0.1)
            sos_pressed_time = None

    else:
        sos_pressed_time = None

    # ---------------- OBSTACLE SCAN ----------------
    set_angle(90)
    front = distance_cm()
    print("Front:", front)

    if front < OBSTACLE_DISTANCE:
        print("STOP")
        play(6)
        time.sleep(1.5)

        set_angle(0)
        left = distance_cm()
        print("Left:", left)

        set_angle(180)
        right = distance_cm()
        print("Right:", right)

        if left > right:
            print("RIGHT")
            play(4)
        else:
            print("LEFT")
            play(5)

        time.sleep(3)

    time.sleep(0.2)
