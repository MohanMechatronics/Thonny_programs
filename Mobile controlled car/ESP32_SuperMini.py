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

# ===== Servo + Motor Setup =====
def map_servo(x, in_min=0, in_max=4095, out_min=500, out_max=2500):
    """Map joystick (0–4095) to servo microseconds (500–2500)."""
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def us_to_duty(us, freq=50):
    """Convert microseconds to duty_u16 for given PWM frequency."""
    period = 1000000 // freq  # microseconds per cycle (20ms at 50Hz)
    duty = int((us / period) * 65535)
    return max(0, min(65535, duty))  # Clamp safely within range

# Servos
servo_aileron = machine.PWM(machine.Pin(4), freq=50)   # Aileron
servo_elevator = machine.PWM(machine.Pin(7), freq=50)  # Elevator (moved from 10 to 7)

# Motors
motor_low = machine.PWM(machine.Pin(3), freq=50)   # Motor for 0–1900 range
motor_high = machine.PWM(machine.Pin(1), freq=50) # Motor for 2200–4000 range

motor_low.duty_u16(0)
motor_high.duty_u16(0)

# ===== Main Loop =====
client_address = None
last_packet_time = utime.ticks_ms()
CONNECTION_TIMEOUT_MS = 3000

while True:
    try:
        data, addr = sock.recvfrom(1024)

        if client_address is None:
            print("Connection successful from:", addr[0])
        client_address = addr
        last_packet_time = utime.ticks_ms()

        # Handshake
        if data == b'PING':
            sock.sendto(b'PONG', addr)
            print("Responded to PING from", addr[0])
            continue

        # Joystick packet (8 bytes expected)
        if len(data) == 8:
            elevator, rudder, throttle, aileron = struct.unpack("<4H", data)

            # Servo control
            servo_aileron.duty_u16(us_to_duty(map_servo(aileron)))
            servo_elevator.duty_u16(us_to_duty(map_servo(elevator)))

            # ===== Throttle zone control =====
            if throttle <= 1900:
                # Map 0–1900 → 0–65535 for Pin 8
                motor_speed = int((throttle / 1900) * 65535)
                motor_speed = max(0, min(65535, motor_speed))
                motor_low.duty_u16(motor_speed)  # Pin 8 active
                motor_high.duty_u16(0)           # Pin 10 off

            elif throttle >= 2200:
                # Map 2200–4000 → 0–65535 for Pin 10
                motor_speed = int(((throttle - 2200) / (4000 - 2200)) * 65535)
                motor_speed = max(0, min(65535, motor_speed))
                motor_high.duty_u16(motor_speed) # Pin 10 active
                motor_low.duty_u16(0)            # Pin 8 off

            else:
                # Dead zone (1900–2200)
                motor_low.duty_u16(0)
                motor_high.duty_u16(0)

            print(f"ELEV={elevator} RUD={rudder} THR={throttle} AIL={aileron}")

    except OSError:
        # Timeout: check connection
        if client_address and utime.ticks_diff(utime.ticks_ms(), last_packet_time) > CONNECTION_TIMEOUT_MS:
            print("Connection lost. No data received.")
            client_address = None
    except KeyboardInterrupt:
        machine.reset()
        utime.sleep(10)

