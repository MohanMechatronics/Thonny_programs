import machine, network, espnow, time, struct

# Wi-Fi in station mode (mandatory for ESP-NOW)
w0 = network.WLAN(network.STA_IF)
w0.active(True)
w0.disconnect()

# ESP-NOW init
e = espnow.ESPNow()
e.active(True)
peer = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # Broadcast or replace with actual MAC
e.add_peer(peer)

# ADC pins: [Aileron, Throttle2, Elev, Throttle1]
adc_pins = [32, 33, 34, 35]
adcs = [machine.ADC(machine.Pin(pin)) for pin in adc_pins]
for adc in adcs:
    adc.atten(machine.ADC.ATTN_11DB)  # Full range (0–4095)

# Trim settings
TRIM_STEP = 5
TRIM_MIN = -1000
TRIM_MAX = 1000

# Trim offsets
aileron_trim = 0      # ADC[0] - Pin 32
throttle2_trim = 0    # ADC[1] - Pin 33
throttle1_trim = 0    # ADC[3] - Pin 35

# Trim buttons (active LOW)
left_aileron_btn = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP)
right_aileron_btn = machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_UP)

down_throttle1_btn = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
up_throttle1_btn = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

down_throttle2_btn = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
up_throttle2_btn = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)


while True:
    try:
        # --- Trim button check ---
        if not left_aileron_btn.value():
            aileron_trim = max(TRIM_MIN, aileron_trim - TRIM_STEP)
        if not right_aileron_btn.value():
            aileron_trim = min(TRIM_MAX, aileron_trim + TRIM_STEP)

        if not down_throttle1_btn.value():
            throttle1_trim = max(TRIM_MIN, throttle1_trim - TRIM_STEP)
        if not up_throttle1_btn.value():
            throttle1_trim = min(TRIM_MAX, throttle1_trim + TRIM_STEP)

        if not down_throttle2_btn.value():
            throttle2_trim = max(TRIM_MIN, throttle2_trim - TRIM_STEP)
        if not up_throttle2_btn.value():
            throttle2_trim = min(TRIM_MAX, throttle2_trim + TRIM_STEP)

        # --- Read ADCs ---
        values = [adc.read() for adc in adcs]

        # Apply trims
        values[0] = max(0, min(4095, values[0] + aileron_trim))     # Aileron
        values[1] = max(0, min(4095, values[1] + throttle2_trim))   # Throttle2
        values[3] = max(0, min(4095, values[3] + throttle1_trim))   # Throttle1

        # Reverse aileron channel after trim
        values[1] = 4095 - values[1]

        # Pad to 6 channels
        while len(values) < 6:
            values.append(0)

        # Send over ESP-NOW
        packed = struct.pack('6H', *values)
        e.send(peer, packed)

        # Debug
        print("Sent:", values, "| AilTrim:", aileron_trim, "| Thr1Trim:", throttle1_trim, "| Thr2Trim:", throttle2_trim)
        time.sleep(0.05)

    except KeyboardInterrupt:
        print("Program stopped")
        raise

