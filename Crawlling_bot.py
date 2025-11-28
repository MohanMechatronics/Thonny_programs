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

# ===== L293D Motor Pins =====
# Motor A
IN1 = machine.Pin(19, machine.Pin.OUT)
IN2 = machine.Pin(18, machine.Pin.OUT)

# Motor B
IN3 = machine.Pin(22, machine.Pin.OUT)
IN4 = machine.Pin(23, machine.Pin.OUT)

# Enable pins (use PWM for speed control)
EN1 = machine.PWM(machine.Pin(21), freq=1000)   # Motor A
EN2 = machine.PWM(machine.Pin(25), freq=1000)   # Motor B

# Set speeds
EN1.duty_u16(int(65535 * 0.90))   # 50% speed
EN2.duty_u16(int(65535 * 0.90))   # 50% speed

# ===== Motor Movement Functions =====
def stop_all():
    IN1.value(0)
    IN2.value(0)
    IN3.value(0)
    IN4.value(0)

def forward():
    IN1.value(1)
    IN2.value(0)
    IN3.value(1)
    IN4.value(0)

def reverse():
    IN1.value(0)
    IN2.value(1)
    IN3.value(0)
    IN4.value(1)

def turn_right():
    IN1.value(0)
    IN2.value(1)
    IN3.value(1)
    IN4.value(0)

def turn_left():
    IN1.value(1)
    IN2.value(0)
    IN3.value(0)
    IN4.value(1)

# ===== MAIN LOOP =====
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

        # Joystick packet (8 bytes)
        # We will only use: X = rudder, Y = elevator
        if len(data) == 8:
            elevator, rudder, throttle, aileron = struct.unpack("<4H", data)

            X = aileron     # left / right
            Y = elevator    # forward / reverse

            # ===== Movement Logic =====
            if Y > 2300:
                forward()
            elif Y < 1700:
                reverse()
            elif X < 1700:
                turn_left()
            elif X > 2300:
                turn_right()
            else:
                stop_all()

            print(f"X={X}  Y={Y}")
            utime.sleep(0.1)

    except OSError:
        if client_address and utime.ticks_diff(utime.ticks_ms(), last_packet_time) > CONNECTION_TIMEOUT_MS:
            print("Connection lost. No data received.")
            client_address = None

    except KeyboardInterrupt:
        stop_all()
        machine.reset()

