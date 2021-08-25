import math
from Leg import Leg
import time

class Dog:

    LENGTH = 200
    WIDTH = 117

    x = 0
    y = 0
    z = 0
    roll = 0
    pitch = 0
    yaw = 0

    desired_x = 0
    desired_y = 0
    desired_z = 0
    desired_roll = 0
    desired_pitch = 0
    desired_yaw = 0
    desired_speed = 0
    
    def __init__(self, legs):
        """[summary]

        Args:
            legs (List of Legs): Follow order Front Left, Front Right, Rear Left, Rear Right
        """
        self.legs = legs

    def get_voltage(self):
        return self.legs[0].servos[0].getVoltage()

    def flatten_shoulders(self, speed):
        for leg in self.legs:
            leg.go_shoulder_angle(0, speed)

    def set_desired_to_position(self):
        """ Sets the desired setpoint variables equal to the current position
        """
        self.desired_x = self.x
        self.desired_y = self.y
        self.desired_z = self.z
        self.desired_roll = self.roll
        self.desired_pitch = self.pitch
        self.desired_yaw = self.yaw
        self.desired_speed = self.speed

    def go_desired(self):
        self.go_position(self.desired_x, self.desired_y, self.desired_z, self.desired_roll, self.desired_pitch, self.desired_yaw, self.desired_speed)

    def go_position(self, X, Y, Z, roll, pitch, yaw, speed):

        self.x = X
        self.y = Y
        self.z = Z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.speed = speed

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
        

        # Update all of the leg positions
        for leg in self.legs:
            leg.go_desired()

        pass

    def prance(self, n, lift = 20, speed = 10, sleep_time = .1):
        original_angles = []
        new_angles = []
        for leg in self.legs:
            original_angles.append(leg.theta_knee)
            new_angles.append(leg.theta_knee - lift)

        ctr = 0
        while ctr < int(n):
            self.legs[0].go_knee_angle(new_angles[0], speed)
            self.legs[3].go_knee_angle(new_angles[3], speed)
            time.sleep(sleep_time)
            self.legs[0].go_knee_angle(original_angles[0], speed)
            self.legs[3].go_knee_angle(original_angles[3], speed)
            time.sleep(sleep_time)
            ctr += 1
            self.legs[1].go_knee_angle(new_angles[1], speed)
            self.legs[2].go_knee_angle(new_angles[2], speed)
            time.sleep(sleep_time)
            self.legs[1].go_knee_angle(original_angles[1], speed)
            self.legs[2].go_knee_angle(original_angles[2], speed)
            time.sleep(sleep_time)
            ctr += 1

    def die(self):
        for leg in self.legs:
            for servo in leg.servos:
                servo.torqueOff()