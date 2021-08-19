import serial
import time
import random
from xbox360controller import Xbox360Controller
import signal
from XYZrobotServo import XYZrobotServo
from Leg import Leg
from Dog import Dog


def play_with_xbox(dog):
   
    with Xbox360Controller(0, axis_threshold=0.5) as controller:
        des_x = 0
        des_y = 0
        des_z = 150

        des_roll = 0
        des_pitch = 0
        des_yaw = 0
        

        while True:
            des_x = 80*controller.axis_r.x
            
            if not controller.button_trigger_r.is_pressed:
                des_y = 40*-controller.axis_r.y
            else:
                des_z -= 10*controller.axis_r.y
            # des_z = 100-(80*controller.axis_r.y)


            des_pitch = -20*controller.axis_l.y

            if not controller.button_trigger_l.is_pressed:
                des_roll = 30*controller.axis_l.x
            else:
                des_yaw += 2*controller.axis_l.x

            print("{:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f}".format(des_x, des_y, des_z, des_roll, des_pitch, des_yaw))

            try:
                dog.go_position(des_x, des_y, des_z, des_roll, des_pitch, des_yaw, 40)
                time.sleep(.2)
            except ValueError:
                
                if controller.has_rumble:
                    controller.set_rumble(0.5, 0.5, 1000)

                des_x = 0
                des_y = 0
                des_z = 150

                des_roll = 0
                des_pitch = 0
                des_yaw = 0

def cmd_control(dog):

    while True:

        response = input("Please enter command: ")

        if response=='help':
            
            print("[space]: Home")
            print("Dog absolute move: A [x] [y] [z] [roll, optional] [pitch, optional] [yaw, optional] [speed, optional]")
            print("Dog relative move: R {x, y, z, roll, pitch, yaw} [value]")
            print("Prance: prance [num]")

        response_tokens = response.split(' ')

        if response_tokens[0] == '':
            dog.go_position(0, 0, 150, 0, 0, 0, 20)
            print("Resetting position")

        if response_tokens[0] == 'A':
            x = 0 
            y = 0
            roll = 0
            pitch = 0
            yaw = 0
            z = 150
            speed = 100
            try:
                x = float(response_tokens[1])
                y = float(response_tokens[2])
                z = float(response_tokens[3])
                roll = float(response_tokens[4])
                pitch = float(response_tokens[5])
                yaw = float(response_tokens[6])
                speed = int(response_tokens[7])
            except IndexError:
                pass

            dog.go_position(x, y, z, roll, pitch, yaw, speed)
            print("Position: {: 3.0f}  {: 3.0f}  {: 3.0f}  {: 3.0f} {: 3.0f} {: 3.0f} {: 3.0f}".format(x, y, z, roll, pitch, yaw, speed))

        if response_tokens[0] == 'R':
            
            dog.set_desired_to_position()

            if response_tokens[1] in {'x', 'y', 'z', 'roll', 'pitch', 'yaw'}:
                new_val = getattr(dog, 'desired_' + response_tokens[1]) + float(response_tokens[2])
                setattr(dog, 'desired_' + response_tokens[1], new_val)

            dog.desired_speed = 20
            dog.go_desired()
            print("Relative move: {} {}".format(response_tokens[1], response_tokens[2]))

        if response_tokens[0] == 'prance':
            # Test code: Lift the front right leg a tiny bit (change the theta knee)
            
            speed = 10
            sleep_time = .1
            lift_amount = 25
            original_angles = []
            new_angles = []
            for leg in dog.legs:
                original_angles.append(leg.theta_knee)
                new_angles.append(leg.theta_knee - lift_amount)

            ctr = 0
            while ctr < int(response_tokens[1]):

                dog.legs[0].go_knee_angle(new_angles[0], speed)
                dog.legs[3].go_knee_angle(new_angles[3], speed)
                time.sleep(sleep_time)
                dog.legs[0].go_knee_angle(original_angles[0], speed)
                dog.legs[3].go_knee_angle(original_angles[3], speed)
                time.sleep(sleep_time)
                ctr += 1
                dog.legs[1].go_knee_angle(new_angles[1], speed)
                dog.legs[2].go_knee_angle(new_angles[2], speed)
                time.sleep(sleep_time)
                dog.legs[1].go_knee_angle(original_angles[1], speed)
                dog.legs[2].go_knee_angle(original_angles[2], speed)
                time.sleep(sleep_time)
                ctr += 1

            
if __name__ == '__main__':

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

    dog.flatten_shoulders(100)

    # play_with_xbox(dog)
    cmd_control(dog)
