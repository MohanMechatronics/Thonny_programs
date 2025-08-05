import machine
import utime


class sensor:
    def __init__(self):
        self.trigger =  machine.Pin(13, machine.Pin.OUT)
        self.echo = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_DOWN)

    def distance(self):
        utime.sleep(0.1)
        self.trigger.off()
        utime.sleep_us(1)
        self.trigger.on()
        utime.sleep_us(1)
        self.trigger.off()


        while self.echo.value()==0:
            send_time = utime.ticks_us()
        while self.echo.value()==1:
            received_time = utime.ticks_us()
            
        duration = received_time - send_time
        total_distance =  0.0343*duration
        object_distance = total_distance/2
        return object_distance
        
        
        
