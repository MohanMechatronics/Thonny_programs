import cellular
import time
from machine import Pin
import machine

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────
WAIT_FOR_SIM_INIT_TIMEOUT  = 20   # seconds
WAIT_FOR_NETWORK_TIMEOUT   = 30   # seconds

ADMIN_NUMBER   = "+917358289559"
STARTUP_MSG    = "A9G ready"

# ─────────────────────────────────────────────
#  HARDWARE
# ─────────────────────────────────────────────
led = Pin(27, Pin.OUT)

# ─────────────────────────────────────────────
#  UTILITY HELPERS
# ─────────────────────────────────────────────
def blink_led(times, interval=0.5):
    """Blink the onboard LED a given number of times."""
    for _ in range(times):
        led.value(1)
        time.sleep(interval)
        led.value(0)
        time.sleep(interval)

def countdown_timer(seconds, message="Waiting"):
    """Print a live countdown on a single line."""
    for remaining in range(seconds, 0, -1):
        print("{}... {} seconds remaining".format(message, remaining), end='\r')
        time.sleep(1)
    print()

def interpret_network_status(status_code):
    """Return a human-readable string for a cellular network status code."""
    status_messages = {
        0: "Not registered, not searching",
        1: "Registered, home network",
        2: "Not registered, searching for network",
        3: "Registration denied",
        4: "Unknown status",
        5: "Registered, roaming"
    }
    return status_messages.get(status_code, "Invalid status code")

# ─────────────────────────────────────────────
#  FUNCTION 1 – NETWORK INITIALISATION
# ─────────────────────────────────────────────
def initialize_device():
    """
    Perform first-time SIM check and network registration.
    Returns True on success, False on failure.
    """
    print("\n=== Device Initialization ===")
    blink_led(5)

    # ── SIM ──
    print("Getting SIM info...")
    countdown_timer(WAIT_FOR_SIM_INIT_TIMEOUT, message="Initializing SIM")

    if not cellular.is_sim_present():
        print("ERROR: SIM not inserted!")
        return False

    print("SIM inserted.")
    print("  ICCID :", cellular.get_iccid())
    print("  IMSI  :", cellular.get_imsi())

    # ── Network ──
    print("Waiting for network registration...")
    countdown_timer(WAIT_FOR_NETWORK_TIMEOUT, message="Waiting for network")

    if not cellular.is_network_registered():
        print("ERROR: Network not registered.")
        return False

    network_status = interpret_network_status(cellular.get_network_status())
    print("  Network Status :", network_status)

    operator_info = cellular.register()
    print("  Operator       :", operator_info[1])
    print("  Signal Quality :", cellular.get_signal_quality()[0])

    print("=== Initialization complete ===\n")
    return True

# ─────────────────────────────────────────────
#  FUNCTION 2 – SMS  (send & receive)
# ─────────────────────────────────────────────
def sms_event_handler(evt):
    """Callback fired by the cellular stack for SMS events."""
    if evt == cellular.SMS_SENT:
        print("[SMS] Startup message sent successfully.")
    else:
        print("[SMS] SMS event:", evt)

def send_startup_sms():
    """Send a startup notification to the admin number."""
    print("[SMS] Registering SMS callback...")
    cellular.on_sms(sms_event_handler)

    print("[SMS] Sending startup message to {}...".format(ADMIN_NUMBER))
    cellular.SMS(ADMIN_NUMBER, STARTUP_MSG).send()

def check_incoming_sms():
    """
    Read all pending SMS messages, print their content,
    then delete them from the modem storage.
    Returns the list of (phone_number, message) tuples that were found.
    """
    found = []
    messages_list = cellular.SMS.list()
    messages_list = [msg for msg in messages_list if msg is not None]

    if not messages_list:
        return found

    for msg in messages_list:
        try:
            number  = msg.phone_number
            content = msg.message
            print("\n[SMS] New message!")
            print("  From   : {}".format(number))
            print("  Message: {}".format(content))
            found.append((number, content))
            msg.withdraw()            # delete from modem after reading
        except AttributeError as e:
            print("[SMS] Error reading message attributes: {}".format(e))

    return found

# ─────────────────────────────────────────────
#  FUNCTION 3 – CALLS  (make & receive)
# ─────────────────────────────────────────────
def call_event_handler(event):
    """
    Callback fired by the cellular stack for call events.
      - 'hangup'        : the remote side ended the call
      - anything else   : treated as an incoming caller ID string
    """
    if event == 'hangup':
        print("[CALL] Call ended by remote party.")
    else:
        print("[CALL] Incoming call from: {}".format(event))
        time.sleep(2)                  # short delay before answering
        try:
            if cellular.answer():
                print("[CALL] Call answered.")
            else:
                print("[CALL] Failed to answer call.")
        except Exception as e:
            print("[CALL] Error answering call: {}".format(e))

def register_call_handler():
    """Register the call-event callback with the modem."""
    print("[CALL] Registering call event handler...")
    cellular.on_call(call_event_handler)

def make_call(phone_number, duration=10):
    """
    Dial phone_number, wait duration seconds, then hang up.
    """
    print("[CALL] Dialling {}...".format(phone_number))
    try:
        if cellular.dial(phone_number):
            print("[CALL] Call initiated successfully.")
        else:
            print("[CALL] Failed to initiate call.")
    except Exception as e:
        print("[CALL] Error during dial: {}".format(e))
        return

    print("[CALL] Waiting {} seconds before hanging up...".format(duration))
    time.sleep(duration)

    try:
        if cellular.dial(False):       # False = hang up
            print("[CALL] Call ended.")
        else:
            print("[CALL] Failed to end call.")
    except Exception as e:
        print("[CALL] Error ending call: {}".format(e))

# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
def main():
    # ── Step 1: network init ──────────────────
    if not initialize_device():
        print("Device initialization failed. Restarting in 5 s...")
        time.sleep(5)
        machine.reset()

    # ── Step 2: SMS setup & startup message ───
    send_startup_sms()

    # ── Step 3: register call handler ─────────
    register_call_handler()

    # ── Step 4: make an outgoing call ─────────
    make_call(ADMIN_NUMBER, duration=10)

    # ── Step 5: main event loop ───────────────
    print("\n[MAIN] Entering main loop. Monitoring SMS & calls...\n")
    while True:
        check_incoming_sms()
        time.sleep(5)                  # poll every 5 seconds

main()