from machine import Pin, ADC, PWM, TouchPad
from time import ticks_ms, ticks_diff, sleep
from random import choice
import sys

# -------------------------------
# BOOT BUTTON TO STOP PROGRAM
# -------------------------------
boot_btn = Pin(0, Pin.IN, Pin.PULL_UP)
def boot_stop():
    if boot_btn.value() == 0:
        raise KeyboardInterrupt

# -------------------------------
# MOTOR DRIVER
# -------------------------------
lf = Pin(18, Pin.OUT)
lb = Pin(19, Pin.OUT)
rf = Pin(22, Pin.OUT)
rb = Pin(23, Pin.OUT)

def motor(a,b,c,d):
    lf.value(a)
    lb.value(b)
    rf.value(c)
    rb.value(d)

def forward():   motor(1,0,1,0)
def backward():  motor(0,1,0,1)
def left():      motor(0,0,1,0)
def right():     motor(1,0,0,0)
def drift_left():  motor(0,1,1,0)
def drift_right(): motor(1,0,0,1)
def stop():      motor(0,0,0,0)

# -------------------------------
# LED / BUZZER
# -------------------------------
led_b = Pin(17, Pin.OUT)
led_r = Pin(32, Pin.OUT)
led_l = Pin(33, Pin.OUT)
buzzer = Pin(26, Pin.OUT)

pwm_r = PWM(led_r)
pwm_l = PWM(led_l)
for p in (pwm_r, pwm_l):
    p.freq(1000)

pwm_status = PWM(led_b)
pwm_status.freq(1000)
pwm_status_value = 0
pwm_status_dir = 1

# -------------------------------
# SENSORS
# -------------------------------
adc_left  = ADC(Pin(35))
adc_mid   = ADC(Pin(39))
adc_right = ADC(Pin(36))

touch_l = TouchPad(Pin(4))
touch_r = TouchPad(Pin(27))

dig_left  = Pin(35, Pin.IN)
dig_mid   = Pin(39, Pin.IN)
dig_right = Pin(36, Pin.IN)

# -------------------------------
# SWITCHES
# -------------------------------
switch_pins = [
    Pin(13, Pin.IN, Pin.PULL_DOWN),
    Pin(14, Pin.IN, Pin.PULL_DOWN),
    Pin(15, Pin.IN, Pin.PULL_DOWN),
    Pin(16, Pin.IN, Pin.PULL_DOWN)
]

def read_switches():
    return tuple(sw.value() for sw in switch_pins)

# -------------------------------
# MODE TABLE PRINT
# -------------------------------
def print_table():
    table = [
        ["ROBOT______",     "S1 S2 S3 S4", "__"],
        ["TESTING______",   "1 0 0 0",     "______"],
        ["RANDOM____",      "0 1 0 0",     "______"],
        ["CLAPGO______",    "0 0 1 0",     "1 1 0 0"],
        ["FIRE BACK_____",  "0 0 0 1",     "1 0 1 0"],
        ["OBSTACLE____",    "0 1 1 0",     "1 0 0 1"],
        ["LINE FOLLOW_",    "0 1 0 1",     "1 1 1 0"],
        ["LIGHT FOLLOW",    "0 0 1 1",     "1 1 0 1"],
        ["TOUCH_______",    "1 0 1 1",     "______"]
    ]
    print("\nMODE TABLE")
    print("-"*40)
    for row in table:
        print('| {:^14} | {:^13} | {:^6} |'.format(*row))
    print("-"*40)

# -------------------------------
# TIMER TASK
# -------------------------------
class TimerTask:
    def __init__(self, interval, func):
        self.interval = interval
        self.func = func
        self.last = ticks_ms()
    def run(self):
        now = ticks_ms()
        if ticks_diff(now, self.last) >= self.interval:
            self.last = now
            self.func()

# -------------------------------
# RANDOM ROBOT STATE
# -------------------------------
current_random_move = None
random_move_start = 0

def random_robot():
    global current_random_move, random_move_start
    now = ticks_ms()
    if current_random_move is None or ticks_diff(now, random_move_start) >= 2000:
        current_random_move = choice([forward, backward, left, right, drift_left, drift_right, stop])
        random_move_start = now
    current_random_move()

# -------------------------------
# CLAPGO ROBOT
# -------------------------------
clap_state = 0
last_mid = 0

def clap_robot():
    global clap_state, last_mid
    mid = dig_mid.value()
    if mid == 1 and last_mid == 0:
        clap_state ^= 1
    last_mid = mid
    if clap_state:
        forward()
    else:
        stop()

# -------------------------------
# FIREBACK ROBOT
# -------------------------------
def fire_back_robot():
    if adc_mid.read() < 700:
        backward()
        buzzer.on()
    else:
        stop()
        buzzer.off()

# -------------------------------
# OBSTACLE AVOIDANCE
# -------------------------------
def obstacle_robot():
    if adc_mid.read() > 700:
        forward()
        return
    stop()
    buzzer.on()
    buzzer.off()
    turn = choice(["left", "right"])
    if turn == "left":
        drift_left()
    else:
        drift_right()
    sleep(0.4)

# -------------------------------
# LINE FOLLOWER
# -------------------------------
def line_robot():
    L = dig_left.value()
    R = dig_right.value()
    if L==0 and R==1: drift_right()
    elif L==1 and R==0: drift_left()
    elif L==1 and R==1: forward()
    else: stop()

# -------------------------------
# LIGHT FOLLOWER
# -------------------------------
def light_robot():
    L = dig_left.value()
    R = dig_right.value()
    if L==0 and R==0: forward()
    elif L==0 and R==1: left()
    elif L==1 and R==0: right()
    else: stop()

# -------------------------------
# TOUCH ROBOT
# -------------------------------
base_l = touch_l.read()
base_r = touch_r.read()

def touch_robot():
    l = touch_l.read()
    r = touch_r.read()
    if base_l - l > 50 and base_r - r > 50:
        forward()
    elif base_l - l > 50:
        left()
    elif base_r - r > 50:
        right()
    else:
        backward()

# -------------------------------
# SWITCH COMBINATIONS TO MODES
# -------------------------------
switch_map = {
    (1,0,0,0): forward,           # Testing
    (0,1,0,0): random_robot,      # Random
    (0,0,1,0): clap_robot,        # ClapGo
    (1,1,0,0): clap_robot,        # ClapGo alt
    (0,0,0,1): fire_back_robot,   # FireBack
    (1,0,1,0): fire_back_robot,   # FireBack alt
    (0,1,1,0): obstacle_robot,    # Obstacle
    (1,0,0,1): obstacle_robot,    # Obstacle alt
    (0,1,0,1): line_robot,        # Line follow
    (1,1,1,0): line_robot,        # Line follow alt
    (0,0,1,1): light_robot,       # Light follow
    (1,1,0,1): light_robot,       # Light follow alt
    (1,0,1,1): touch_robot        # Touch
}

# -------------------------------
# MODE CONTROL
# -------------------------------
current_mode = None
last_mode_name = None

mode_names = {

    forward: "TESTING",
    random_robot: "RANDOM",
    clap_robot: "CLAPGO",
    fire_back_robot: "FIRE BACK",
    obstacle_robot: "OBSTACLE",
    line_robot: "LINE FOLLOW",
    light_robot: "LIGHT FOLLOW",
    touch_robot: "TOUCH"
}

def update_mode():
    global current_mode, last_mode_name
    sw = read_switches()
    if sw == (0,0,0,0):
        current_mode = None
        mode_name = "IDLE"
    else:
        current_mode = switch_map.get(sw, stop)
        mode_name = mode_names.get(current_mode, "UNKNOWN")

    if mode_name != last_mode_name:
        print("MODE:", mode_name, "| SWITCH:", sw)
        last_mode_name = mode_name

# -------------------------------
# RUN ROBOT
# -------------------------------
def run_robot():
    if current_mode:
        pwm_status.duty_u16(0)
        current_mode()
    else:
        stop()
        breathe_status_led()

# -------------------------------
# STATUS LED BREATHING
# -------------------------------
def breathe_status_led():
    global pwm_status_value, pwm_status_dir
    step = 1000
    pwm_status_value += pwm_status_dir * step
    if pwm_status_value >= 65535:
        pwm_status_value = 65535
        pwm_status_dir = -1
    elif pwm_status_value <= 0:
        pwm_status_value = 0
        pwm_status_dir = 1
    pwm_status.duty_u16(pwm_status_value)

# -------------------------------
# TASK LOOP
# -------------------------------

tasks = [
    TimerTask(50, update_mode),
    TimerTask(30, run_robot)
]
print_table()
stop()

try:
    while True:
        boot_stop()
        for t in tasks:
            t.run()
        sleep(0.001)
except KeyboardInterrupt:
    print("\nPROGRAM STOPPED")
    stop()
    buzzer.off()
    led_r.off()
    led_l.off()
    led_b.off()
    sys.exit()
except Exception as e:
    print("Error:", e)
    stop()
    buzzer.off()
    led_r.off()
    led_l.off()
    led_b.off()
    sys.exit()
