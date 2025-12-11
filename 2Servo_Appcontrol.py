import network
import socket
import machine
import struct
import utime

# ===== Soft AP Setup =====

SSID = "RC"
PASSWORD = "12345678"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, password=PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)

print("SoftAP created:", SSID)
print("IP config:", ap.ifconfig())

# ===== UDP Socket Setup =====
UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ap.ifconfig()[0], UDP_PORT))
sock.settimeout(1.0)

print("Listening on", ap.ifconfig()[0], "port", UDP_PORT)

# Make socket non-blocking
sock.setblocking(False)

# ===== Servo Functions =====
def angle_to_us(angle):
	# angle 0-180 -> 500-2500 us
	return 500 + (angle / 180.0) * 2000

def us_to_duty(us, freq=50):
	period = 1000000 // freq
	return int((us / period) * 65535)

# Speed configuration — max speed
STEP_DEG = 5.0
DELAY_MS = 8

# Servos
servo1 = machine.PWM(machine.Pin(10), freq=50) #14
servo2 = machine.PWM(machine.Pin(9), freq=50) #47

# ===== Main Loop =====
client_address = None
last_packet_time = utime.ticks_ms()
CONNECTION_TIMEOUT_MS = 3000
servo_position = 0.0  # 0 to 180 degrees
servo_direction = 1  # 1 for increasing, -1 for decreasing
last_servo_update = utime.ticks_ms()  # Track last servo update time
throttle_active = False  # Track if throttle was > 10
data_received = False  # Track if new data arrived this cycle

while True:
    data_received = False  # Reset flag at start of loop
    
    try:
        data, addr = sock.recvfrom(1024)

        if client_address is None:
            print("Connection successful from:", addr[0])
        client_address = addr
        last_packet_time = utime.ticks_ms()

        # Handshake
        if data == b'PING':
            sock.sendto(b'PONG', addr)
            continue

        # Joystick packet (8 bytes expected)
        if len(data) == 8:
            elevator, rudder, throttle, aileron = struct.unpack("<4H", data)
            data_received = True  # Mark that new data arrived
            print(f"ELEV={elevator} RUD={rudder} THR={throttle} AIL={aileron}")

            # ===== If throttle > 10: set flag to run servo =====
            if throttle > 10:
                throttle_active = True
            else:
                throttle_active = False

    except OSError as e:
        # No data available (non-blocking mode) - servo runs on PAST data
        pass

    # ===== Run servo oscillation independently (non-blocking) =====
    now = utime.ticks_ms()
    if throttle_active and utime.ticks_diff(now, last_servo_update) >= DELAY_MS:
        last_servo_update = now

        # Step size in degrees per loop iteration
        step = STEP_DEG * servo_direction

        servo_position += step
        if servo_position >= 180:
            servo_position = 180
            servo_direction = -1
        elif servo_position <= 0:
            servo_position = 0
            servo_direction = 1

        us1 = angle_to_us(servo_position)
        duty1 = us_to_duty(us1)
        # servo1 follows position, servo2 is inverse (180 - position)
        inv_position = 180 - servo_position
        us2 = angle_to_us(inv_position)
        duty2 = us_to_duty(us2)
        servo1.duty_u16(duty1)
        servo2.duty_u16(duty2)

