import machine
from time import sleep

# Define the UART pins and create a UART object
gps_serial = machine.UART(2, baudrate=9600, tx=2, rx=16)

def parse_coords(nmea_sentence):
    parts = nmea_sentence.split(',')
    if parts[0] == "$GPRMC" and parts[2] == 'A':  # Check if it's a valid fix
        raw_lat = parts[3]
        lat_dir = parts[4]
        raw_lon = parts[5]
        lon_dir = parts[6]

        # Convert raw NMEA format to decimal degrees
        lat_deg = float(raw_lat[:2])
        lat_min = float(raw_lat[2:])
        lat = lat_deg + (lat_min / 60)
        if lat_dir == 'S':
            lat = -lat

        lon_deg = float(raw_lon[:3])
        lon_min = float(raw_lon[3:])
        lon = lon_deg + (lon_min / 60)
        if lon_dir == 'W':
            lon = -lon

        return lat, lon
    return None, None

while True:
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
    sleep(0.5)