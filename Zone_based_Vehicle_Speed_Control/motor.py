import machine
import utime

class car:
    def __init__(self):
        self.enable_A = machine.Pin(21, machine.Pin.OUT)
        self.enable_B = machine.Pin(25, machine.Pin.OUT)

        self.left_f = machine.Pin(18, machine.Pin.OUT)
        self.left_b = machine.Pin(19, machine.Pin.OUT)
        self.right_f = machine.Pin(23, machine.Pin.OUT)
        self.right_b = machine.Pin(22, machine.Pin.OUT)

        self.stop()

    def forward(self):
        self.enable_A.on()
        self.enable_B.on()

        self.left_b.off()
        self.right_b.off()
        self.left_f.on()
        self.right_f.on()
        print("Forward")

    def backward(self):
        self.enable_A.on()
        self.enable_B.on()

        self.left_f.off()
        self.right_f.off()
        self.left_b.on()
        self.right_b.on()
        print("Backward")

    def stop(self):
        self.enable_A.off()
        self.enable_B.off()

        self.left_f.off()
        self.right_f.off()
        self.left_b.off()
        self.right_b.off()
        print("Stopped")

    def drift_left(self):
        self.enable_A.on()
        self.enable_B.on()

        self.left_f.off()
        self.right_b.off()
        self.left_b.on()
        self.right_f.on()
        print("Drift Left")

    def drift_right(self):
        self.enable_A.on()
        self.enable_B.on()

        self.left_b.off()
        self.right_f.off()
        self.left_f.on()
        self.right_b.on()
        print("Drift Right")
