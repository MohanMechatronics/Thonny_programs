from machine import Pin, I2C
from time import ticks_ms, ticks_diff
from lcd_api import LcdApi
from machine_i2c_lcd import I2cLcd

# === LCD SETUP ===
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
devices = i2c.scan()
if not devices:
    print("No I2C LCD found.")
    while True:
        pass

lcd = I2cLcd(i2c, devices[0], 2, 16)
lcd.clear()
lcd.putstr("LCD Counter:")

# === COUNTER TIMER ===
count = 0
counter_timer = ticks_ms()

# === LOOP ===
while True:
    now = ticks_ms()

    # --- LCD COUNTER UPDATE ---
    if ticks_diff(now, counter_timer) >= 1000:
        counter_timer = now
        count += 1
        lcd.move_to(0, 1)
        lcd.putstr("Count: {:<5}".format(count))
