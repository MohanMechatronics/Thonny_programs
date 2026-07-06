"""
ESP32-C3 Device Finder - MicroPython
ACCESS POINT MODE ONLY
- Device creates its own WiFi hotspot
- Connect your phone/laptop to that hotspot
- Open http://192.168.4.1/ in your browser
"""

import network
import socket
import time
import json
from machine import Pin, PWM

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

AP_SSID      = "ROCKY_PROJECT"
AP_PASSWORD  = "12345678"       # min 8 chars; set "" for open (no password)

PIN_LED      = 8                # Built-in LED on ESP32-C3; change if needed
PIN_BUZZER   = 4                # PWM-capable GPIO for passive buzzer

# Emergency alert tone configuration
HIGH_TONE       = 2000          # High pitch (Hz)
LOW_TONE        = 1000          # Low pitch (Hz)
BEEP_ON         = 150           # Tone ON duration (ms)
BEEP_OFF        = 80            # Gap between beeps (ms)
BURST_GAP       = 400           # Gap between bursts (ms)
CYCLE_GAP       = 800           # Gap between full alert cycles (ms)
BEEPS_PER_BURST = 3             # Number of beeps per burst

FIND_SECS    = 15                # How long "Find My Device" runs

# ─────────────────────────────────────────────
# HARDWARE
# ─────────────────────────────────────────────

led    = Pin(PIN_LED, Pin.OUT)
buzzer = PWM(Pin(PIN_BUZZER), freq=HIGH_TONE, duty=0)

def led_on():  led.value(0)
def led_off(): led.value(1)

# ── Buzzer helpers ──────────────────────────

def tone_on(freq, duty=512):
    buzzer.freq(freq)
    buzzer.duty(duty)

def tone_off():
    buzzer.duty(0)

def buzz_on():
    tone_on(HIGH_TONE)

def buzz_off():
    tone_off()

def beep(freq, duration_ms, duty=512):
    tone_on(freq, duty)
    time.sleep_ms(duration_ms)
    tone_off()

def emergency_burst():
    for _ in range(BEEPS_PER_BURST):
        beep(HIGH_TONE, BEEP_ON)
        time.sleep_ms(BEEP_OFF)
        beep(LOW_TONE, BEEP_ON)
        time.sleep_ms(BEEP_OFF)

def wail_effect(duration_ms=600, steps=30):
    step_time = duration_ms // (steps * 2)
    for i in range(steps):
        freq = LOW_TONE + int((HIGH_TONE - LOW_TONE) * i / steps)
        tone_on(freq)
        time.sleep_ms(step_time)
    for i in range(steps, 0, -1):
        freq = LOW_TONE + int((HIGH_TONE - LOW_TONE) * i / steps)
        tone_on(freq)
        time.sleep_ms(step_time)
    tone_off()

def find_beep(secs=FIND_SECS):
    end = time.time() + secs
    while time.time() < end:
        led_on()
        emergency_burst()
        led_off()
        time.sleep_ms(BURST_GAP)
        if time.time() >= end:
            break
        led_on()
        wail_effect(duration_ms=700, steps=40)
        led_off()
        time.sleep_ms(BURST_GAP)
        if time.time() >= end:
            break
        led_on()
        emergency_burst()
        led_off()
        time.sleep_ms(CYCLE_GAP)
    tone_off()
    led_off()

# ─────────────────────────────────────────────
# ACCESS POINT
# ─────────────────────────────────────────────

def start_ap():
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    if AP_PASSWORD:
        ap.config(essid=AP_SSID, password=AP_PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)
    else:
        ap.config(essid=AP_SSID, authmode=network.AUTH_OPEN)
    while not ap.active():
        time.sleep(0.1)
    ip = ap.ifconfig()[0]
    print(f"AP '{AP_SSID}' started | IP: {ip}")
    return ip

# ─────────────────────────────────────────────
# HTML PAGE  (buttons use fetch — zero page reload)
# ─────────────────────────────────────────────

HTML = """\
HTTP/1.0 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ESP32 Device Finder</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@600;700&display=swap');
  :root{--bg:#0a0f1e;--panel:#0d1a2e;--border:#1a3a5c;--accent:#00e5ff;--accent2:#ff6b35;--green:#39ff14;--text:#cce8f4;--dim:#4a7a99}
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    background:var(--bg);color:var(--text);font-family:'Share Tech Mono',monospace;
    min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px;
    background-image:
      radial-gradient(ellipse at 20% 20%,rgba(0,229,255,.06) 0%,transparent 60%),
      radial-gradient(ellipse at 80% 80%,rgba(255,107,53,.06) 0%,transparent 60%),
      repeating-linear-gradient(0deg,transparent,transparent 40px,rgba(0,229,255,.03) 40px,rgba(0,229,255,.03) 41px),
      repeating-linear-gradient(90deg,transparent,transparent 40px,rgba(0,229,255,.03) 40px,rgba(0,229,255,.03) 41px);
  }
  .card{
    background:var(--panel);border:1px solid var(--border);border-radius:16px;
    padding:40px 36px;max-width:420px;width:100%;
    box-shadow:0 0 60px rgba(0,229,255,.08),inset 0 1px 0 rgba(255,255,255,.05);
    position:relative;overflow:hidden;
  }
  .card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent),transparent)}
  .badge{display:inline-block;background:rgba(0,229,255,.1);border:1px solid var(--accent);color:var(--accent);font-size:10px;letter-spacing:3px;padding:4px 12px;border-radius:20px;text-transform:uppercase;margin-bottom:16px}
  h1{font-family:'Rajdhani',sans-serif;font-size:2rem;font-weight:700;color:#fff;line-height:1.1;margin-bottom:6px}
  h1 span{color:var(--accent)}
  .subtitle{color:var(--dim);font-size:12px;letter-spacing:1px;margin-bottom:24px}
  .ap-info{background:rgba(0,229,255,.05);border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin-bottom:24px;font-size:11px;color:var(--dim);line-height:1.9}
  .ap-info span{color:var(--accent)}
  .status-row{display:flex;gap:12px;margin-bottom:28px}
  .status-box{flex:1;background:rgba(0,0,0,.3);border:1px solid var(--border);border-radius:10px;padding:14px;text-align:center}
  .status-box .label{font-size:10px;color:var(--dim);letter-spacing:2px;margin-bottom:8px}
  .dot{width:14px;height:14px;border-radius:50%;margin:0 auto 6px;background:var(--dim);transition:background .3s,box-shadow .3s}
  .dot.on  {background:var(--green);  box-shadow:0 0 12px var(--green)}
  .dot.buzz{background:var(--accent2);box-shadow:0 0 12px var(--accent2)}
  .status-val{font-size:11px;color:var(--text)}
  .btn-group{display:flex;flex-direction:column;gap:12px}
  .btn{display:block;width:100%;padding:16px;border:none;border-radius:10px;font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;cursor:pointer;text-align:center;transition:transform .1s,box-shadow .2s,opacity .2s}
  .btn:active{transform:scale(.97)}
  .btn.busy{opacity:.45;pointer-events:none}
  .btn-find{background:linear-gradient(135deg,#ff6b35,#ff3500);color:#fff;box-shadow:0 4px 20px rgba(255,107,53,.4)}
  .btn-find:hover{box-shadow:0 6px 30px rgba(255,107,53,.6)}
  .btn-led-on {background:linear-gradient(135deg,#1a3a5c,#0d2240);color:var(--green);border:1px solid var(--green);box-shadow:0 0 16px rgba(57,255,20,.2)}
  .btn-led-on:hover{box-shadow:0 0 28px rgba(57,255,20,.4)}
  .btn-led-off{background:rgba(0,0,0,.3);color:var(--dim);border:1px solid var(--border)}
  .btn-buzz-on {background:linear-gradient(135deg,#1a1a3a,#0d0d2a);color:var(--accent);border:1px solid var(--accent);box-shadow:0 0 16px rgba(0,229,255,.2)}
  .btn-buzz-on:hover{box-shadow:0 0 28px rgba(0,229,255,.4)}
  .btn-buzz-off{background:rgba(0,0,0,.3);color:var(--dim);border:1px solid var(--border)}
  .divider{height:1px;background:var(--border);margin:4px 0}
  .footer{margin-top:28px;text-align:center;font-size:10px;color:var(--dim);letter-spacing:1px}
  #toast{
    position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(60px);
    background:rgba(0,229,255,.12);border:1px solid var(--accent);color:var(--accent);
    font-size:11px;letter-spacing:2px;padding:10px 22px;border-radius:20px;
    opacity:0;transition:opacity .3s,transform .3s;pointer-events:none;white-space:nowrap
  }
  #toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>
<div class="card">
  <div class="badge">&#x25C6; WELCOME &#x25C6;</div>
  <h1>Device <span>Finder</span></h1>
  <p class="subtitle">LOCATE &bull; SIGNAL &bull; CONTROL</p>

  <div class="ap-info">
    &#x1F4F6; Hotspot &nbsp;: <span>ROCKY_PROJECT</span><br>
    &#x1F511; Password : <span>12345678</span><br>
    &#x1F4CD; Address &nbsp;: <span>http://192.168.4.1/</span>
  </div>

  <div class="status-row">
    <div class="status-box">
      <div class="label">LED</div>
      <div class="dot" id="led-dot"></div>
      <div class="status-val" id="led-txt">OFF</div>
    </div>
    <div class="status-box">
      <div class="label">BUZZER</div>
      <div class="dot" id="buzz-dot"></div>
      <div class="status-val" id="buzz-txt">OFF</div>
    </div>
  </div>

  <div class="btn-group">
    <button class="btn btn-find"     onclick="cmd('/find',    this)">&#x1F6F0; FIND MY DEVICE</button>
    <div class="divider"></div>
    <button class="btn btn-led-on"   onclick="cmd('/led/on',  this)">&#x25CF; LED ON</button>
    <button class="btn btn-led-off"  onclick="cmd('/led/off', this)">&#x25CB; LED OFF</button>
    <div class="divider"></div>
    <button class="btn btn-buzz-on"  onclick="cmd('/buzz/on', this)">&#x266B; BUZZER ON</button>
    <button class="btn btn-buzz-off" onclick="cmd('/buzz/off',this)">&#x25A0; BUZZER OFF</button>
  </div>

  <div class="footer">HOPE &bull; YOU FOUND &bull; YOUR DEVICE</div>
</div>

<div id="toast"></div>

<script>
  function applyState(data) {
    document.getElementById('led-dot').className  = 'dot' + (data.led  ? ' on'   : '');
    document.getElementById('buzz-dot').className = 'dot' + (data.buzz ? ' buzz' : '');
    document.getElementById('led-txt').textContent  = data.led  ? 'ON' : 'OFF';
    document.getElementById('buzz-txt').textContent = data.buzz ? 'ON' : 'OFF';
  }

  var toastTimer;
  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function(){ t.classList.remove('show'); }, 2200);
  }

  function cmd(path, btn) {
    btn.classList.add('busy');
    if (path === '/find') toast('SCANNING\u2026');

    fetch(path)
      .then(function(r){ return r.json(); })
      .then(function(data){
        applyState(data);
        if (path === '/find') toast('ALERT DONE');
      })
      .catch(function(){ toast('ERROR \u2014 retry'); })
      .finally(function(){ btn.classList.remove('busy'); });
  }

  // Sync status dots on first load
  fetch('/state')
    .then(function(r){ return r.json(); })
    .then(applyState)
    .catch(function(){});
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────
# RESPONSE HELPERS
# ─────────────────────────────────────────────

def json_resp(led_state, buzz_state):
    body = json.dumps({"led": led_state, "buzz": buzz_state})
    return (
        "HTTP/1.0 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Content-Length: " + str(len(body)) + "\r\n"
        "\r\n" + body
    )

# ─────────────────────────────────────────────
# WEB SERVER
# ─────────────────────────────────────────────

def start_server(ip):
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print(f"Server ready -> http://{ip}/")

    led_state  = False
    buzz_state = False

    while True:
        try:
            conn, _ = s.accept()
            req  = conn.recv(1024).decode("utf-8", "ignore")
            path = req.split(" ")[1] if " " in req else "/"

            if path == "/find":
                # Reply with JSON first so fetch() resolves immediately,
                # then run the blocking alert sequence
                conn.send(json_resp(False, False))
                conn.close()
                find_beep(FIND_SECS)
                led_state  = False
                buzz_state = False
                continue

            elif path == "/led/on":
                led_on();  led_state = True
            elif path == "/led/off":
                led_off(); led_state = False
            elif path == "/buzz/on":
                buzz_on();  buzz_state = True
            elif path == "/buzz/off":
                buzz_off(); buzz_state = False

            # /state or any other path just returns current state
            # (root "/" serves HTML)
            if path == "/":
                conn.send(HTML)
            else:
                conn.send(json_resp(led_state, buzz_state))

            conn.close()

        except OSError as e:
            print("Socket error:", e)
            try: conn.close()
            except: pass

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    for _ in range(3):
        led_on(); time.sleep(0.1); led_off(); time.sleep(0.1)

    ip = start_ap()
    print(f"\n1. Connect your device to WiFi: '{AP_SSID}'  pw: '{AP_PASSWORD}'")
    print(f"2. Open browser -> http://{ip}/\n")
    start_server(ip)

main()

