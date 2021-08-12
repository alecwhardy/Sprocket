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

    SHOULDER_LENGTH = 42

    # Leg length constraints
    # The "R" variable is for leg length, or, when the shoulders are flat, the height at the shoulder/thigh joint.
    R_L1_MIN = 0
    R_L1_MAX = L1_len
    R_L2_MIN = L2_len*math.sin(math.radians(THETA_KNEE_MIN))
    R_L2_MAX = L2_len*math.sin(math.radians(abs(THETA_KNEE_MAX-180)))
    R_MIN = R_L1_MIN + R_L2_MIN
    R_MAX = R_L1_MAX + R_L2_MAX


    def __init__(self, location, servos):
        
        # Define each joint's servo ID

        self.side = 'L' if location[1] == 'L' else 'R'
        self.end = 'F' if location[0] == 'F' else 'R'
        self.location = location

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
        """Sets the shoulder position, a positive valuve moves the shoulders "up", like a shrug

        Args:
            position_degrees ([type]): [description]
            speed ([type]): [description]
        """

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
        """Set the position of the knee, relative to the thigh

        Args:
            position_degrees (int): Can be between 15 degrees and 160 degrees. 
            speed (uint8): Time in 10ms units to respond to new position
        """

        if not self.THETA_KNEE_MIN <= position_degrees <= self.THETA_KNEE_MAX:
            # Invalid Position!  TODO: Log error!
            return

        self.theta_knee = position_degrees

        # Position angles need to be inverted on the LHS
        if self.side == 'L':
            position_degrees = -position_degrees

        self.knee_stream.set_position_deg(position_degrees, speed)
        

    def get_r_l1(self):
        return self.L1_len*math.sin(math.radians(self.theta_thigh))

    def get_r_l2(self):
        return self.L2_len*math.sin(math.radians(self.theta_knee))

    def get_r(self):
        return self.get_r_l1 + self.get_r_l2

    @staticmethod
    def get_theta_knee_for_r(desired_r, theta_thigh):
        """ Dont use this
        """
        r_l1 = Leg.L1_len*math.sin(math.radians(theta_thigh))
        r_l2_req = desired_r - r_l1
        try:
            return math.degrees(math.asin(r_l2_req/Leg.L2_len))
        except ValueError:
            return 90


    @staticmethod
    def get_thetas_for_length(leg_length):
        """Returns the thigh and knee angles needed to achieve a desired leg z length.
           
           Note that Leg Z length does NOT necessarily mean dog height, as a change in the shoulder angle will change this

        Args:0, 
            desired_z (int): Desired leg length

        Returns:
            Tuple: Thigh Angle, Knee Angle
        """

        # We are going to assume here that L1 and L2 are equal, so we will set theta_knee = theta_thigh
        # Remember that theta_knee must stay between 15-165 degrees
        # Because of this, if we need to go to a z-height lower than the position that would require theta_knee < 15
        # then we will lower theta_thigh even more.

        if not Leg.R_MIN <= leg_length <= Leg.R_MAX:
            # TODO: Log error!
            return

        if leg_length <= 2*Leg.R_L2_MIN:

            # Now try to set theta_thigh to determine the difference
            desired_z_l1 = leg_length -Leg.R_L2_MIN
            desired_thigh_pos = math.degrees(math.asin(desired_z_l1/Leg.L1_len))
            desired_knee_pos = Leg.THETA_KNEE_MIN

        else:
            # Let's just use L1 as the assumed leg segment length
            desired_z_l1 = leg_length / 2
            desired_thigh_pos = math.degrees(math.asin(desired_z_l1/Leg.L1_len))
            desired_knee_pos = desired_thigh_pos

        # Now set the positions
        return desired_thigh_pos, desired_knee_pos
        
    def set_position(self, X, Y, Z, speed):
        """Sets the X, Y, Z position of each individual leg

           TODO: Something isn't quite right.  Changing the X offset also changes the Z height, the
           trig must be wrong somewhere.

        Args:
            X (int or float): Desired X position
            Y (int or float): Desired Y position
            Z (int or float): Desired Z position
            speed (int, between 0-255): Desired movement time, in units of 10ms
        """

        neg_X = False
        if X<0:
            neg_X = True
            X = abs(X)

        X = X+self.SHOULDER_LENGTH

        if X == 0.0:
            X = 0.001
        if Y == 0.0:
            Y = 0.001

        # Leg length l
        l_xz = math.sqrt((X*X)+(Z*Z)-(Leg.SHOULDER_LENGTH*Leg.SHOULDER_LENGTH))
        h = math.sqrt(X*X + Z*Z)
        theta_1_rad = math.atan(X/Z)
        theta_2_rad = math.asin(Leg.SHOULDER_LENGTH/h)
        l = math.sqrt((l_xz*l_xz)+(Y*Y))
        
        theta_shoulder = math.degrees(theta_2_rad-theta_1_rad)

        # The shoulder theta values work for RHS shoulders, but need to be inverted for LHS
        if self.location == 'FL' or self.location == 'RR':
            theta_shoulder = -theta_shoulder
        if neg_X:
            theta_shoulder = -theta_shoulder

         # TODO: SHOULD THIS BE l OR l_xz
        theta_thigh_offset = math.degrees(math.atan(Y/l_xz))

        # From SSS (Side Side Side) Law of Cosines
        theta_knee = math.degrees(math.acos(((Leg.L1_len*Leg.L1_len)+(Leg.L2_len*Leg.L2_len)-(l*l))/(2*Leg.L1_len*Leg.L2_len)))

        # If we are moving in +Y direction, then theta_thigh will decrease
        # TODO: This might not be correct, does it assume that L1 and L2 are the same?
        theta_thigh = (theta_knee/2)-theta_thigh_offset
       
        self.set_shoulder_position(theta_shoulder, speed)
        self.set_thigh_position(theta_thigh, speed)
        self.set_knee_position(theta_knee, speed)
        