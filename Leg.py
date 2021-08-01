from enum import Enum
import math

class Leg:

    FL = 0
    FR = 1
    RL = 2
    RR = 3

    theta_shoulder = 0
    theta_thigh = 0
    theta_knee = 0
    

    THETA_KNEE_MIN = 15
    THETA_KNEE_MAX = 160

    L1_len = 120
    L2_len = 106

    Z_L1_MIN = 0
    Z_L1_MAX = L1_len

    Z_L2_MIN = L2_len*math.sin(math.radians(THETA_KNEE_MIN))
    Z_L2_MAX = L2_len*math.sin(math.radians(THETA_KNEE_MAX-90))   # TODO:  Do I need the -90 degrees?  Arctrig with angles >90 deg?!?

    Z_MIN = Z_L1_MIN + Z_L2_MIN
    Z_MAX = Z_L1_MAX + Z_L2_MAX



    def __init__(self, location, servos):
        
        # Define each joint's servo ID

        self.side = 'L' if location[1] == 'L' else 'R'
        self.end = 'F' if location[0] == 'F' else 'R'

        # Front Left
        if location == "FL":
            self.shoulder_ID = 1
            self.thigh_ID = 2
            self.knee_ID = 3
        #Front Right
        if location == "FR":
            self.shoulder_ID = 4
            self.thigh_ID = 5
            self.knee_ID = 6
        # Rear Right
        if location == "RR":
            self.shoulder_ID = 7
            self.thigh_ID = 8
            self.knee_ID = 9
        # Rear Left
        if location == "RL":
            self.shoulder_ID = 10
            self.thigh_ID = 11
            self.knee_ID = 12

        # Now assign the servo stream for each joint
        self.shoulder_stream = servos[self.shoulder_ID-1]
        self.thigh_stream = servos[self.thigh_ID-1]
        self.knee_stream = servos[self.knee_ID-1]

        # TODO: Use Servo getStatus to determine the starting position.

    def set_shoulder_position(self, position_degrees, speed):

        # Make sure we are at a valid position.  0 degrees is flat, allow +/- 45 degrees
        if not -60 <= position_degrees <= 60:
            # Invalid Position!  TODO: Log error!
            return

        self.theta_shoulder = position_degrees
        # Position angles need to be inverted on the RHS
        if self.side == 'R':
            position_degrees = -position_degrees

        self.shoulder_stream.set_position_deg(position_degrees, speed)
        

    def set_thigh_position(self, position_degrees, speed):
        """Set the position of the thigh, 0 degrees is straight horizontal backwards, 90 degrees is straight down

        Args:
            position_degrees (int): Can be between -45 degrees and 165 degrees. 
            speed (uint8): Time in 10ms units to respond to new position
        """

        if not -45 <= position_degrees <= 165:
            # Invalid Position!  TODO: Log error!
            return
        
        self.theta_thigh = position_degrees
        
        # Position angles need to be inverted on the LHS
        if self.side == 'L':
            position_degrees = -position_degrees

        self.thigh_stream.set_position_deg(position_degrees, speed)
        

    def set_knee_position(self, position_degrees, speed):
        self._set_knee_position_relative(position_degrees + self.theta_thigh, speed)
        self.theta_knee = position_degrees

    def _set_knee_position_relative(self, position_degrees, speed):
        """Set the position of the knee, relative to the angle of the thigh (L1)

        Args:
            position_degrees (int): Can be between 15 degrees and 160 degrees. 
            speed (uint8): Time in 10ms units to respond to new position
        """

        if not self.THETA_KNEE_MIN <= position_degrees <= self.THETA_KNEE_MAX:
            # Invalid Position!  TODO: Log error!
            return

        # Position angles need to be inverted on the LHS
        if self.side == 'L':
            position_degrees = -position_degrees

        self.knee_stream.set_position_deg(position_degrees, speed)
        

    def get_z_l1(self):
        return self.L1_len*math.sin(math.radians(self.theta_thigh))

    def get_z_l2(self):
        return self.L2_len*math.sin(math.radians(self.theta_knee))

    def get_z(self):
        return self.get_z_l1 + self.get_z_l2

    def set_z(self, desired_z, speed):

        # We are going to assume here that L1 and L2 are equal, so we will set theta_knee = theta_thigh
        # Remember that theta_knee must stay between 15-165 degrees
        # Because of this, if we need to go to a z-height lower than the position that would require theta_knee < 15
        # then we will lower theta_thigh even more.

        if not self.Z_MIN <= desired_z <= self.Z_MAX:
            # TODO: Log error!
            return

        if desired_z <= 2*self.Z_L2_MIN:
            # Set theta_knee to min
            self.knee_stream.set_position_deg(self.THETA_KNEE_MIN, speed)

            # Now try to set theta_thigh to determine the difference
            desired_z_l1 = desired_z - self.Z_L2_MIN
            desired_thigh_pos = math.degrees(math.asin(desired_z_l1/self.L1_len))

            desired_knee_pos = self.THETA_KNEE_MIN

        else:
            # Let's just use L1 as the assumed leg segment length
            desired_z_l1 = desired_z / 2
            desired_thigh_pos = math.degrees(math.asin(desired_z_l1/self.L1_len))
            desired_knee_pos = desired_thigh_pos

        # Now set the positions
        self.set_thigh_position(desired_thigh_pos, speed)
        self.set_knee_position(desired_knee_pos, speed)
        

