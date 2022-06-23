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
    
    Kp_dat = bytearray(2)
    Ki_dat = bytearray(2)
    
    Kp_dat[1] = 0x20
    Kp_dat[0] = 0x00
    
    Ki_dat[1] = 0x00
    Ki_dat[0] = 0x00
    
    for servo in servos:
        servo.RAMWrite(24, Kp_dat)
        servo.RAMWrite(28, Ki_dat)

    # Start the data server thread (daemon)
    server_thread = Thread(target=serve, daemon=True, args=(dog, )).start()

    # Schedule Events
    dog.schedule_event(dog.check_voltage, 30000)    # Check the voltage every 30s
    dog.schedule_event(dog.update_orientation, 100)
    dog.schedule_event(dog.servos.updateAllStatus, 10) # Update the servo status every 10ms

    #dog.wake_up()
    dog.die()
    dog.live(verbose = True)



    # TODO!!!
    # Dog calfs hit floor while walking becauyse they bend in too much.  Change code so shoulders bend (straighten) more than legs.
    # Example: When z-height is low (dog crounching), the calfs are almost parallel with the ground.  Change this (Leg.py?)