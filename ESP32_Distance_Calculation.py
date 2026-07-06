from machine import Pin, I2C, time_pulse_us
import time
import lcd_api
import i2c_lcd

# =========================
# I2C LCD SETUP
# =========================
I2C_ADDR = 0x27  # Change if needed
i2c = I2C(0, scl=Pin(14), sda=Pin(13), freq=400000)
lcd = i2c_lcd.I2cLcd(i2c, I2C_ADDR, 2, 16)

# =========================
# ULTRASONIC SETUP
# =========================
trigger = Pin(26, Pin.OUT)
echo = Pin(27, Pin.IN)

def measure_distance():
    # Ensure trigger low
    trigger.off()
    time.sleep_us(2)

    # Send 10us pulse
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    # Measure pulse duration
    try:
        pulse_time = time_pulse_us(echo, 1, 30000)  # 30ms timeout
    except OSError:
        return None

    # Distance calculation (cm)
    distance = (pulse_time * 0.0343) / 2
    return distance

# =========================
# START DISPLAY
# =========================
lcd.clear()
lcd.putstr("Ultrasonic Ready")
time.sleep(2)

# =========================
# MAIN LOOP
# =========================
while True:
    dist = measure_distance()

    lcd.clear()
    lcd.putstr("Distance:")

    lcd.move_to(0, 1)

    if dist is None:
        lcd.putstr("Out of range")
    else:
        lcd.putstr("{:.2f} cm".format(dist))

    time.sleep(0.5)
