import machine
import utime
import network
import espnow
from  gyro import MPU6050
import struct

i2c = machine.I2C(scl=machine.Pin(14),sda=machine.Pin(13))
mpu6050 = MPU6050(i2c)

station = network.WLAN()
station.active(True)
station.disconnect()

protocol = espnow.ESPNow()
protocol.active(True)

mac = b'(V/I\xf9|'

protocol.add_peer(mac)

protocol.send(mac, "sending...")

while True:
    utime.sleep(0.1)
    ax=round(mpu6050.accel.x,2)
    ay=round(mpu6050.accel.y,2)

    protocol.send(struct.pack('ff', ax, ay))
    print(protocol.send(struct.pack('ff', ax, ay)))
    print("ax:",ax,"m/s" ,"ay:",ay,"m/s")