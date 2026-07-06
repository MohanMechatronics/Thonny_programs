from machine import Pin, SoftI2C
import network
import espnow
import ssd1306
import time

# ================= I2C OLED (REFERENCE STYLE) =================
SDA_PIN = 13
SCL_PIN = 14

i2c = SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)

devices = i2c.scan()
print("I2C devices:", devices)

if not devices:
    raise OSError("OLED not detected. Check wiring!")

oled_addr = devices[0]   # auto-pick detected address
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=oled_addr)

def update_oled(line1, line2):
    oled.fill(0)
    oled.text(line1, 0, 15)
    oled.text(line2, 0, 35)
    oled.show()

# ================= BUTTON PINS =================
button1 = Pin(25, Pin.IN, Pin.PULL_DOWN)   # HIGHWAY
button2 = Pin(26, Pin.IN, Pin.PULL_DOWN)   # HOSPITAL
button3 = Pin(27, Pin.IN, Pin.PULL_DOWN)   # SCHOOL

# ================= WIFI + ESPNOW INIT =================
sta = network.WLAN(network.STA_IF)
sta.active(True)

e = espnow.ESPNow()
e.active(True)

# SLAVE MAC ADDRESS (change if needed)
peer = b'L\xc3\x82\xcfP\x1c'
e.add_peer(peer)

# ================= START SCREEN =================
oled.fill(0)
oled.text("ESP32 ESP-NOW", 0, 0)
oled.text("OLED READY", 0, 20)
oled.text("Addr: {}".format(hex(oled_addr)), 0, 40)
oled.show()
time.sleep(2)

update_oled("Ready...", "Press button")

# ================= MAIN LOOP =================
while True:

    if button1.value() == 1:
        e.send(peer, b'1')
        update_oled("HIGHWAY", "Speed 100km/h")

    elif button2.value() == 1:
        e.send(peer, b'3')
        update_oled("HOSPITAL ZONE", "Speed 40km/h")

    elif button3.value() == 1:
        e.send(peer, b'2')
        update_oled("SCHOOL ZONE", "Speed 20km/h")

    else:
        e.send(peer, b'0')
        update_oled("NORMAL ZONE", "Speed 50km/h")

    time.sleep(0.2)