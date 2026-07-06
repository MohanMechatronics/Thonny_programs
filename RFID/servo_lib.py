from machine import Pin, PWM
from utime import sleep

class Servo:
    def __init__(self, pin):
        pwm = PWM(Pin(pin), freq=50)
        self.set_angle = lambda a: pwm.duty_ns(int((2000000 * (min(180, max(0, a)) / 180)) + 500000))
        self.d=0
            
    def servo_open(self):
        while self.d>0:
            self.d = self.d-1 if self.d>0 else self.d
            self.set_angle(self.d)
            sleep(0.01)
            
    def servo_close(self):
        while self.d<90:
            self.d = self.d+1 if self.d<90 else self.d
            self.set_angle(self.d)
            sleep(0.01)
            
    def lock(self):
        while self.d>0:
            self.d = self.d-1 if self.d>0 else self.d
            self.set_angle(self.d)
            sleep(0.01)
            
    def unlock(self):
        while self.d<90:
            self.d = self.d+1 if self.d<90 else self.d
            self.set_angle(self.d)
            sleep(0.01)