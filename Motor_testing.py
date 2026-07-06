import machine
import utime

class RMC:
    def __init__(self):
        self.Left_en = machine.Pin(21, machine.Pin.OUT)
        self.Right_en = machine.Pin(25, machine.Pin.OUT)
        self.Left_en.on()
        self.Right_en.on()
        self.Left_F = machine.Pin(19, machine.Pin.OUT)
        self.Left_B = machine.Pin(18, machine.Pin.OUT)
        self.Right_F = machine.Pin(22, machine.Pin.OUT)
        self.Right_B = machine.Pin(23, machine.Pin.OUT)

    def forward(self):
        print("forward")
        self.Left_F.on()
        self.Right_F.on()
        self.Left_B.off()
        self.Right_B.off()

    def backward(self):
        print("backward")
        self.Left_F.off()
        self.Right_F.off()
        self.Left_B.on()
        self.Right_B.on()

    def left(self):
        print("left")
        self.Left_F.off()
        self.Right_F.on()
        self.Left_B.off()
        self.Right_B.off()

    def right(self):
        print("right")
        self.Left_F.on()
        self.Right_F.off()
        self.Left_B.off()
        self.Right_B.off()

    def drift_left(self):
        print("drift left")
        self.Left_F.off()
        self.Right_F.on()
        self.Left_B.on()
        self.Right_B.off()

    def drift_right(self):
        print("drift right")
        self.Left_F.on()
        self.Right_F.off()
        self.Left_B.off()
        self.Right_B.on()

    def stop(self):
        print("stop")
        self.Left_F.off()
        self.Right_F.off()
        self.Left_B.off()
        self.Right_B.off()
        utime.sleep(0.1)

# Run the motion sequence in loop
robot = RMC()
robot.forward()
utime.sleep(5)
robot.stop()

# robot.backward()
# utime.sleep(2)
# robot.stop()
# 
# robot.left()
# utime.sleep(1)
# robot.stop()
# 
# robot.right()
# utime.sleep(1)
# robot.stop()