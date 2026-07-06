from machine import Pin, UART
import time
import network

# ================= PIN CONFIG =================
A9G_PON   = 13
A9G_LOWP  = 12
SOS_BTN   = 25

# ================= SETTINGS =================
SOS_NUMBER = "+917358289559"
SOS_TIME   = 5   # seconds (long press)

# ================= UART =================
gsm = UART(1, 115200, tx=17, rx=16)

# ================= GPIO =================
pon  = Pin(A9G_PON, Pin.OUT)
lowp = Pin(A9G_LOWP, Pin.OUT)
sos  = Pin(SOS_BTN, Pin.IN, Pin.PULL_UP)

# ================= WIFI OFF =================
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

# ================= AT COMMAND FUNCTION =================
def send_at(cmd, wait=1):
    if isinstance(cmd, str):
        cmd = cmd.encode()

    gsm.write(cmd + b"\r\n")
    time.sleep(wait)

    resp = b""
    while gsm.any():
        resp += gsm.read()

    if resp:
        try:
            text = resp.decode("utf-8", "ignore")
        except:
            text = ""
        print(text)
        return text

    return ""

# ================= A9G INIT =================
def a9g_init():
    print("Powering A9G...")

    lowp.value(0)
    pon.value(1)
    time.sleep(1)
    pon.value(0)

    time.sleep(10)   # boot time

    while True:
        if "OK" in send_at(b"AT", 1):
            break
        print("Waiting for A9G...")
        time.sleep(2)

    send_at(b"ATE0", 1)
    print("A9G READY")

# ================= CALL FUNCTION =================
def call_sos():
    print("Calling SOS number...")
    send_at(b"ATD" + SOS_NUMBER.encode() + b";", 1)

# ================= MAIN =================
print("System Booting...")
a9g_init()

while True:
    if sos.value() == 0:
        print("SOS button pressed")

        for i in range(SOS_TIME, 0, -1):
            print("Calling in", i)
            time.sleep(1)
            if sos.value() == 1:
                print("SOS cancelled")
                break
        else:
            print("SOS TRIGGERED")
            call_sos()

            # wait until button released (avoid repeat)
            while sos.value() == 0:
                time.sleep(0.1)

    time.sleep(0.1)
