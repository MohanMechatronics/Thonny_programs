import network
import socket
import time
import esp32
import camera
import _thread
import uwebsockets
import ujson
import umsgpack_ws

SSID = "LMESMP"
PASSWORD = "12345678"
WS_URL = "ws://192.168.4.1:81/"   # <-- FIXED: must NOT be renamed or removed


camera_enabled = False
ws = None
ip_addr = None


# ---------------- WIFI ----------------
def connect_wifi():
    global ip_addr
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting WiFi:", SSID)
    while not wlan.isconnected():
        time.sleep(0.5)
        print(".", end="")

    ip_addr = wlan.ifconfig()[0]
    print("\nConnected! IP:", ip_addr)
    return ip_addr


# -------------- CAMERA ----------------
def start_camera():
    global camera_enabled
    if camera_enabled:
        return

    camera.init()
    camera_enabled = True
    print("Camera STARTED")


def stop_camera():
    global camera_enabled
    if not camera_enabled:
        return

    camera.deinit()
    camera_enabled = False
    print("Camera STOPPED")


# ---------- STREAM SERVER (HTTP) ----------
def start_stream_server(ip):
    addr = (ip, 80)
    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print("Stream: http://%s/stream" % ip)

    while True:
        cl, addr = s.accept()
        req = cl.recv(1024)

        if b"GET /stream" in req:
            cl.send(b"HTTP/1.1 200 OK\r\n")
            cl.send(b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n")

            while camera_enabled:
                try:
                    frame = camera.capture()
                    cl.send(b"--frame\r\n")
                    cl.send(b"Content-Type: image/jpeg\r\n\r\n")
                    cl.send(frame)
                    cl.send(b"\r\n")
                except:
                    break

        cl.close()


# ---------- WEBSOCKET CLIENT ----------
def connect_websocket():
    global ws
    global ip_addr
    try:
        print("Connecting to WS server...")
        ws = uwebsockets.connect(WS_URL)
        print("WebSocket connected!")

        # Send IP to server
        time.sleep(1)
        print(ip_addr)
        #msg = ujson.dumps({"msg": "ipaddr", "ip": ip_addr})
        #ws.send(msg.encode())    # force binary
        umsgpack_ws.send_msgpack(ws,{"msg": "ipaddr", "ip": ip_addr})


    except Exception as e:
        print("WS error:", e)


def ws_listen_loop():
    global ws
    while True:
        try:
            msg = ws.recv()
            if msg:
                print("WS RX:", msg)
                handle_command(msg)
        except:
            pass

        time.sleep(0.05)


# ----------- PROCESS JSON COMMANDS ----------
def handle_command(raw):
    try:
        cmd = ujson.loads(raw)
        print(raw)
    except:
        print("Invalid JSON")
        return

    if cmd.get("target") == "camera":
        state = cmd.get("state")

        if state == "start":
            start_camera()
            umspack_ws.send_msgpack(ws,{"status":"camera_started"})

        elif state == "stop":
            stop_camera()
            umspack_ws.send_msgpack(ws,{"status":"camera_stopped"})


# ---------------- MAIN ----------------
ip = connect_wifi()
connect_websocket()

# Background WebSocket listener
_thread.start_new_thread(ws_listen_loop, ())

# Start camera initially
start_camera()

# Run HTTP stream server
start_stream_server(ip)
