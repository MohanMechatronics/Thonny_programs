import machine
import utime

class car:
    def __init__(self):
        self.left_f = machine.Pin(10, machine.Pin.OUT)
        self.left_b = machine.Pin(11, machine.Pin.OUT)
        self.right_f = machine.Pin(9, machine.Pin.OUT)
        self.right_b = machine.Pin(3, machine.Pin.OUT)

        self.stop()

    def forward(self):
        self.left_b.off()
        self.right_b.off()
        self.left_f.on()
        self.right_f.on()
        print("Forward")

    def backward(self):
        self.left_f.off()
        self.right_f.off()
        self.left_b.on()
        self.right_b.on()
        print("Backward")

    def stop(self):
        self.left_f.off()
        self.right_f.off()
        self.left_b.off()
        self.right_b.off()
        print("Stopped")

    def drift_left(self):
        self.left_f.off()
        self.right_b.off()
        self.left_b.on()
        self.right_f.on()
        print("Drift Left")

    def drift_right(self):
        self.left_b.off()
        self.right_f.off()
        self.left_f.on()
        self.right_b.on()
        print("Drift Right")
