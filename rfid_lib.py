from mfrc522 import MFRC522
from machine import SoftSPI, Pin

class RFID():
    def __init__(self,sck=18,mosi=32,miso=19,cs=21):
        spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
        spi.init()
        self.rdr = MFRC522(spi=spi, gpioCs=cs)
#         print("Place card")
    def read(self):
        (stat, tag_type) = self.rdr.request(self.rdr.REQIDL)
        if stat == self.rdr.OK:
            (stat, raw_uid) = self.rdr.anticoll()
            if stat == self.rdr.OK:
                card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                return card_id

while True:
    print(RFID().read())