import network
import asyncio
from machine import Pin, PWM
import ujson

# ─────────────────────────────────────────
#  PIN DEFINITIONS
# ─────────────────────────────────────────
PAN_PIN    = 13
TILT_PIN   = 12
LINK1_PIN  = 32
LINK2_PIN  = 27
LINK3_PIN  = 25
GRIPPER_PIN = 16

# ─────────────────────────────────────────
#  SERVO HELPER
#  MicroPython has no Servo library, so we
#  drive PWM directly.
#  Typical SG90/MG996R: 50 Hz, 0°=0.5 ms, 180°=2.4 ms
# ─────────────────────────────────────────
class Servo:
    def __init__(self, pin_num, freq=50, min_us=500, max_us=2400):
        self.pwm = PWM(Pin(pin_num), freq=freq)
        self.min_us = min_us
        self.max_us = max_us
        self.period_us = 1_000_000 // freq   # 20 000 µs for 50 Hz

    def write(self, angle):
        """Move to angle (0-180 degrees)."""
        angle = max(0, min(180, angle))
        pulse_us = self.min_us + (self.max_us - self.min_us) * angle // 180
        duty = int(pulse_us * 65535 // self.period_us)   # 16-bit duty
        self.pwm.duty_u16(duty)

    def deinit(self):
        self.pwm.deinit()


# ─────────────────────────────────────────
#  SERVO INSTANCES
# ─────────────────────────────────────────
pan_servo     = Servo(PAN_PIN)
tilt_servo    = Servo(TILT_PIN)
link1_servo   = Servo(LINK1_PIN)
link2_servo   = Servo(LINK2_PIN)
link3_servo   = Servo(LINK3_PIN)
gripper_servo = Servo(GRIPPER_PIN)

SERVO_MAP = {
    "Pan":     pan_servo,
    "Tilt":    tilt_servo,
    "Link1":   link1_servo,
    "Link2":   link2_servo,
    "Link3":   link3_servo,
    "Gripper": gripper_servo,
}

def reset_servos():
    """Return arm to safe home position on client disconnect."""
    pan_servo.write(90)
    tilt_servo.write(85)
    link1_servo.write(157)
    link2_servo.write(156)
    link3_servo.write(90)
    gripper_servo.write(90)


# ─────────────────────────────────────────
#  Wi-Fi ACCESS POINT
# ─────────────────────────────────────────
SSID     = "Impact_Makers"
PASSWORD = "12345678"

def start_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=SSID, password=PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
    while not ap.active():
        pass
    print("AP IP address:", ap.ifconfig()[0])


# ─────────────────────────────────────────
#  HTML PAGE  (same UI as the original)
# ─────────────────────────────────────────
HTML_PAGE = """\
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  <style>
    .noselect{-webkit-touch-callout:none;-webkit-user-select:none;-khtml-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}
    .slider{-webkit-appearance:none;width:20%;height:20px;border-radius:5px;background:#d3d3d3;outline:none;opacity:.7;-webkit-transition:.2s;transition:opacity .2s}
    .slider:hover{opacity:1}
    .slider::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:30px;height:30px;border-radius:50%;background:deepskyblue;cursor:pointer}
    .slider::-moz-range-thumb{width:40px;height:80px;border-radius:50%;background:red;cursor:pointer}
    .sliders{width:100%;height:200px;display:flex;flex-direction:column;justify-content:space-evenly}
    @media only screen and (max-width:600px){.slider{width:200px}}
  </style>
</head>
<body class="noselect" align="center" style="background-color:white">
  <h1>IMPACT MAKERS</h1>
  <DIV class="sliders">
  </br></br>
  </br></br>
    <div><span>Base </span><input type="range" min="0" max="180" value="90" class="slider" id="Pan" oninput='sendInput("Pan",this.value)'><span id="PanValue" style="color:red;font-weight:bold;"></span></div></br></br>
    <div><span>Shoulder </span><input type="range" min="0" max="180" value="90" class="slider" id="Tilt" oninput='sendInput("Tilt",this.value)'><span id="TiltValue" style="color:red;font-weight:bold;"></span></div></br></br>
    <div><span>Elbow </span><input type="range" min="0" max="180" value="90" class="slider" id="Link1" oninput='sendInput("Link1",this.value)'><span id="Link1Value" style="color:red;font-weight:bold;"></span></div></br></br>
    <div><span>Pitch </span><input type="range" min="0" max="180" value="90" class="slider" id="Link2" oninput='sendInput("Link2",this.value)'><span id="Link2Value" style="color:red;font-weight:bold;"></span></div></br></br>
    <div><span>Rotate </span><input type="range" min="0" max="180" value="90" class="slider" id="Link3" oninput='sendInput("Link3",this.value)'><span id="Link3Value" style="color:red;font-weight:bold;"></span></div></br></br>
    <div><span>Gripper </span><input type="range" min="0" max="180" value="90" class="slider" id="Gripper" oninput='sendInput("Gripper",this.value)'><span id="GripperValue" style="color:red;font-weight:bold;"></span></div>
  </DIV>
  <script>
    var ws;
    var sliders = ["Pan","Tilt","Link1","Link2","Link3","Gripper"];

    function connect(){
      ws = new WebSocket("ws://" + window.location.hostname + ":81/");
      ws.onopen = function(){
        sliders.forEach(function(id){
          var el = document.getElementById(id);
          sendInput(id, el.value);
        });
      };
      ws.onclose = function(){ setTimeout(connect, 2000); };
      ws.onmessage = function(e){};
    }

    function sendInput(key, value){
      document.getElementById(key+"Value").innerHTML = value;
      if(ws && ws.readyState === 1) ws.send(key + "," + value);
    }

    window.onload = connect;
  </script>
</body>
</html>
"""


# ─────────────────────────────────────────
#  WEBSOCKET SERVER  (port 81)
#  Minimal hand-rolled WS – no library needed
# ─────────────────────────────────────────
import struct
import hashlib
import binascii

WS_MAGIC = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def _ws_handshake_response(key):
    raw = key + WS_MAGIC
    sha = hashlib.sha1(raw.encode()).digest()
    accept = binascii.b2a_base64(sha).strip().decode()
    return (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
    )

async def _ws_recv_frame(reader):
    """Read one WebSocket frame and return the payload string (text frames only)."""
    header = await reader.read(2)
    if len(header) < 2:
        return None
    fin_op = header[0]
    mask_len = header[1]
    masked = mask_len & 0x80
    length = mask_len & 0x7F

    if length == 126:
        ext = await reader.read(2)
        length = struct.unpack(">H", ext)[0]
    elif length == 127:
        ext = await reader.read(8)
        length = struct.unpack(">Q", ext)[0]

    if masked:
        
        masking_key = await reader.read(4)
    payload = await reader.read(length)

    if masked:
        payload = bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))

    opcode = fin_op & 0x0F
    if opcode == 0x8:   # close frame
        return None
    if opcode == 0x1:   # text frame
        return payload.decode()
    return ""           # ping / binary – ignore

async def handle_ws_client(reader, writer):
    print("WebSocket client connected")
    try:
        # ── parse the upgrade request ──────────────────────────────
        ws_key = None
        while True:
            line = await reader.readline()
            line = line.decode().strip()
            if line.lower().startswith("sec-websocket-key:"):
                ws_key = line.split(":", 1)[1].strip()
            if line == "":
                break

        if not ws_key:
            writer.close()
            await writer.wait_closed()
            return

        # ── send 101 handshake ─────────────────────────────────────
        writer.write(_ws_handshake_response(ws_key).encode())
        await writer.drain()

        # ── receive loop ───────────────────────────────────────────
        while True:
            msg = await _ws_recv_frame(reader)
            if msg is None:
                break
            if "," in msg:
                key, val = msg.split(",", 1)
                key = key.strip()
                val = val.strip()
                print(f"Key,Value = [{key},{val}]")
                if key in SERVO_MAP and val.isdigit():
                    SERVO_MAP[key].write(int(val))

    except Exception as e:
        print("WS error:", e)
    finally:
        print("WebSocket client disconnected – resetting servos")
        reset_servos()
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


# ─────────────────────────────────────────
#  HTTP SERVER  (port 80)
# ─────────────────────────────────────────
async def handle_http(reader, writer):
    try:
        request_line = await reader.readline()
        request_line = request_line.decode().strip()
        # drain remaining headers
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b""):
                break

        # Check for WebSocket upgrade request directed at port 80
        # (browser occasionally hits the wrong port – redirect gracefully)
        if request_line.startswith("GET / "):
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(HTML_PAGE)}\r\n"
                "Connection: close\r\n\r\n"
            ) + HTML_PAGE
        else:
            body = "File Not Found"
            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n"
            ) + body

        writer.write(response.encode())
        await writer.drain()
    except Exception as e:
        print("HTTP error:", e)
    finally:
        writer.close()
        await writer.wait_closed()


# ─────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────
async def main():
    start_ap()

    http_server = await asyncio.start_server(handle_http, "0.0.0.0", 80)
    ws_server   = await asyncio.start_server(handle_ws_client, "0.0.0.0", 81)

    print("HTTP server started on port 80")
    print("WebSocket server started on port 81")

    # Keep both servers running forever
    await asyncio.gather(
        http_server.wait_closed(),
        ws_server.wait_closed(),
    )

asyncio.run(main())