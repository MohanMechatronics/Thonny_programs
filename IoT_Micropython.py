# from machine import Pin, I2C, SPI
# import dht
# import time
# from mfrc522 import MFRC522
# 
# # === LCD DRIVER CLASSES (LcdApi and I2cLcd) ===
# # --- DO NOT MODIFY ---
# class LcdApi:
#     def __init__(self, num_lines, num_columns):
#         self.num_lines = num_lines
#         self.num_columns = num_columns
#         self.cursor_x = 0
#         self.cursor_y = 0
# 
#     def clear(self):
#         self.hal_write_command(0x01)
#         time.sleep(0.002)
#         self.move_to(0, 0)
# 
#     def move_to(self, col, row):
#         self.cursor_x = col
#         self.cursor_y = row
#         addr = col + 0x40 * row
#         self.hal_write_command(0x80 | addr)
# 
#     def putstr(self, string):
#         for char in string:
#             self.hal_write_data(ord(char))
# 
# class I2cLcd(LcdApi):
#     LCD_CLR = 0x01
#     LCD_HOME = 0x02
#     LCD_ENTRY_MODE = 0x04
#     LCD_DISPLAY_CTRL = 0x08
#     LCD_CURSOR_SHIFT = 0x10
#     LCD_FUNCTION_SET = 0x20
#     LCD_CGRAM_ADDR = 0x40
#     LCD_DDRAM_ADDR = 0x80
#     LCD_2LINE = 0x08
#     LCD_5x8DOTS = 0x00
#     LCD_4BIT_MODE = 0x00
#     ENABLE = 0x04
#     READ_WRITE = 0x02
#     REGISTER_SELECT = 0x01
# 
#     def __init__(self, i2c, addr, rows, cols):
#         self.i2c = i2c
#         self.addr = addr
#         self.backlight = 0x08
#         self.buffer = bytearray(1)
#         self.rows = rows
#         self.cols = cols
#         super().__init__(rows, cols)
#         self._init_lcd()
# 
#     def _init_lcd(self):
#         time.sleep(0.02)
#         self._write_init_nibble(0x03)
#         time.sleep(0.005)
#         self._write_init_nibble(0x03)
#         time.sleep(0.001)
#         self._write_init_nibble(0x03)
#         self._write_init_nibble(0x02)
#         self.hal_write_command(self.LCD_FUNCTION_SET | self.LCD_2LINE)
#         self.hal_write_command(self.LCD_DISPLAY_CTRL | 0x04)
#         self.clear()
#         self.hal_write_command(self.LCD_ENTRY_MODE | 0x02)
# 
#     def _write_init_nibble(self, nibble):
#         self._write_byte((nibble << 4) | self.backlight)
#         self._pulse_enable((nibble << 4) | self.backlight)
# 
#     def hal_write_command(self, cmd):
#         self._write_byte((cmd & 0xF0) | self.backlight)
#         self._pulse_enable((cmd & 0xF0) | self.backlight)
#         self._write_byte(((cmd << 4) & 0xF0) | self.backlight)
#         self._pulse_enable(((cmd << 4) & 0xF0) | self.backlight)
# 
#     def hal_write_data(self, data):
#         self._write_byte((data & 0xF0) | self.backlight | self.REGISTER_SELECT)
#         self._pulse_enable((data & 0xF0) | self.backlight | self.REGISTER_SELECT)
#         self._write_byte(((data << 4) & 0xF0) | self.backlight | self.REGISTER_SELECT)
#         self._pulse_enable(((data << 4) & 0xF0) | self.backlight | self.REGISTER_SELECT)
# 
#     def _pulse_enable(self, data):
#         self._write_byte(data | self.ENABLE)
#         time.sleep(0.0005)
#         self._write_byte(data & ~self.ENABLE)
#         time.sleep(0.0001)
# 
#     def _write_byte(self, data):
#         self.buffer[0] = data
#         self.i2c.writeto(self.addr, self.buffer)
# 
# # === INITIALIZE LCD ===
# i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
# devices = i2c.scan()
# if not devices:
#     print("No I2C device found!")
#     while True:
#         pass
# 
# lcd_addr = devices[0]
# lcd = I2cLcd(i2c, lcd_addr, 2, 16)
# lcd.clear()
# lcd.putstr("System Starting...")
# time.sleep(2)
# 
# # === INITIALIZE DHT11, PIR, RELAY ===
# dht_sensor = dht.DHT11(Pin(26))
# pir_sensor = Pin(35, Pin.IN)
# relay = Pin(14, Pin.OUT)
# relay.value(0)
# 
# # === INITIALIZE RFID ===
# spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
#           sck=Pin(18), mosi=Pin(19), miso=Pin(25))
# rdr = MFRC522(spi=spi, gpio_rst=Pin(23), gpio_cs=Pin(27))
# 
# # === MAIN LOOP ===
# while True:
#     try:
#         # DHT11 Read
#         dht_sensor.measure()
#         temp = dht_sensor.temperature()
#         hum = dht_sensor.humidity()
# 
#         # PIR Motion
#         motion = pir_sensor.value()
#         relay.value(1 if motion else 0)
# 
#         # RFID Check
#         (status, _) = rdr.request(rdr.REQIDL)
#         if status == rdr.OK:
#             (status, uid) = rdr.anticoll()
#             if status == rdr.OK:
#                 uid_str = "{:02X}:{:02X}:{:02X}:{:02X}".format(*uid[:4])
#                 print("RFID UID:", uid_str)
#                 lcd.clear()
#                 lcd.putstr("RFID: {}".format(uid_str))
#                 time.sleep(2)
#                 lcd.clear()
# 
#         # LCD Display
#         lcd.move_to(0, 0)
#         lcd.putstr("T:{}C H:{}%".format(temp, hum))
#         lcd.move_to(0, 1)
#         lcd.putstr("Motion: {}".format("YES" if motion else "NO"))
# 
#     except Exception as e:
#         print("Error:", e)
#         lcd.clear()
#         lcd.putstr("Sensor Error")
#     
#     time.sleep(1)
#

from rfid_lib import RFID
from utime import sleep
from machine import Pin

uid = RFID(sck=18,mosi=23,miso=25,cs=22)
buzzer = Pin(15, Pin.OUT)

try:
    while True:
        person = uid.read()
        print(person)
        if person == "0xd1707c00" or person == "0x0cd00402" :
            buzzer.on()
            sleep(0.5)
            buzzer.off()
            print(person, "Door open")
            sleep(2)
                             print("close")
        sleep(1)
except KeyboardInterrupt:
    print("Program interrupted. Cleaning up...")
    Pin(18, Pin.IN)
    Pin(19, Pin.IN)
    Pin(22, Pin.IN)
    Pin(23, Pin.IN)
    print("RFID pins reset successfully.")