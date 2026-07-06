from machine import Pin
import time

class SoftI2C:
    def __init__(self, scl_pin, sda_pin):
        self.scl = Pin(scl_pin, Pin.OUT)
        self.sda = Pin(sda_pin, Pin.OUT)

        self.scl.value(1)
        self.sda.value(1)

    def delay(self):
        time.sleep_us(5)

    def start(self):
        self.sda.value(1)
        self.scl.value(1)
        self.delay()
        self.sda.value(0)
        self.delay()
        self.scl.value(0)

    def stop(self):
        self.sda.value(0)
        self.scl.value(1)
        self.delay()
        self.sda.value(1)
        self.delay()

    def write_byte(self, byte):
        for i in range(8):
            self.sda.value((byte >> 7) & 1)
            self.scl.value(1)
            self.delay()
            self.scl.value(0)
            byte <<= 1

        self.sda.init(Pin.IN)
        self.scl.value(1)
        self.delay()
        ack = self.sda.value()
        self.scl.value(0)
        self.sda.init(Pin.OUT)

        return ack == 0