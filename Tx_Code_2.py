import machine, network, espnow, time, struct

w0 = network.WLAN(network.STA_IF)
w0.active(True)
w0.disconnect()

e = espnow.ESPNow()
e.active(True)
peer = b'\xFF\xFF\xFF\xFF\xFF\xFF'
e.add_peer(peer)

adc_pins = [35, 34, 39, 36]          # [Elevator, Rudder, Aileron, Throttle]
adcs = [machine.ADC(machine.Pin(pin)) for pin in adc_pins]
for adc in adcs:
    adc.atten(machine.ADC.ATTN_11DB)

# Trim settings
TRIM_STEP = 5
TRIM_MIN = -1000
TRIM_MAX = 1000

# Trim offsets for each control channel
elevator_trim = 0
rudder_trim = 0
aileron_trim = 0
throttle_trim = 0

# Trim buttons configuration
up_elevator_btn    = machine.Pin(21, machine.Pin.IN, machine.Pin.PULL_UP)    # Up elevator trim
down_elevator_btn  = machine.Pin(22, machine.Pin.IN, machine.Pin.PULL_UP)    # Down elevator trim
left_throttle_btn  = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)    # Left throttle trim
right_throttle_btn = machine.Pin(32, machine.Pin.IN, machine.Pin.PULL_UP)    # Right throttle trim

# Rudder trim buttons
left_rudder_btn    = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)   # Left rudder trim
right_rudder_btn   = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)   # Right rudder trim


# Control pins for reverse function
elevator_mode_pin    = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)
rudder_mode_pin    = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)
# elevator_reverse_pin = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
# rudder_reverse_pin = machine.Pin(13,  machine.Pin.IN, machine.Pin.PULL_UP)

while True:
    try:
        # Elevator trim adjustments
        if not down_elevator_btn.value():
            elevator_trim = max(TRIM_MIN, elevator_trim - TRIM_STEP)
        if not up_elevator_btn.value():
            elevator_trim = min(TRIM_MAX, elevator_trim + TRIM_STEP)

        # Rudder trim adjustments
        if not left_rudder_btn.value():
            rudder_trim = max(TRIM_MIN, rudder_trim - TRIM_STEP)
        if not right_rudder_btn.value():
            rudder_trim = min(TRIM_MAX, rudder_trim + TRIM_STEP)

        # Throttle trim adjustments
        if not left_throttle_btn.value():
            throttle_trim = max(TRIM_MIN, throttle_trim - TRIM_STEP)
        if not right_throttle_btn.value():
            throttle_trim = min(TRIM_MAX, throttle_trim + TRIM_STEP)

        # --- Read and process control values ---
        values = [adc.read() for adc in adcs]

        # Apply trims and process elevator control
        values[0] = max(0, min(4095, values[0] + elevator_trim))    # Elevator (Pin 35)
        if elevator_mode_pin.value() and not elevator_reverse_pin.value():
            values[0] = 4095 - values[0]                            # Reverse elevator if enabled

        # Apply trims and process rudder control
        values[1] = max(0, min(4095, values[1] + rudder_trim))      # Rudder (Pin 34)
        if rudder_mode_pin.value() and not rudder_reverse_pin.value():
            values[1] = 4095 - values[1]                            # Reverse rudder if enabled

        # Apply remaining trims
        values[2] = max(0, min(4095, values[2] + aileron_trim))     # Aileron (Pin 32)
        values[3] = max(0, min(4095, values[3] + throttle_trim))    # Throttle (Pin 33)

        # --- Prepare and send data ---
        while len(values) < 6:                                      # Pad to 6 channels
            values.append(0)

        packed = struct.pack('6H', *values)                         # Pack values for transmission
        e.send(peer, packed)                                        # Send over ESP-NOW

        # --- Debug output ---
        print("Sent:", values, "| Elevator:", elevator_trim, "| Rudder:", rudder_trim, 
              "| Aileron:", aileron_trim, "| Throttle:", throttle_trim)
        time.sleep(0.05)                                           # Control loop delay

    except KeyboardInterrupt:
        print("Program stopped")
        raise