import machine
import time

# Define pins
rudder_rev1 = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)
rudder_rev2 = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)
elev_rev1   = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
elev_rev2   = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

print("Testing reverse switch pins...")
print("Press each switch and watch for 0 when pressed.\n")

while True:
    try:
        print("Rud1:", rudder_rev1.value(),
              "Rud2:", rudder_rev2.value(),
              "Elev1:", elev_rev1.value(),
              "Elev2:", elev_rev2.value())
        time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopped.")
        break
