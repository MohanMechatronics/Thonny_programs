from machine import Pin, I2C
import time
from i2c_lcd import I2cLcd


# =========================
# I2C SETUP
# =========================
i2c = I2C(0, scl=Pin(14), sda=Pin(13), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# =========================
# ENCODER PINS
# =========================
clk = Pin(25, Pin.IN)
dt  = Pin(33, Pin.IN)

pulse_count = 0


# =========================
# WHEEL PARAMETERS
# =========================
wheel_diameter = 15.5  # cm
pulses_per_revolution = 110

distance_per_pulse = (3.14 * wheel_diameter) / pulses_per_revolution

# =========================
# ENCODER INTERRUPT
# =========================
def encoder_callback(pin):
    global pulse_count
    if dt.value() != clk.value():
        pulse_count += 1
    else:
        pulse_count -= 1

clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_callback)

# =========================
# LCD INIT
# =========================
lcd.clear()
lcd.putstr("Distance wheel")

# =========================
# MAIN LOOP
# =========================
while True:
    distance_cm = pulse_count * distance_per_pulse
    distance_m = distance_cm / 100

    lcd.move_to(0, 1)
    lcd.putstr("{:.2f}m   ".format(distance_m))  # ✅ FIXED

    print("Distance:", distance_cm, "cm |", distance_m, "m")

    time.sleep(0.2)
