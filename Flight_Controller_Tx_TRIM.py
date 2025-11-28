import machine, network, espnow, time, struct

# Wi-Fi in station mode (mandatory for ESP-NOW)
w0 = network.WLAN(network.STA_IF)
w0.active(True)
w0.disconnect()

# ESP-NOW initialization
e = espnow.ESPNow()
e.active(True)
peer = b'\xFF\xFF\xFF\xFF\xFF\xFF'   # Broadcast or replace with actual MAC
e.add_peer(peer)

# ADC pins mapped to flight controls
# pin35=Elevator, pin34=Rudder, pin32=Aileron, pin33=Throttle
adc_pins = [35, 34, 32, 33]          # [Elevator, Rudder, Aileron, Throttle]
adcs = [machine.ADC(machine.Pin(pin)) for pin in adc_pins]
for adc in adcs:
    adc.atten(machine.ADC.ATTN_11DB) # Full range (0–4095)

# Trim settings
TRIM_STEP = 5                        # Step size for trim adjustments
TRIM_MIN = -1000                     # Minimum trim value
TRIM_MAX = 1000                      # Maximum trim value

# Trim offsets for each control channel
elevator_trim = 0                    # ADC[0] - Pin 35
rudder_trim = 0                      # ADC[1] - Pin 34
aileron_trim = 0                     # ADC[2] - Pin 32
throttle_trim = 0                    # ADC[3] - Pin 33

# Trim buttons configuration (active LOW)
down_elevator_btn  = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP)    # Down elevator trim
up_elevator_btn    = machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_UP)    # Up elevator trim

left_throttle_btn  = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)    # Left throttle trim
right_throttle_btn = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)    # Right throttle trim

# Control pins for elevator reverse function
elevator_mode_pin    = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)  # Mode selection
elevator_reverse_pin = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)  # Reverse control

# Control pins for rudder reverse function
rudder_mode_pin    = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)   # Mode selection
rudder_reverse_pin = machine.Pin(5,  machine.Pin.IN, machine.Pin.PULL_UP)   # Reverse control

# Rudder trim buttons
left_rudder_btn    = machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP)   # Left rudder trim
right_rudder_btn   = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)   # Right rudder trim


while True:
    try:
        # --- Process trim button inputs ---
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
        values = [adc.read() for adc in adcs]                       # Read all ADC values

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