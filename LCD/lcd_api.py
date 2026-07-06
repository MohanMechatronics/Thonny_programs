import time

class LcdApi:
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_FUNCTION = 0x20
    LCD_FUNCTION_2LINES = 0x08
    LCD_DDRAM = 0x80

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)

    def move_to(self, col, row):
        addr = col + (0x40 if row else 0)
        self.hal_write_command(self.LCD_DDRAM | addr)

    def putstr(self, string):
        for char in string:
            self.hal_write_data(ord(char))
