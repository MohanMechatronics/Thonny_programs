from machine import Pin, PWM, I2C
from time import ticks_ms, ticks_diff, sleep_ms
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
lcd.putstr("Servo Counter:")

# === SERVO & LED SETUP ===
servo1 = PWM(Pin(21), freq=50)
servo2 = PWM(Pin(25), freq=50)
led = Pin(16, Pin.OUT)

def set_servo_angle(angle):
    duty = int((angle / 180 * 102) + 26)  # approx: 0° -> 26, 180° -> 128
    servo1.duty(duty)
    servo2.duty(duty)

# === TIMER AND ANGLE SETUP ===
angle = 0
direction = 1
angle_step_time = 200  # milliseconds between angle updates
angle_timer = ticks_ms()

# === COUNTER TIMER ===
count = 0
counter_timer = ticks_ms()

# === LOOP ===
while True:
    now = ticks_ms()

    # --- SERVO SWEEP ---
    if ticks_diff(now, angle_timer) >= angle_step_time:
        angle_timer = now
        set_servo_angle(angle)
        angle += direction
        if angle >= 180:
            angle = 180
            direction = -1
        elif angle <= 0:
            angle = 0
            direction = 1
        led.on()

    # --- LCD COUNTER UPDATE ---
    if ticks_diff(now, counter_timer) >= 1000:
        counter_timer = now
        count += 1
        lcd.move_to(0, 1)
        lcd.putstr("Count: {:<5}".format(count))
