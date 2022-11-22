from enum import Enum
import math
from XYZrobotServo import *

class Leg:

    FL = 0
    FR = 1
    RL = 2
    RR = 3

    # The current angles
    theta_shoulder = 0
    theta_thigh = 0
    theta_knee = 0

    # The calculated angles
    calc_theta_shoulder = 0
    calc_theta_thigh = 0
    calc_theta_knee = 0

    x = 0
    y = 0
    z = 0

    desired_x = 0
    desired_y = 0
    desired_z = 0
    desired_speed = 0
    desired_done = False     # After we update desired_*, this is set False until we have moved there

    THETA_KNEE_MIN = 10
    THETA_KNEE_MAX = 175

    L1_len = 120
    L2_len = 120

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

        self.servos = servos

        # TODO: Use Servo getStatus to determine the starting position.

    def no_torque(self):
        self.shoulder_stream.torqueOff()
        self.thigh_stream.torqueOff()
        self.knee_stream.torqueOff()

    def read_torques(self):
        shoulder_torque = self.shoulder_stream.readStatus().pwm
        thigh_torque = self.thigh_stream.readStatus().pwm
        knee_torque = self.knee_stream.readStatus().pwm

        return shoulder_torque, thigh_torque, knee_torque
        

    def verify_shoulder_angle(self, position_degrees):
        # Make sure we are at a valid position.  0 degrees is flat, allow +/- 45 degrees
        if not -60 <= position_degrees <= 60:
            # Invalid Position!  TODO: Log error!
            return

        self.theta_shoulder = position_degrees
        # Position angles need to be inverted on the RHS
        if self.side == 'R':
            position_degrees = -position_degrees
            
        return position_degrees
    
    def get_shoulder_raw_pos(self, position_degrees):
        position_degrees = self.verify_shoulder_angle(position_degrees)
        return XYZrobotServo.get_raw_position(position_degrees)
        
    def go_shoulder_angle(self, position_degrees, speed):
        """Sets the shoulder position, a positive valuve moves the shoulders "up", like a shrug

        Args:
            position_degrees ([type]): [description]
            speed ([type]): [description]
        """
        
        position_degrees = self.verify_shoulder_angle(position_degrees)
        self.shoulder_stream.set_position_deg(position_degrees, speed)
        

    def verify_thigh_angle(self, position_degrees):
        if not -45 <= position_degrees <= 165:
            # Invalid Position!  TODO: Log error!
            return
        
        self.theta_thigh = position_degrees
        
        # Position angles need to be inverted on the LHS
        if self.side == 'L':
            position_degrees = -position_degrees
            
        return position_degrees

    def get_thigh_raw_pos(self, position_degrees):
        position_degrees = self.verify_thigh_angle(position_degrees)
        return XYZrobotServo.get_raw_position(position_degrees)

    def go_thigh_angle(self, position_degrees, speed):
        """Set the position of the thigh, 0 degrees is straight horizontal backwards, 90 degrees is straight down

        Args:
            position_degrees (int): Can be between -45 degrees and 165 degrees. 
            speed (uint8): Time in 10ms units to respond to new position
        """

        position_degrees = self.verify_thigh_angle(position_degrees)
        self.thigh_stream.set_position_deg(position_degrees, speed)
        

    def verify_knee_angle(self, position_degrees):
        if not self.THETA_KNEE_MIN <= position_degrees <= self.THETA_KNEE_MAX:
            # Invalid Position!  TODO: Log error!
            return

        self.theta_knee = position_degrees

        # Position angles need to be inverted on the LHS
        if self.side == 'L':
            position_degrees = -position_degrees
            
        return position_degrees

    def get_knee_raw_pos(self, position_degrees):
        position_degrees = self.verify_knee_angle(position_degrees)
        return XYZrobotServo.get_raw_position(position_degrees)

    def go_knee_angle(self, position_degrees, speed):
        """Set the position of the knee, relative to the thigh

        Args:
            position_degrees (int): Can be between 15 degrees and 160 degrees. 
            speed (uint8): Time in 10ms units to respond to new position
        """
        
        position_degrees = self.verify_knee_angle(position_degrees)
        self.knee_stream.set_position_deg(position_degrees, speed)

    def set_desired(self, x, y, z, speed=None):
        self.desired_x = x
        self.desired_y = y
        self.desired_z = z
        if speed is not None:
            self.desired_speed = speed
        self.desired_done = False

    def set_desired_to_current(self):
        """ Sets the desired setpoint variables equal to the current position
        """
        self.desired_x = self.x
        self.desired_y = self.y
        self.desired_z = self.z
        self.desired_speed = self.speed

    def verify_desired(self):
        x = self.desired_x
        y = self.desired_y
        z = self.desired_z
        # playtime = self.desired_speed
        
        theta_shoulder, theta_thigh, theta_knee = self.calc_position(x, y, z)
        return theta_shoulder, theta_thigh, theta_knee
    

    def go_desired(self):
        """Moves leg to the desired pos_x, pos_y, pos_z positions.  Make sure you set these variables first before calling this function

        Args:
            speed (int, between 0-255): Desired movement time, in units of 10ms
        """
        self.go_position(self.desired_x, self.desired_y, self.desired_z, self.desired_speed)
        self.desired_done = True

    def calc_position(self, X, Y, Z):
        """Returns tulpe of (theta_shoulder, theta_thigh, theta_knee).  Also sets calc_theta values

        Args:
            X (int or float): Desired X position
            Y (int or float): Desired Y position
            Z (int or float): Desired Z position
        """
        neg_X = False
        if X<0:
            neg_X = True
            X = abs(X)

        # TODO: Should this be here?
        X = X+self.SHOULDER_LENGTH

        if X == 0.0:
            X = 0.001
        if Y == 0.0:
            Y = 0.001

        try:

            # Leg length l
            h = math.sqrt(X*X + Z*Z)
            s = Leg.SHOULDER_LENGTH
            theta_1_rad = math.atan(Z/X)
            theta_2_rad = math.acos(s/h)
            theta_shoulder = math.degrees(theta_2_rad-theta_1_rad)

            l_xz = h*math.sin(theta_2_rad)
            l = math.sqrt((l_xz*l_xz)+(Y*Y))

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
            theta_thigh = (theta_knee/2)-theta_thigh_offset

        except ValueError:
            print("Math error trying to move to: {}, {}, {}".format(X, Y, Z))
            return False

        self.calc_theta_shoulder = theta_shoulder
        self.calc_theta_thigh = theta_thigh
        self.calc_theta_knee = theta_knee

        return (theta_shoulder, theta_thigh, theta_knee)

    def calc_desired(self):
        return self.calc_position(self.desired_x, self.desired_y, self.desired_z)
        
    def go_position(self, X, Y, Z, speed):
        """Sets the X, Y, Z position of each individual leg. X, Y, Z is specific to the shoulder.

        Args:
            X (int or float): Desired X position
            Y (int or float): Desired Y position
            Z (int or float): Desired Z position
            speed (int, between 0-255): Desired movement time, in units of 10ms
        """

        self.x = X
        self.y = Y
        self.z = Z
        self.speed = speed

        theta_shoulder, theta_thigh, theta_knee = self.calc_position(X, Y, Z)
       
        self.go_shoulder_angle(theta_shoulder, speed)
        self.go_thigh_angle(theta_thigh, speed)
        self.go_knee_angle(theta_knee, speed)
        