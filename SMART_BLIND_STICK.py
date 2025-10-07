import machine
import utime
from time import sleep

# ==== Ultrasonic + Buzzer Setup ====
buzzer = machine.Pin(4, machine.Pin.OUT)
trigger = machine.Pin(1, machine.Pin.OUT)
echo = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_DOWN)

# ==== GPS Setup ====
gps_serial = machine.UART(2, baudrate=9600, tx=2, rx=16)

# ---- Helper: Ultrasonic Distance ----
def get_distance():
    trigger.off()
    utime.sleep_us(2)


trigger.on()
    utime.sleep_us(10)
    trigger.off()

    while echo.value() == 0:
        send_time = utime.ticks_us()
    while echo.value() == 1:
        received_time = utime.ticks_us()

    duration = received_time - send_time
    total_distance = 0.0343 * duration
    return total_distance / 2  # cm

# ---- Helper: GPS Parsing ----
def parse_coords(nmea_sentence):
    parts = nmea_sentence.split(',')
    if parts[0] == "$GPRMC" and parts[2] == 'A':  # Valid fix
        raw_lat = parts[3]
        lat_dir = parts[4]
        raw_lon = parts[5]
        lon_dir = parts[6]

        # Latitude conversion
        lat_deg = float(raw_lat[:2])
        lat_min = float(raw_lat[2:])
        lat = lat_deg + (lat_min / 60)
        if lat_dir == 'S':
            lat = -lat

        # Longitude conversion
        lon_deg = float(raw_lon[:3])
        lon_min = float(raw_lon[3:])
        lon = lon_deg + (lon_min / 60)
        if lon_dir == 'W':
            lon = -lon

        return lat, lon
    return None, None

# ==== Main Loop ====
while True:
    # --- Distance Measurement ---
    object_distance = get_distance()
    if object_distance < 35:  # Danger zone
        buzzer.on()
        print(object_distance, "cm Danger")
    else:
        buzzer.off()
        print(object_distance, "cm Safe")

    # --- GPS Data ---
    if gps_serial.any():
        line = gps_serial.readline()
        if line:
            try:
                line = line.decode('utf-8').strip()
                lat, lon = parse_coords(line)
                if lat is not None and lon is not None:
                    print(f"Latitude: {lat}, Longitude: {lon}")
                    print(f"Google Maps: https://www.google.com/maps?q={lat},{lon}")
            except Exception as e:
                print("Error parsing line:", e)

    sleep(0.5)  # small delay
