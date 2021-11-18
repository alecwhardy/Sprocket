import math
from Leg import Leg
import time
from CommandHandler import CommandHandler
from Motion import Motion

class Dog:
    """ Contains all of the necessary code to determine the current state of the dog.  All behavior is handled by the Behavior class

    Returns:
        [type]: [description]
    """

    LENGTH = 200
    WIDTH = 117

    NEUTRAL_HEIGHT = 150
    NEUTRAL_SPEED = 20

    # The most recent x, y, z, r, p, yaw values that the dog moved to after a go_position() call
    x = 0
    y = 0
    z = 0
    roll = 0
    pitch = 0
    yaw = 0
    speed = 0

    sensor_roll = 0
    sensor_pitch = 0
    sensor_yaw = 0

    def __init__(self, legs):
        """[summary]

        Args:
            legs (List of Legs): Follow order Front Left, Front Right, Rear Left, Rear Right
        """
        self.legs = legs
        self.command_handler = CommandHandler(self)
        self.motion = Motion(self)


    def get_voltage(self):
        return self.legs[0].servos[0].getVoltage()

    def flatten_shoulders(self, speed):
        for leg in self.legs:
            leg.go_shoulder_angle(0, speed)

    def go_position(self, X, Y, Z, roll, pitch, yaw, speed):

        if roll == 0:
            roll = 0.001
        if pitch == 0:
            pitch = 0.001
        if yaw == 0:
            yaw = 0.001

        for leg in self.legs:
            leg.desired_x = X
            leg.desired_y = Y
            leg.desired_z = Z
            leg.desired_speed = speed


        # Take care of pitch first
        # TODO: Determine if we *can* even go to the desired pitch (at the given height at we are at)

        Z_front_offset = (Dog.LENGTH/2)*math.tan(math.radians(pitch))
        for leg in self.legs:
            if leg.end == 'F':
                leg.desired_z += Z_front_offset
            if leg.end == 'R':
                leg.desired_z -= Z_front_offset

        # Now take care of roll
        # TODO: Determine if we *can* even go to the desired roll (at the given height at we are at)

        Z_left_offset = (Dog.WIDTH/2)*math.tan(math.radians(roll))
        for leg in self.legs:
            if leg.side == 'R':
                leg.desired_z -= Z_left_offset
            if leg.side == 'L':
                leg.desired_z += Z_left_offset

        # Now take care of yaw
        # TODO: Determine if we *can* even go to the desired yaw (at the given height at we are at)

        X_front_offset = (Dog.LENGTH/2)*math.tan(math.radians(yaw))
        for leg in self.legs:
            if leg.end == 'F':
                leg.desired_x += X_front_offset
            if leg.end == 'R':
                leg.desired_x -= X_front_offset
        
        # Calculate where each leg needs to go
        # We need to do all of the shoulders first, then thighs, then knees in order, otherwise the legs don't move at the same time
        # i.e. leg[3] will run last and behind the others if we don't run this way
        for leg in self.legs:
            if leg.calc_desired():
                # If we successfully calculate the desired
                self.x = X
                self.y = Y
                self.z = Z
                self.roll = roll
                self.pitch = pitch
                self.yaw = yaw
                self.speed = speed
        # Go to the calculated shoulder angles
        for leg in self.legs:
            leg.go_shoulder_angle(leg.calc_theta_shoulder, leg.desired_speed)
        # Go to the calculated thigh angles
        for leg in self.legs:
            leg.go_thigh_angle(leg.calc_theta_thigh, leg.desired_speed)
        # Go to the calculated knee angles
        for leg in self.legs:
            leg.go_knee_angle(leg.calc_theta_knee, leg.desired_speed)

    def die(self):
        print("Dog is dying...")
        for leg in self.legs:
            for servo in leg.servos:
                servo.torqueOff()

    def wake_up(self):
        print("Resetting position 'waking up'")
        self.go_position(0, 0, 150, 0, 0, 0, self.NEUTRAL_SPEED)
        #TODO: Calibrate Euler angles here

    def servo_reboot(self):
        for servo in self.legs[0].servos:
            servo.reboot()

    def live(self, verbose = False):
        """ Main loop.  Update sensor data, update servos, and respond to behaviors and controls
        """

        while True:

            # get new commands
            self.command_handler.get_new_commands()
            
            # handle commands
            self.command_handler.handle_commands()

            # update sensors
            
            # update motion
            self.motion.update_motion()

            time.sleep(0)