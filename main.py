import serial
import time
import random
from XYZrobotServo import XYZrobotServo
from Leg import Leg
from Dog import Dog

# Create the Servo serial stream
ser = serial.Serial('/dev/ttyS0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

# Create a XYZrobotServo object for each leg servo
leg_servos = []
for i in range(12):
    leg_servos.append(XYZrobotServo(ser, i+1, debug=True))

# Create a Leg object for each leg in an array, following the order used by the Dog class initializer (FL, FR, RL, RR)
# The Leg class already knows what servo ID corresponds to what joint
# Example Usage: legs[Leg.FR].set_thigh_position(0, 0)
legs = [Leg("FL", leg_servos), Leg("FR", leg_servos), Leg("RL", leg_servos), Leg("RR", leg_servos)]

# Create the Dog object that lets us control the body position and movements
dog = Dog(legs)


"""
def down():
    servos[2-1].setPosition(512, 200)
    servos[11-1].setPosition(512, 200)
    servos[5-1].setPosition(512, 200)
    servos[8-1].setPosition(512, 200)
    servos[3-1].setPosition(450, 200)
    servos[12-1].setPosition(450, 200)
    servos[6-1].setPosition(574, 200)
    servos[9-1].setPosition(574,200)

def pushup():
    for i in range(10):
        down()
        time.sleep(2)
        stand()
        time.sleep(2)

"""


dog.flatten_shoulders(100)


while True:
    
    resp = input("Enter X, Y, Z position: ").split(',')

    for leg in legs:
        leg.set_position(int(resp[0]), int(resp[1]), int(resp[2]), 100)

    time.sleep(1)
