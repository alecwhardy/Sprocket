import serial
from Behavior import Behavior
from XYZrobotServo import XYZrobotServo
from Leg import Leg
from Dog import Dog
from Controls.XboxControl import XboxControl
            
if __name__ == '__main__':

    # Create the Servo serial stream
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

    # Create a XYZrobotServo object for each leg servo
    leg_servos = []
    for i in range(12):
        leg_servos.append(XYZrobotServo(ser, i+1, debug=False))

    # Create a Leg object for each leg in an array, following the order used by the Dog class initializer (FL, FR, RL, RR)
    # The Leg class already knows what servo ID corresponds to what joint
    # Example Usage: legs[Leg.FR].set_thigh_position(0, 0)
    legs = [Leg("FL", leg_servos), Leg("FR", leg_servos), Leg("RL", leg_servos), Leg("RR", leg_servos)]

    # Create the Dog object that lets us control the body position and movements
    dog = Dog(legs)
    
    Kp_dat = bytearray(2)
    Ki_dat = bytearray(2)
    
    Kp_dat[1] = 0x20
    Kp_dat[0] = 0x00
    
    Ki_dat[1] = 0x00
    Ki_dat[0] = 0x00
    
    for servo in leg_servos:
        servo.RAMWrite(24, Kp_dat)
        servo.RAMWrite(28, Ki_dat)

    dog.wake_up()
    dog.live(verbose = True)



    # TODO!!!
    # Dog calfs hit floor while walking becauyse they bend in too much.  Change code so shoulders bend (straighten) more than legs.
    # Example: When z-height is low (dog crounching), the calfs are almost parallel with the ground.  Change this (Leg.py?)