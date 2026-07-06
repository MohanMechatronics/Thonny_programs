from lcd_api import LcdApi
from time import sleep_ms

# PCF8574 pin mapping
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E  = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

class I2cLcd(LcdApi):
    def __init__(self, i2c, addr, num_lines, num_columns):
        self.i2c = i2c
        self.addr = addr
        self.backlight = 1
        sleep_ms(20)

        self.hal_write_init_nibble(0x03)
        sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        sleep_ms(1)
        self.hal_write_init_nibble(0x02)

        LcdApi.__init__(self, num_lines, num_columns)

        self.hal_write_command(0x28)
        self.hal_write_command(0x0C)
        self.hal_write_command(0x06)
        self.clear()

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << SHIFT_DATA)
        self.i2c.writeto(self.addr, bytes([byte | self.backlight << SHIFT_BACKLIGHT]))
        self.pulse_enable(byte)

    def hal_write_command(self, cmd):
        self.hal_write(cmd, 0)

    def hal_write_data(self, data):
        self.hal_write(data, MASK_RS)

    def hal_write(self, data, mode):
        high = (data >> 4) & 0x0F
        low = data & 0x0F

        self.write4bits(high, mode)
        self.write4bits(low, mode)

    def write4bits(self, nibble, mode):
        byte = (nibble << SHIFT_DATA) | mode
        self.i2c.writeto(self.addr, bytes([byte | (self.backlight << SHIFT_BACKLIGHT)]))
        self.pulse_enable(byte)

    def pulse_enable(self, data):
        self.i2c.writeto(self.addr, bytes([data | MASK_E | (self.backlight << SHIFT_BACKLIGHT)]))
        sleep_ms(1)
        self.i2c.writeto(self.addr, bytes([data | (self.backlight << SHIFT_BACKLIGHT)]))
        sleep_ms(1)