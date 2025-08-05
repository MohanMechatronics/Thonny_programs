from machine import Pin, SPI
import mfrc522
from time import sleep

# SPI and RFID setup
spi = SPI(1, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(22), mosi=Pin(32), miso=Pin(19))

# Create MFRC522 object — RST pin is not used here
rdr = mfrc522.MFRC522(spi, Pin(5))

print("Place RFID card near the reader...")

while True:
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            uid_str = "{:02X}{:02X}{:02X}{:02X}".format(*raw_uid)
            print("Card detected! UID:", uid_str)
            sleep(1)
