import cellular
import time

WAIT_FOR_SIM_TIMEOUT = 20      # max wait time
WAIT_FOR_NETWORK_TIMEOUT = 30  # max wait time

admin_number = "+917358289559"
message_to_send = "SOS Alert "

# =========================
# SMS CALLBACK 
# =========================
def sms_handler(evt):
    if evt == cellular.SMS_SENT:
        print("Startup SMS sent Successfully")

# =========================
# NETWORK STATUS
# =========================
def interpret_network_status(status_code):
    if status_code == 0:
        return "Not registered, not searching"
    elif status_code == 1:
        return "Registered, home network"
    elif status_code == 2:
        return "Not registered, searching"
    elif status_code == 3:
        return "Registration denied"
    elif status_code == 4:
        return "Unknown"
    elif status_code == 5:
        return "Registered, roaming"
    else:
        return "Invalid"

# =========================
# WAIT FOR SIM (SMART)
# =========================
def wait_for_sim():
    print("Checking SIM...")

    start = time.time()
    while time.time() - start < WAIT_FOR_SIM_TIMEOUT:
        if cellular.is_sim_present():
            print("✅ SIM detected")
            return True
        time.sleep(0.5)

    print("❌ SIM not detected")
    return False

# =========================
# WAIT FOR NETWORK (SMART)
# =========================
def wait_for_network():
    print("Connecting to network...")

    start = time.time()
    while time.time() - start < WAIT_FOR_NETWORK_TIMEOUT:
        if cellular.is_network_registered():
            print("✅ Network connected")
            return True
        print("Searching...", end="\r")
        time.sleep(1)

    print("\n❌ Network failed")
    return False

# =========================
# MAIN
# =========================
def main():
    print("Initializing...")

    # SIM CHECK (no fixed delay)
    if not wait_for_sim():
        return

    print("ICCID:", cellular.get_iccid())
    print("IMSI:", cellular.get_imsi())

    # NETWORK CHECK (no fixed delay)
    if not wait_for_network():
        return

    network_status = interpret_network_status(cellular.get_network_status())
    print("Network Status:", network_status)

    operator_info = cellular.register()
    print("Operator:", operator_info[1])

    signal_quality = cellular.get_signal_quality()
    print("Signal:", signal_quality[0])

    # SMS setup
    cellular.on_sms(sms_handler)

    print("Sending startup SMS...")
    cellular.SMS(admin_number, message_to_send).send()

    # =========================
    # READ INCOMING SMS
    # =========================
    print("Listening for incoming SMS...")

    while True:
        messages_list = cellular.SMS.list()
        messages_list = [msg for msg in messages_list if msg is not None]

        for msg in messages_list:
            try:
                print("\n📩 New message")
                print("From:", msg.phone_number)
                print("Message:", msg.message)

                msg.withdraw()  # delete after reading

            except Exception as e:
                print("Error:", e)

        time.sleep(1)  # small delay to avoid overload


# =========================
# RUN
# =========================
main()
