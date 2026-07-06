import machine
import utime

class servo:
    def __init__(self):
        self.led = machine.PWM(machine.Pin(4))
        self.led.freq(50)

    def angle(self, angle):
        formula = int(2000000* angle/180)+500000

        self.led.duty_ns(formula)

        print(formula, " ns")


