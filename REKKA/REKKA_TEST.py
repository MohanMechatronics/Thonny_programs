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
    return int((us / period) * 65535)

# Servos
servo1 = machine.PWM(machine.Pin(9), freq=50)
servo2 = machine.PWM(machine.Pin(10), freq=50)

# Motors (throttle control)
motors = [
    machine.PWM(machine.Pin(1), freq=50),
    machine.PWM(machine.Pin(2), freq=50),
    machine.PWM(machine.Pin(4), freq=50),
    machine.PWM(machine.Pin(5), freq=50),
]
for m in motors:
    m.duty_u16(0)

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
            duty1 = us_to_duty(map_servo(elevator))
            servo1.duty_u16(duty1)

            duty2 = us_to_duty(map_servo(rudder))
            servo2.duty_u16(duty2)

            # Motor throttle control (map 0–4095 → 0–65535)
            motor_speed = int((throttle / 4095) * 65535)
            for m in motors:
                m.duty_u16(motor_speed)

            print(f"ELEV={elevator} RUD={rudder} THR={throttle} AIL={aileron}")

    except OSError:
        # Timeout: check connection
        if client_address and utime.ticks_diff(utime.ticks_ms(), last_packet_time) > CONNECTION_TIMEOUT_MS:
            print("Connection lost. No data received.")
            client_address = None
    except KeyboardInterrupt:
        machine.reset()
        utime.sleep(10)


