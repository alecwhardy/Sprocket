import os, psutil
import serial
import time
from xbox360controller import Xbox360Controller
from XYZrobotServo import XYZrobotServo
from Leg import Leg
from Dog import Dog
import Walk


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
            print("Leg absolute move: L [n] [x] [y] [z]")
            print("Prance: prance [num]")
            print("Sleep: sleep")
            print("Die: die")
            print("Resource usage: res")
            print("Reboot: reboot")
            print("Error: error")

        response_tokens = response.split(' ')

        if response_tokens[0] == '':
            dog.go_position(0, 0, 150, 0, 0, 0, 20)
            print("Resetting position")

        if response_tokens[0] == 'die':
            dog.die()

        if response_tokens[0] == 'sleep':
            dog.go_position(0, 0, 35, 0, 0, 0, 100)
            time.sleep(1)
            dog.die()

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
            
            # TODO: Which "prance" behavior is better?
            # dog.prance(response_tokens[1])
            Walk.crude_walk(dog, Walk.IN_PLACE, int(response_tokens[1]), 40, 30)


        if response_tokens[0] == 'L':
            x = float(response_tokens[2])
            y = float(response_tokens[3])
            z = float(response_tokens[4])
            legs[int(response_tokens[1])-1].go_position(x, y, z, 20)

        if response_tokens[0] == 'wf':
            Walk.crude_walk(dog, Walk.FORWARD, int(response_tokens[1]), 30, 50, 12)

        if response_tokens[0] == 'wl':
            Walk.crude_walk(dog, Walk.TURN_LEFT, int(response_tokens[1]), 30, 50, 12)

        if response_tokens[0] == 'wr':
            Walk.crude_walk(dog, Walk.TURN_RIGHT, int(response_tokens[1]), 30, 50, 12)

        if response_tokens[0] == 'wsl':
            Walk.crude_walk(dog, Walk.SIDE_LEFT, int(response_tokens[1]), 30, 50, 12)

        if response_tokens[0] == 'wsr':
            Walk.crude_walk(dog, Walk.SIDE_RIGHT, int(response_tokens[1]), 30, 50, 12)

        if response_tokens[0] == 'res':
            # Resource Usage
            process = psutil.Process(os.getpid())
            print("Memory Usage (MB): " + str(process.memory_info().rss/1024/2014))
            print("CPU Usage: "+str(psutil.cpu_percent()))
            print("Voltage: {}V".format(dog.get_voltage()))

        if response_tokens[0] == 'pid':
            print(dog.legs[0].servos[0].readPID_RAM())

        if response_tokens[0] == 'reboot':
            for servo in dog.legs[0].servos:
                servo.reboot()

        if response_tokens[0] == 'error':
            for servo in dog.legs[0].servos:
                status = servo.readStatus()
                print("Servo {}: {}".format(servo.id, status.statusError))

            
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

    dog.flatten_shoulders(100)

    # play_with_xbox(dog)
    cmd_control(dog)
    
