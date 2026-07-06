from machine import UART, Pin
import time

# =========================
# UART SETUP
# =========================
gsm = UART(1, baudrate=115200, tx=17, rx=16)

# =========================
# PINS
# =========================
SOS = Pin(27, Pin.IN, Pin.PULL_UP)
LED = Pin(2, Pin.OUT)

# =========================
# SETTINGS
# =========================
SOS_NUMBER = "+917358289559"

CALL_DURATION = 30
RETRY_COUNT = 2

# =========================
# GLOBAL
# =========================
incoming_handled = False

# =========================
# FUNCTIONS
# =========================

def send_cmd(cmd, wait=0.5):
    print("➡️ CMD:", cmd)
    gsm.write(cmd + "\r\n")
    time.sleep(wait)

    resp = b""
    start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start) < (wait * 1000):
        if gsm.any():
            resp += gsm.read()

    try:
        decoded = resp.decode('utf-8', 'ignore')
        print("⬅️ RESP:", decoded)
        return decoded
    except:
        return ""


# =========================
# GET GPS LOCATION
# =========================
def get_location():
    print("📡 Getting GPS location...")

    for _ in range(2):
        resp = send_cmd("AT+LOCATION=2", 3)

        try:
            for line in resp.split("\n"):
                line = line.strip()

                if "," in line and line.count(",") == 1:
                    lat, lon = line.split(",")

                    lat = lat.strip()
                    lon = lon.strip()

                    if lat.replace(".", "", 1).isdigit() and lon.replace(".", "", 1).isdigit():
                        print("📍", lat, lon)
                        return lat, lon
        except:
            pass

        time.sleep(1)

    print("❌ GPS Not Available")
    return None, None


# =========================
# SEND SMS
# =========================
def send_sms(number, message):
    print("📩 Sending SMS to:", number)

    send_cmd("AT+CMGF=1", 1)

    gsm.write('AT+CMGS="{}"\r\n'.format(number))
    time.sleep(1)

    gsm.write(message + "\r\n")
    time.sleep(1)

    gsm.write(chr(26))
    time.sleep(3)

    print("✅ SMS Sent")


# =========================
# INCOMING CALL HANDLER (FIXED)
# =========================
def check_incoming_call():
    global incoming_handled

    if gsm.any():
        try:
            resp = gsm.read().decode('utf-8', 'ignore')
            print("📥 GSM:", resp)

            # 📲 Incoming call
            if "RING" in resp and not incoming_handled:

                print("📲 Incoming Call Detected")

                # ✅ PICK IMMEDIATELY
                send_cmd("ATA", 0.5)
                LED.value(1)

                incoming_handled = True

                # small delay for stability
                time.sleep(1)

                # 📍 Now get location
                lat, lon = get_location()

                if lat and lon:
                    link = "https://maps.google.com/?q={},{}".format(lat, lon)
                    msg = "📞 Incoming Call Alert!\n" + link
                else:
                    msg = "📞 Incoming Call Alert!\nLocation not available"

                send_sms(SOS_NUMBER, msg)

            # 📵 Call ended
            if "NO CARRIER" in resp:
                print("📴 Call Ended")
                LED.value(0)
                incoming_handled = False

        except:
            pass


# =========================
# CALL WITH RETRY
# =========================
def make_call(number, retries=2, duration=30):

    for attempt in range(retries + 1):

        print(f"📞 Calling {number} (Attempt {attempt+1})")
        send_cmd("ATD{};".format(number), 2)

        start = time.time()
        call_success = True

        while time.time() - start < duration:

            if gsm.any():
                try:
                    resp = gsm.read().decode('utf-8', 'ignore')
                    print("📥", resp)

                    if "NO CARRIER" in resp or "BUSY" in resp or "NO ANSWER" in resp:
                        print("❌ Call not answered")
                        call_success = False
                        break

                except:
                    pass

            time.sleep(0.5)

        send_cmd("ATH", 1)

        if call_success:
            print("✅ Call completed")
            return True

        print("🔁 Retrying...\n")

    print("❌ All attempts failed")
    return False


# =========================
# INITIAL SETUP
# =========================
print("🔄 Initializing A9G...")

send_cmd("AT")
send_cmd("AT+CLIP=1")
send_cmd("AT+COLP=1")   # improves call detection
send_cmd("AT+CLVL=5")
send_cmd("ATS0=0")      # manual answering
send_cmd("AT+GPS=1")

LED.value(0)
time.sleep(5)

print("✅ System Ready")

# =========================
# DOUBLE CLICK VARIABLES
# =========================
last_press_time = 0
click_count = 0
DOUBLE_CLICK_TIME = 500

# =========================
# MAIN LOOP
# =========================
while True:

    # 📲 Handle incoming calls
    check_incoming_call()

    # SOS BUTTON
    if SOS.value() == 0:
        now = time.ticks_ms()

        if time.ticks_diff(now, last_press_time) < DOUBLE_CLICK_TIME:
            click_count += 1
        else:
            click_count = 1

        last_press_time = now

        while SOS.value() == 0:
            time.sleep(0.05)

        if click_count == 2:

            print("🆘 SOS TRIGGERED")
            LED.value(1)
            
            make_call(SOS_NUMBER, RETRY_COUNT, CALL_DURATION)

            lat, lon = get_location()

            if lat and lon:
                link = "https://maps.google.com/?q={},{}".format(lat, lon)
                msg = "🚨 SOS ALERT!\n" + link
            else:
                msg = "🚨 SOS ALERT!\nLocation not available"

            send_sms(SOS_NUMBER, msg)


            LED.value(0)
            click_count = 0

            print("✅ DONE\n")
            time.sleep(2)

    time.sleep(0.1)
