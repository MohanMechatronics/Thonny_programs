import machine
import time

# Setup digital input pin
flame = machine.Pin(14, machine.Pin.IN)

while True:
    state = flame.value()
    
    if state == 0:
        print("🔥 Flame Detected!")
    else:
        print("✅ No Flame")
    
    time.sleep(0.5)