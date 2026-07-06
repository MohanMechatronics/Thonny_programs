import cellular
import time
from machine import Pin

# =========================
# SETTINGS
# =========================
phone_number = "8883808878"
admin_number = "+918883808878"
message_to_send = "SOS ALERT! I need help! Location: https://maps.google.com/?q=12.95258N+80.172535E"

# =========================
# PINS
# =========================
led = Pin(27, Pin.OUT)
button = Pin(4, Pin.IN, Pin.PULL_UP)
buzzer = Pin(25, Pin.OUT)

# =========================
# BATTERY BOOT STABILIZATION
# =========================
led.value(1)
time.sleep(3)
led.value(0)
time.sleep(0.5)
buzzer.value(0)

# =========================
# LED BLINK
# =========================
def blink_led(times, interval=0.2):
    for _ in range(times):
        led.value(1)
        time.sleep(interval)
        led.value(0)
        time.sleep(interval)

# =========================
# INITIALIZATION
# =========================
def initialize_device():
    print("Initializing...")
    blink_led(3)
    sim_ok = False
    for i in range(10):
        if cellular.is_sim_present():
            sim_ok = True
            break
        print("Waiting for SIM...")
        time.sleep(1)
    if not sim_ok:
        print("SIM not found. Halting.")
        while True:
            blink_led(1, 1.0)
    print("SIM OK")
    net_ok = False
    for i in range(60):
        if cellular.is_network_registered():
            net_ok = True
            break
        print("Network connecting...")
        time.sleep(1)
    if not net_ok:
        print("Network failed. Halting.")
        while True:
            blink_led(2, 0.5)
            time.sleep(2)
    print("Network OK")

# =========================
# MULTI-CLICK DETECTION
# =========================
def count_clicks(max_wait_ms=1500, debounce_ms=50, max_clicks=4):
    if button.value() != 0:
        return 0

    time.sleep(debounce_ms / 1000)
    if button.value() != 0:
        return 0

    clicks = 1
    print("Click {}".format(clicks))

    stuck = 0
    while button.value() == 0:
        time.sleep(0.01)
        stuck += 1
        if stuck > 200:
            return 0

    window_start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), window_start) < max_wait_ms:
        if button.value() == 0:
            time.sleep(debounce_ms / 1000)
            if button.value() == 0:
                clicks += 1
                print("Click {}".format(clicks))

                if clicks >= max_clicks:
                    while button.value() == 0:
                        time.sleep(0.01)
                    return clicks

                while button.value() == 0:
                    time.sleep(0.01)

        time.sleep(0.02)

    return clicks

# =========================
# PRESS AND HOLD DETECTION
# =========================
def is_held(hold_ms=1500):
    if button.value() != 0:
        return False
    time.sleep(0.05)
    if button.value() != 0:
        return False

    hold_start = time.ticks_ms()
    while button.value() == 0:
        if time.ticks_diff(time.ticks_ms(), hold_start) >= hold_ms:
            print("Hold detected - turning off buzzer")
            while button.value() == 0:
                time.sleep(0.01)
            return True
        time.sleep(0.01)

    return False

# =========================
# CALL
# =========================
def make_call(number):
    print("Calling...")
    led.value(1)
    try:
        cellular.dial(number)
    except Exception as e:
        print("Dial error: {}".format(e))
        led.value(0)
        return
    time.sleep(20)
    try:
        cellular.hangup()
    except:
        pass
    led.value(0)
    print("Call done")

# =========================
# SMS
# =========================
def send_sms():
    print("Sending SMS...")
    try:
        cellular.SMS(admin_number, message_to_send).send()
        print("SMS sent")
    except Exception as e:
        print("SMS error: {}".format(e))

# =========================
# START
# =========================
initialize_device()
print("Ready - Double-click: SOS | 4 clicks: Buzzer ON | Hold to turn buzzer OFF")
blink_led(2, 0.3)

buzzer_active = False

# =========================
# MAIN LOOP
# =========================
while True:

    if buzzer_active:
        if is_held(hold_ms=1500):
            buzzer.value(0)
            buzzer_active = False
            print("Buzzer OFF")
            blink_led(2, 0.2)
        time.sleep(0.05)
        continue

    if button.value() == 0:
        clicks = count_clicks(max_wait_ms=1500, max_clicks=4)

        if clicks == 2:
            print("SOS!")
            blink_led(3, 0.1)
            make_call(phone_number)
            time.sleep(5)
            send_sms()
            print("Done. Ready.")
            time.sleep(2)

        elif clicks == 4:
            print("Buzzer ON! Hold button to turn off.")
            buzzer.value(1)
            buzzer_active = True
            blink_led(4, 0.1)

        elif clicks == 1:
            print("Single click - ignored")

        elif clicks == 3:
            print("3 clicks - ignored")

    time.sleep(0.05)