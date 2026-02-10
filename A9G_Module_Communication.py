from machine import UART, Pin
import time

# ---------- UART SETUP ----------
gsm = UART(1, baudrate=115200, tx=17, rx=16)

# ---------- A9G POWER ON ----------
PON = Pin(13, Pin.OUT)
PON.value(1)
time.sleep(2)
PON.value(0)
time.sleep(5)

print("A9G AT Console Ready")
print("Type AT commands and press Enter")
print("Type 'exit' to stop\n")

# ---------- AT CONSOLE ----------
while True:
    try:
        cmd = input("AT> ")

        if cmd.lower() == "exit":
            print("Exiting AT console")
            break

        gsm.write(cmd + "\r\n")
        time.sleep(0.5)

        # Read response
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < 3000:
            if gsm.any():
                data = gsm.read()
                if data:
                    print(data.decode(), end="")

    except KeyboardInterrupt:
        print("\nStopped by user")
        break
