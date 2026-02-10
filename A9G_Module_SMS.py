from machine import Pin, UART
import time
import network

# ==================================================
# PIN CONFIG
# ==================================================
A9G_PON  = 13
A9G_LOWP = 12
TX_PIN  = 17

RX_PIN  = 16

# ==================================================
# SETTINGS
# ==================================================
PHONE_NUMBER = "+917358289559"
SMS_TEXT = "Hello! SMS sent successfully from ESP32 + A9G"

# ==================================================
# WIFI OFF
# ==================================================
wlan = network.WLAN(network.STA_IF)
wlan.active(False)

# ==================================================
# UART
# ==================================================
gsm = UART(1, baudrate=115200, tx=TX_PIN, rx=RX_PIN, timeout=1000)

# ==================================================
# GPIO
# ==================================================
pon  = Pin(A9G_PON, Pin.OUT)
lowp = Pin(A9G_LOWP, Pin.OUT)

# ==================================================
# SAFE AT COMMAND FUNCTION (NO UNICODE ERROR)
# ==================================================
def send_at(cmd, wait=2):
    try:
        if isinstance(cmd, str):
            cmd_bytes = cmd.encode()
        else:
            cmd_bytes = cmd

        gsm.write(cmd_bytes + b"\r\n")
    except Exception as e:
        print("UART write error:", e)
        return ""

    time.sleep(wait)

    resp = b""
    while gsm.any():
        try:
            resp += gsm.read()
        except:
            pass

    try:
        text = resp.decode("utf-8", "ignore")
    except:
        text = ""

    if text:
        print(text)

    return text

# ==================================================
# A9G POWER ON SEQUENCE
# ==================================================
def power_on_a9g():
    print("Powering ON A9G...")

    lowp.value(1)
    pon.value(1)
    time.sleep(1)
    pon.value(0)

    print("Waiting for GSM network...")
    time.sleep(30)

    lowp.value(0)

    while True:
        if "OK" in send_at("AT", 1):
            break
        print("Waiting for A9G response...")
        time.sleep(2)

    send_at("ATE0", 1)
    send_at("AT+CMGF=1", 1)
    send_at("AT+CSMP=17,167,0,0", 1)

    print("A9G READY")

# ==================================================
# SEND SMS FUNCTION
# ==================================================
def send_sms(number, message):
    print("Sending SMS...")

    send_at("AT+CMGF=1", 1)
    resp = send_at('AT+CMGS="{}"'.format(number), 2)

    if ">" not in resp:
        print("SMS prompt not received")
        return False

    gsm.write(message.encode())
    time.sleep(1)
    gsm.write(b"\x1A")   # CTRL + Z
    time.sleep(6)

    print("SMS SENT SUCCESSFULLY")
    return True

# ==================================================
# MAIN

# ==================================================
print("System Booting...")
power_on_a9g()
send_sms(PHONE_NUMBER, SMS_TEXT)

print("Program finished")

while True:
    time.sleep(1)
