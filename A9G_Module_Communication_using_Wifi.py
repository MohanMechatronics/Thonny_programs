from machine import UART
import network
import socket
import time
import ure

# ==================================================
# UART CONFIG (A9G)
# ==================================================
gsm = UART(1, baudrate=115200, tx=17, rx=16, timeout=1000)

# ==================================================
# WIFI ACCESS POINT
# ==================================================
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="Iam_Disguised", password="gunasree")

print("Access Point Started")
print("Connect to WiFi: ESP32_GSM")
print("Password: 12345678")
print("IP:", ap.ifconfig()[0])

# ==================================================
# HTML PAGE
# ==================================================
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 GSM Terminal</title>
</head>
<body>
    <h2>ESP32 A9G AT Command Terminal</h2>
    <form action="/" method="get">
        <input type="text" name="cmd" placeholder="Enter AT Command" style="width:300px">
        <input type="submit" value="Send">
    </form>
    <pre>{}</pre>
</body>
</html>
"""

# ==================================================
# URL DECODE FUNCTION (🔥 FIX)
# ==================================================
def url_decode(s):
    s = s.replace('+', ' ')
    return ure.sub('%([0-9A-Fa-f]{2})',
                   lambda m: chr(int(m.group(1), 16)),
                   s)

# ==================================================
# SEND AT COMMAND
# ==================================================
def send_at(cmd):
    print("Sending:", cmd)
    gsm.write((cmd + "\r\n").encode())
    time.sleep(2)

    resp = b""
    while gsm.any():
        resp += gsm.read()

    result = resp.decode("utf-8", "ignore")
    print("Response:", result)

    return result

# ==================================================
# SOCKET SERVER
# ==================================================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)

print("Web server running...")

while True:
    cl, addr = server.accept()
    print("Client connected:", addr)

    request = cl.recv(1024).decode()
    
    cmd = ""
    response = ""

    # ==================================================
    # PARSE & DECODE COMMAND
    # ==================================================
    if "GET /?cmd=" in request:
        try:
            raw_cmd = request.split("GET /?cmd=")[1].split(" ")[0]
            cmd = url_decode(raw_cmd)   # 🔥 DECODE FIX

            print("Decoded Command:", cmd)

            response = send_at(cmd)
        except Exception as e:
            response = "Error: " + str(e)

    # ==================================================
    # SEND WEB PAGE
    # ==================================================
    page = html.format(response)

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(page)
    cl.close()