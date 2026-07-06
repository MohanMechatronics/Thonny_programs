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

# =========================
# BATTERY BOOT STABILIZATION
# =========================
led.value(1)
time.sleep(3)
led.value(0)
time.sleep(0.5)

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
# DOUBLE CLICK DETECTION
# =========================
def wait_for_double_click():
    if button.value() != 0:
        return False
    time.sleep(0.05)
    if button.value() != 0:
        return False

    print("1st press")
    stuck = 0
    while button.value() == 0:
        time.sleep(0.01)
        stuck += 1
        if stuck > 200:
            return False

    first_tick = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), first_tick) < 1500:
        if button.value() == 0:
            time.sleep(0.05)
            if button.value() == 0:
                print("2nd press!")
                while button.value() == 0:
                    time.sleep(0.01)
                return True
        time.sleep(0.02)

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
        print("Dial error:", e)
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
        print("SMS error:", e)

# =========================
# START
# =========================
initialize_device()
print("Ready - Double-click for SOS")
blink_led(2, 0.3)

# =========================
# MAIN LOOP (top level, no def)
# =========================
while True:
    if wait_for_double_click():
        print("SOS!")
        blink_led(3, 0.1)
        make_call(phone_number)
        time.sleep(5)
        send_sms()
        print("Done. Ready.\n")
        time.sleep(2)
    time.sleep(0.05)
