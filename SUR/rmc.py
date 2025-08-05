import machine

# Class Creation
class RMC:
    def __init__(self,speed=65000,ml=21,mr=25,lf=19,lb=18,rf=22,rb=23):
        self.speed = speed
        # MOTOR DRIVE
        self.pwm_L = machine.PWM(machine.Pin(ml))
        self.pwm_R = machine.PWM(machine.Pin(mr))
        self.pwm_L.freq(1907)
        self.pwm_R.freq(1907)
        # ROBOT WHEELS
        self.LH_B = machine.Pin(lf, machine.Pin.OUT)  # LEFT BACKWARD
        self.LH_F = machine.Pin(lb, machine.Pin.OUT)  # LEFT FORWARD
        self.RH_B = machine.Pin(rf, machine.Pin.OUT)  # RIGHT BACKWARD
        self.RH_F = machine.Pin(rb, machine.Pin.OUT)  # RIGHT FORWARD
      
    def set_speed(self,s=65000):
        self.speed = s
        self.pwm_L.duty_u16(self.speed)
        self.pwm_R.duty_u16(self.speed)
    def set_speedL(self,s=65000):
        self.speed = s
        self.pwm_L.duty_u16(self.speed-5000)
        self.pwm_R.duty_u16(self.speed)
    def set_speedR(self,s=65000):
        self.speed = s
        self.pwm_L.duty_u16(self.speed)
        self.pwm_R.duty_u16(self.speed-5000)
        
    # DIRECTION
    def forward(self,s=65000):
        self.set_speed(s)
        self.RH_F.on()
        self.LH_F.on()
        self.RH_B.off()
        self.LH_B.off()
        print("Accelerate(f)")

    def backward(self,s=65000):
        self.set_speed(s)  
        self.RH_F.off()
        self.LH_F.off()
        self.RH_B.on()
        self.LH_B.on()
        print("Reverse")

    def stop(self):
        self.RH_F.off()
        self.LH_F.off()
        self.RH_B.off()
        self.LH_B.off()
        print("Brake")

    def left(self,s=65000):
        self.speed = s
        self.pwm_R.duty_u16(self.speed)  
        self.RH_F.on()
        self.LH_F.off()
        self.RH_B.off()
        self.LH_B.off()
        print("Turn left")

    def right(self,s=65000):
        self.speed = s
        self.pwm_L.duty_u16(self.speed)  
        self.RH_F.off()
        self.LH_F.on()
        self.RH_B.off()
        self.LH_B.off()
        print("Turn right")

    def drift_left(self,s=65000):
        self.set_speed(s)
        self.RH_F.on()
        self.LH_F.off()
        self.RH_B.off()
        self.LH_B.on()
        print("Turn left(d)")

    def drift_right(self,s=65000):
        self.set_speed(s)
        self.RH_F.off()
        self.LH_F.on()
        self.RH_B.on()
        self.LH_B.off()
        print("Turn right(d)")
        
    def forward_left(self,s=65000):
        self.set_speedL(s)
        self.RH_F.on()
        self.LH_F.on()
        self.RH_B.off()
        self.LH_B.off()
        print("Forward Left")
        
    def backward_left(self,s=65000):
        self.set_speedL(s)
        self.RH_F.off()
        self.LH_F.off()
        self.RH_B.on()
        self.LH_B.on()
        print("Backward Left")
    
    def forward_right(self,s=65000):
        self.set_speedR(s)
        self.RH_F.on()
        self.LH_F.on()
        self.RH_B.off()
        self.LH_B.off()
        print("Forward Right")
        
    def backward_right(self,s=65000):
        self.set_speedR(s)
        self.RH_F.off()
        self.LH_F.off()
        self.RH_B.on()
        self.LH_B.on()
        print("Backward Right")
