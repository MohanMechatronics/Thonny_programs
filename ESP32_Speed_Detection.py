from machine import Pin, I2C
import time
import lcd_api
import i2c_lcd

# ===== Distance between sensors in meters =====

DISTANCE = 0.10   # 10 cm

# ===== IR Sensors =====

ir1 = Pin(27, Pin.IN)
ir2 = Pin(26, Pin.IN)

# ===== I2C LCD Setup =====
i2c = I2C(0, scl=Pin(14), sda=Pin(13), freq=400000)

lcd_addr = i2c.scan()[0]
lcd = i2c_lcd.I2cLcd(i2c, lcd_addr, 2, 16)

lcd.clear()
lcd.putstr("Speed Meter")
time.sleep(2)
lcd.clear()

while True:
    
    # Wait for first sensor trigger
    if ir1.value() == 0:   # object detected
        start_time = time.ticks_us()
        
        # Wait for second sensor trigger
        while ir2.value() == 1:
            pass
        
        end_time = time.ticks_us()
        
        # Time difference in seconds
        time_taken = time.ticks_diff(end_time, start_time) / 1000000
        
        if time_taken > 0:
            speed = DISTANCE / time_taken   # m/s
            
            lcd.clear()
            lcd.putstr("Speed:")
            lcd.move_to(0,1)
            lcd.putstr("{:.2f} m/s".format(speed))
            
            print("Speed:", speed, "m/s")
        
        time.sleep(1)
