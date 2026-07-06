import machine
import time

# 1. Pins Setup (Where parts are connected)
button = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_UP)
relay = machine.Pin(13, machine.Pin.OUT) # Relay: 0 is ON, 1 is OFF
led = machine.Pin(2, machine.Pin.OUT)    # LED: 1 is ON, 0 is OFF
rain_sensor = machine.Pin(18, machine.Pin.IN)
buzzer = machine.Pin(5, machine.Pin.OUT)

# 2. Starting Position (Everything should be OFF initially)
relay.value(1)  # Motor OFF
led.value(0)    # LED OFF
buzzer.value(0) # Buzzer OFF

# 3. State Variables (To keep track of states and timers)
is_motor_on = False
sensor_time = 0
motor_start_time = 0
motor_runing_time = 20000 # 20 Seconds
sensor_off_time = 2000   # 10 Seconds

# NEW Variables for Siren Sound
is_siren_active = False
siren_start_time = 0
siren_toggle_time = 0

print("Project Started! Press the button...")

# 4. Main Loop (Runs continuously)
while True:
    # 'current_time' acts as our digital stopwatch for the whole system
    current_time = time.ticks_ms()

    # --- STEP A: CHECK BUTTON PRESS ---
    if button.value() == 0:  # Button value is 0 when pressed
        time.sleep(0.3)      # Short delay to avoid button debounce (double click)
        
        if is_motor_on == False:
            # If Motor is OFF, turn it ON
            relay.value(0)
            led.value(1)
            is_motor_on = True
            
            # Start stopwatches
            sensor_time = time.ticks_ms() 
            motor_start_time = time.ticks_ms()
            
            print("Motor ON!")
        else:
            # If Motor is ON, turn it OFF manually
            relay.value(1)
            led.value(0)
            is_motor_on = False
            print("Motor OFF! (Manual Button Press)")

    # --- STEP B: CHECK SENSORS & TIMEOUTS (Only when Motor is ON) ---
    if is_motor_on == True:
        
        # FEATURE 1: Maximum Run Time Check
        if time.ticks_diff(current_time, motor_start_time) > motor_runing_time:
            relay.value(1)
            led.value(0)
            is_motor_on = False
            print("Motor OFF! (Time Limit Reached)")
            
        else:
            # FEATURE 2: Rain Sensor Check
            # Is there data from the sensor?
            if rain_sensor.value() == 0:
                sensor_time = time.ticks_ms() # Reset the sensor stopwatch!
            
            # Check if time passed without sensor data
            if time.ticks_diff(current_time, sensor_time) > sensor_off_time:
                # Turn OFF Motor and LED
                relay.value(1)
                led.value(0)
                is_motor_on = False
                print("Motor OFF! (No sensor data for 10 seconds)")
                
                # Turn ON Siren Mode
                is_siren_active = True
                siren_start_time = time.ticks_ms()   # Overall 2-second stopwatch
                siren_toggle_time = time.ticks_ms()  # Fast ON/OFF stopwatch
                buzzer.value(1)

    # --- STEP C: SIREN SOUND LOGIC (Pulsing Beeps) ---
    if is_siren_active == True:
        
        # 1. Fast Toggle: Turn Buzzer ON and OFF every 150 milliseconds
        if time.ticks_diff(current_time, siren_toggle_time) > 150:
            if buzzer.value() == 1:
                buzzer.value(0)
            else:
                buzzer.value(1)
            
            siren_toggle_time = current_time # Reset the fast stopwatch
            
        # 2. Main Timeout: Stop the Siren completely after 2 seconds (2000 ms)
        if time.ticks_diff(current_time, siren_start_time) > 4000: 
            buzzer.value(0) # Force Buzzer OFF
            is_siren_active = False # Turn off siren mode

    # Small delay to prevent the board from crashing or rebooting
    time.sleep(0.01)
