import camera
import network,socket,sys,utime,machine

STATIC_IP = '192.168.4.5'
SUBNET_MASK = '255.255.255.0'
GATEWAY = '192.168.4.1'
DNS = '8.8.8.8'

flash = machine.Pin(4, machine.Pin.OUT)
flash.on()
utime.sleep(1)
flash.off()

try:
    utime.sleep(0.01)
    if camera.init(True):
        print("Camera is recording")
    else:
        print("Camera is not recording")

    #camera.flip(True)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))
    try:
        wifi.connect('Chitti','esp@1234')
    except OSError:
        pass
    while not wifi.isconnected():
        print("wifi is connecting...")

    print(wifi.isconnected())
    print("IP Address:",wifi.ifconfig()[0])
    ip=wifi.ifconfig()[0]
    #TCP Protocol
    server=socket.socket()
    server.bind((ip,80))
    server.listen(True)
    while True:
        client,address=server.accept()
        client.send(b"HTTP/1.1 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=frame\r\nConnection: keep-alive\r\n\r\n")
        while True:
            frame = camera.capture()
            client.send(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            utime.sleep(0.01)
except OSError:
    machine.reset()
except Exception as error:
    print(error)
    sys.exit()
except KeyboardInterrupt:
    sys.exit()
    server.close()
    wifi.disconnect()