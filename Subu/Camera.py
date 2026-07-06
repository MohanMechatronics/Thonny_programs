import uasyncio as asyncio
from Wheels import Wheels  # Your complete class code in wheels.py

async def websocket_poll_loop(wheels_obj):
    while True:
        wheels_obj.WSServer.poll()
        await asyncio.sleep_ms(10)  # Yield to scheduler

async def camera_starter(wheels_obj):
    await asyncio.sleep(20)  # Let server start first (20 seconds delay)
    print("Enabling Camera")
    wheels_obj.enableCamera()

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


