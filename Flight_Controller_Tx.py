import machine, network, espnow, time, struct

# Wi-Fi in station mode (mandatory for ESP-NOW)
w0 = network.WLAN(network.STA_IF)
w0.active(True)
w0.disconnect()

# ESP-NOW init
e = espnow.ESPNow()
e.active(True)
peer = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # Broadcast (or replace with receiver MAC)
e.add_peer(peer)

# Analog pins (adjust as per wiring)
adc_pins = [32, 33, 34, 35, 36, 39]  # Example GPIOs
adcs = [machine.ADC(machine.Pin(pin)) for pin in adc_pins]
for adc in adcs:
    adc.atten(machine.ADC.ATTN_11DB)  # Max range (0-4095)

# Aileron trim (channel on pin 32, index 0)
aileron_trim_offset = 0
elevator_trim_offset = 0
TRIM_STEP = 20
TRIM_MIN = -500
TRIM_MAX = 500

# Setup trim switches for aileron
left_atrim_btn = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_DOWN)   # Decrease
right_atrim_btn = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)  # Increase
# Setup trim switches for elevator
left_etrim_btn = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_DOWN)   # Pitch Down
right_etrim_btn = machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_DOWN)  # Pitch Up

while True:
    try:
        # Read trim buttons (active LOW)
        if not left_atrim_btn.value():
            aileron_trim_offset = min(TRIM_MAX, aileron_trim_offset + TRIM_STEP)
        if not right_atrim_btn.value():
            aileron_trim_offset = max(TRIM_MIN, aileron_trim_offset - TRIM_STEP)
        if not left_etrim_btn.value():
            elevator_trim_offset = max(TRIM_MIN, elevator_trim_offset - TRIM_STEP)
        if not right_etrim_btn.value():
            elevator_trim_offset = min(TRIM_MAX, elevator_trim_offset + TRIM_STEP)

        values = [adc.read() for adc in adcs]

        # Apply aileron trim to pin 32 (index 0)
        values[0] = max(0, min(4095, values[0] + aileron_trim_offset))
        # Reverse pin 32 value (after trim)
        values[0] = 4095 - values[0]
        
        # Apply elevator trim to pin 33 (index 1)
        values[1] = max(0, min(4095, values[1] + elevator_trim_offset))
#         # Reverse pin 33 value (after trim)
#         values[1] = 4095 - values[1]

        packed = struct.pack('6H', *values)
        e.send(peer, packed)
        print("Sent:", values, "Aileron Trim:", aileron_trim_offset, "Elevator Trim:", elevator_trim_offset)
        time.sleep(0.1)
        
    except Exception as e:
        raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Program stopped")
        raise SystemExit
