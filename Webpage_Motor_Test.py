import network
import socket
from machine import Pin, PWM

# ==== WiFi Access Point Setup ====
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))
ap.config(essid="MotorController", password="12345678")

# ==== PWM Pins (adjust pins as needed) ====
pwm_pins = [PWM(Pin(1), freq=1000),
            PWM(Pin(3), freq=1000),
            PWM(Pin(4), freq=1000),
            PWM(Pin(48), freq=1000)]

for p in pwm_pins:
    p.duty(0)

# ==== States ====
switch_state = [0, 0, 0, 0]   # checkbox linked state
slider_values = [0, 0, 0, 0]  # slider values

# ==== HTML Page ====
html = """<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
<title>Motor Control</title>
<meta name="viewport" content="width=device-width, initial-scale=1.3"> <!-- zoom in by default -->
<style>
body {
  font-family: Arial, sans-serif;
  text-align: center;
  margin: 0;
  padding: 0;
  background: #f4f4f9;
}

h2 {
  margin: 20px 0;
  font-size: 28px;  /* bigger title */
}

.container {
  display: flex;
  justify-content: center;
  gap: 40px;        /* space between sliders */
  margin-top: 30px;
}

.motor {
  text-align: center;
  flex: 1;
}

.motor p {
  font-size: 20px;  /* larger labels */
  margin-bottom: 10px;
}

input[type=range][orient=vertical] {
  writing-mode: bt-lr;
  -webkit-appearance: slider-vertical;
  width: 40px;      /* thicker slider */
  height: 250px;    /* taller slider */
}

label {
  font-size: 18px;  /* larger checkbox text */
}
</style>
<script>
let sliderTimers = {};

function updateSlider(motor, val) {
  if (sliderTimers[motor]) clearTimeout(sliderTimers[motor]);
  sliderTimers[motor] = setTimeout(() => {
    fetch(`/set?motor=${motor}&value=${val}`)
    .then(res => res.text())
    .then(js => eval(js)); // sync other sliders
  }, 80);
}

function toggleSwitch(motor, el) {
  let state = el.checked ? 1 : 0;
  fetch(`/switch?motor=${motor}&state=${state}`);
}
</script>
</head>
<body>
<h2>ESP32 Motor Speed Control</h2>
<div class="container">
  <div class="motor">
    <p>Motor 1</p>
    <input id="s0" type="range" min="0" max="1023" value="0" orient="vertical" oninput="updateSlider(0,this.value)">
    <br><label><input type="checkbox" onchange="toggleSwitch(0,this)"> M1</label>
  </div>
  <div class="motor">
    <p>Motor 2</p>
    <input id="s1" type="range" min="0" max="1023" value="0" orient="vertical" oninput="updateSlider(1,this.value)">
    <br><label><input type="checkbox" onchange="toggleSwitch(1,this)"> M2</label>
  </div>
  <div class="motor">
    <p>Motor 3</p>
    <input id="s2" type="range" min="0" max="1023" value="0" orient="vertical" oninput="updateSlider(2,this.value)">
    <br><label><input type="checkbox" onchange="toggleSwitch(2,this)"> M3</label>
  </div>
  <div class="motor">
    <p>Motor 4</p>
    <input id="s3" type="range" min="0" max="1023" value="0" orient="vertical" oninput="updateSlider(3,this.value)">
    <br><label><input type="checkbox" onchange="toggleSwitch(3,this)"> M4</label>
  </div>
</div>
</body>
</html>

"""

# ==== Apply motor values and build sync JS ====
def apply_motor_values(source_motor, value):
    global slider_values, switch_state
    slider_values[source_motor] = value
    js_updates = []

    linked = [i for i, s in enumerate(switch_state) if s == 1]

    if source_motor in linked:
        for m in linked:
            pwm_pins[m].duty(value)
            slider_values[m] = value
            js_updates.append(f"document.getElementById('s{m}').value={value};")
            print(f"Linked: Motor {m+1} set to {value}")
    else:
        pwm_pins[source_motor].duty(value)
        js_updates.append(f"document.getElementById('s{source_motor}').value={value};")
        print(f"Motor {source_motor+1} set to {value}")

    return "\n".join(js_updates)

# ==== Web Server ====
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print('Web server running at http://192.168.4.1')

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()

    if "GET /set?" in request:
        try:
            params = request.split("GET /set?")[1].split(" ")[0]
            query = {x.split("=")[0]: x.split("=")[1] for x in params.split("&")}
            motor = int(query["motor"])
            value = int(query["value"])
            if 0 <= motor < 4:
                js_code = apply_motor_values(motor, value)
                cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n")
                cl.send(js_code)
        except:
            pass

    elif "GET /switch?" in request:
        try:
            params = request.split("GET /switch?")[1].split(" ")[0]
            query = {x.split("=")[0]: x.split("=")[1] for x in params.split("&")}
            motor = int(query["motor"])
            state = int(query["state"])
            if 0 <= motor < 4:
                switch_state[motor] = state
                print(f"Switch {motor+1} {'ON' if state else 'OFF'}")
        except:
            pass
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK")

    else:
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.sendall(html.encode())   # <-- encode to bytes

    cl.close()
