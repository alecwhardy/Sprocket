import serial
from Behavior import Behavior
from XYZrobotServo import *
from Leg import Leg
from Dog import Dog
from Controls.XboxControl import XboxControl
from threading import Thread
from Networking.DataServer import serve
            
if __name__ == '__main__':

    # Create the Servo serial stream
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

    # Create a XYZrobotServo object for each leg servo
    servo_list = []
    for i in range(12):
        servo_list.append(XYZrobotServo(ser, i+1, debug=False))
    servos = XYZrobotServos(servo_list)

    # Create the Dog object that lets us control the body position and movements
    dog = Dog(servos)
    
    for servo in servos:
        servo.RAMWrite(24, b'\x00\x20')  # Set kp = 32 by writing 2 bytes (big-endian)
        servo.RAMWrite(28, b'\x00\x00')  # Set ki = 0 by writing 2 bytes (big-endian)

    # Start the data server thread (daemon)
    # server_thread = Thread(target=serve, daemon=True, args=(dog, )).start() 

    # Schedule Events
    dog.schedule_event(dog.check_voltage, 30000)    # Check the voltage every 30s
    dog.schedule_event(dog.update_orientation, 20) # Update the IMU every 20ms
    #og.schedule_event(dog.servos.updateAllStatus, 10) # Update the servo status every 10ms.  Need to make this a seperate thread because it interferes with xbox360 controller

    #dog.wake_up()
    dog.die()
    dog.live(verbose = True)



    # TODO!!!
    # Dog calfs hit floor while walking because they bend in too much.  Change code so shoulders bend (straighten) more than legs.
    # Example: When z-height is low (dog crounching), the calfs are almost parallel with the ground.  Change this (Leg.py?)