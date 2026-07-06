import uasyncio as asyncio
from Wheels import Wheels  # Your complete class code in wheels.py

async def websocket_poll_loop(wheels_obj):
    while True:
        wheels_obj.WSServer.poll()
        await asyncio.sleep_ms(10)  # Yield to scheduler

async def camera_starter(wheels_obj):
    await asyncio.sleep(35)  # Let server start first (20 seconds delay)
    print("Enabling Camera")
    wheels_obj.enableCamera()
    
    while True:
        ges = wheels_obj.motion_command.getCommand()
        if ges != None:
            if ges == "forward":
                wheels_obj.drive_motors(1023,0,1023,0)
            elif ges == "backward":
                wheels_obj.drive_motors(0,1023,0,1023)
            elif ges == "left":
                wheels_obj.drive_motors(1023,0,0,1023)
            elif ges == "right":
                wheels_obj.drive_motors(0,1023,1023,0)
            elif ges == "stop":
                wheels_obj.drive_motors(0,0,0,0)
        await asyncio.sleep_ms(10)

async def main():
    print("Starting Wheels system with WebSocketServer...")
    wheels = Wheels("LMESMP")
    wheels.start_motors()
    wheels.WSServer.start()

    # Launch both WebSocket polling and camera enabler
    await asyncio.gather(
        websocket_poll_loop(wheels),
        camera_starter(wheels)
    )

try:
    asyncio.run(main())
except Exception as e:
    print("Main loop error:", e)



