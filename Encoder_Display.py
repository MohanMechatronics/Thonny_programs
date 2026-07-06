from machine import Pin, SoftI2C
import ssd1306
import time

# =========================
# PIN CONFIGURATION
# =========================
ENC_A = Pin(2, Pin.IN, Pin.PULL_UP)   # CLK
ENC_B = Pin(3, Pin.IN, Pin.PULL_UP)   # DT

i2c  = SoftI2C(sda=Pin(20), scl=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# =========================
# VARIABLES
# =========================
position = 0
last_A = ENC_A.value()

# =========================
# INTERRUPT FUNCTION
# =========================
def encoder_callback(pin):
    global position, last_A

    current_A = ENC_A.value()

    if last_A == 0 and current_A == 1:   # rising edge
        if ENC_B.value() == 0:
            position += 1                # Clockwise
        else:
            position -= 1               # Counter-clockwise

        print("Position:", position)

    last_A = current_A

ENC_A.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_callback)

# =========================
# MAIN LOOP
# =========================
while True:
    oled.fill(0)

    oled.text("ENCODER", 32, 0)
    oled.hline(0, 10, 128, 1)

    # Show position value centred
    val = str(position)
    x = (128 - len(val) * 8) // 2
    oled.text(val, x, 28)

    # Direction label
    if position > 0:
        oled.text(">>> CW", 32, 50)
    elif position < 0:
        oled.text("CCW <<<", 28, 50)
    else:
        oled.text("-- ZERO --", 16, 50)

    oled.show()
    time.sleep(0.1)
