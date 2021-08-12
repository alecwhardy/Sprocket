import serial
import time
import random
from xbox360controller import Xbox360Controller
import signal
from XYZrobotServo import XYZrobotServo
from Leg import Leg
from Dog import Dog

# Create the Servo serial stream
ser = serial.Serial('/dev/ttyS0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

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


"""
while True:
    
    resp = input("Enter X, Y, Z position: ").split(',')

    for leg in legs:
        leg.set_position(int(resp[0]), int(resp[1]), int(resp[2]), 100)

    time.sleep(1)
"""

def on_button_pressed(button):
    if button.name == 'button_a':
        global px, py, pz
        px = 0
        py = 0
        pz = 100

        for leg in legs:
            leg.go_position(px, py, pz, 100)


with Xbox360Controller(0, axis_threshold=0.5) as controller:

    while True:
        des_x = -40*controller.axis_l.x
        des_y = 40*-controller.axis_l.y
        des_z = 150
        # des_z = 100-(80*controller.axis_r.y)

        # des_roll = 20*controller.axis_r.x
        des_roll = 0
        des_pitch = 20*controller.axis_r.y
        des_yaw = 20*controller.axis_r.x

        print(des_x, des_y, des_roll, des_pitch)

        # for leg in legs:
        #     leg.go_position(des_x, des_y, des_z, 20)
        dog.go_position(des_x, des_y, des_z, des_roll, des_pitch, des_yaw, 20)
        time.sleep(.2)



    # controller.button_a.when_pressed = on_button_pressed




        


"""
while True:    
    for leg in legs:
        leg.set_position(0, 0, 100, 100)
    time.sleep(1)
"""