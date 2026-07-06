import network
import socket
from machine import Pin

# LED
led = Pin(16, Pin.OUT)

# Create WiFi Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)

# Set SSID and Password
ap.config(essid='CHITTI_LED', password='12345678')

# Static IP
ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '8.8.8.8'))

print("AP Started")
print("IP Address:", ap.ifconfig()[0])

# HTML Page
html = """
<!DOCTYPE html>
<html>
<head>
<title>CHITTI LED Control</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{
    font-family:Arial;
    text-align:center;
    margin-top:50px;
}
button{
    width:180px;
    height:60px;
    font-size:22px;
    border:none;
    border-radius:10px;
    margin:10px;
    color:white;
}
.on{background:green;}
.off{background:red;}
</style>
</head>
<body>
<h1>CHITTI LED Controller</h1>
<a href="/on"><button class="on">LED ON</button></a>
<a href="/off"><button class="off">LED OFF</button></a>
</body>
</html>
"""

# Web Server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

server = socket.socket()
server.bind(addr)
server.listen(1)

print("Web Server Running")

while True:
    client, addr = server.accept()

    request = client.recv(1024).decode()

    if "GET /on" in request:
        led.value(1)

    elif "GET /off" in request:
        led.value(0)

    client.send("HTTP/1.1 200 OK\r\n")
    client.send("Content-Type: text/html\r\n")
    client.send("Connection: close\r\n\r\n")
    client.sendall(html)

    client.close()