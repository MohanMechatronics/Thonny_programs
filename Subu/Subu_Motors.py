from Wheels import Wheels
import Subu

wheels = Wheels("LMESMP")
wheels.start_motors()

#forward
# wheels.drive_motors(512, 0, 512, 0)

#reverse
wheels.drive_motors(0, 1023, 0, 1023)
