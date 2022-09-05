import time

from Leg import Leg
from functions import *

# Leg IDs, for using dog.legs[]
RR = 4-1
RF = 2-1
LR = 3-1
LF = 1-1

class Walk:

    IN_PLACE = 0
    FORWARD = 1
    SIDE_RIGHT = 2
    SIDE_LEFT = 3
    TURN_RIGHT = 4
    TURN_LEFT = 5
    BACKWARD = 6
    STILL = 10

    def __init__(self, dog, gait): 
        self.dog = dog
        self.gait = gait()

    def walk(self, direction):
        self.gait.walk(self.dog, direction)

    def reset(self):
        self.gait.reset()


class Crude_Balanced_Gait:

    NAME = "CRUDE_BALANCED_GAIT"

    MAX_EXTENSION_X = 30 # Max amount the leg can move in or out in the X-direction
    MAX_EXTENSION_Y = 100 # Max amount the leg can move forward or backwards in Y-direction
    MAX_EXTENSION_YAW = 50
   
    direction_x = 0    # Magnitude of X-direction walking motion
    direction_y = 0    # Magnitude of Y-direction walking motion
    direction_yaw = 0  # Magnitude of rotation walking motion

    step_lift_amount = 50
    step_length = 0
    substep_time = 0.11         #Units of 1s
    substep_motion_playtime = 10 #Units of 10ms

    state = 0

    # Leg order (FL, FR, RL, RR)
    setpoint_modifiers = [
        # X, Y, Z, playtime modifiers for each leg for the four different substeps.  These are added to the setpoints during the calc_setpoints call
        {
            "DOWN"     : (0, 0, 0, 0),
            "UP"       : (0, 0, 0, 0),
            "UP_EXT"   : (0, 0, 0, 0),
            "DOWN_EXT" : (0, 0, 0, 0)
        } for _ in range(4)  # This weird syntax is used to create 4 unique dictionaries.  Otherwise, we create 4 references to the same dictionary.
    ]

    # Leg order (FL, FR, RL, RR)
    setpoints = [
        # Default setpoints have Z-height of 150 units, left height of 50 (Z-height = 100), motion playtime: 9 (90ms)
        # (X-pos, Y-pos, Z-pos, PlayTime (10ms))
        {
            "DOWN"         : (0, 0, 150, 10),
            "UP"           : (0, 0, 100, 10),
            "UP_EXT_IN"    : (0, 0, 100, 10),
            "UP_EXT_OUT"   : (0, 0, 100, 10),
            "DOWN_EXT_IN"  : (0, 0, 150, 10),
            "DOWN_EXT_OUT" : (0, 0, 150, 10)
        } for _ in range(4)
    ]

    def reset(self):
        self.state = 1

    def calc_setpoints(self, dog, direction):

        # Determine what positions the legs would be in if the dog was stationary, based on its current position
        # Now, dog.legs[*].desired_* will be updated
        # TODO: Update all desired variables?
        dog.calc_position(
            dog.x,
            dog.desired_y,
            dog.desired_z,
            dog.roll,
            dog.pitch,
            dog.yaw,
            dog.speed
        )

        # Determine the direction we want the dog to move in
        self.direction_x = lin_interp(-1.0, direction[0], 1.0, -self.MAX_EXTENSION_X, self.MAX_EXTENSION_X)
        self.direction_y = lin_interp(-1.0, direction[1], 1.0, -self.MAX_EXTENSION_Y, self.MAX_EXTENSION_Y)
        self.direction_yaw = lin_interp(-1.0, direction[2], 1.0, -self.MAX_EXTENSION_YAW, self.MAX_EXTENSION_YAW)

        playtime = self.substep_motion_playtime
        
        for leg_num, setpoint in enumerate(self.setpoints):

            if dog.legs[leg_num].side == 'L':
                x_rotational_offset = self.direction_yaw
            else:
                x_rotational_offset = -self.direction_yaw

            setpoint["DOWN"] = (
                dog.legs[leg_num].desired_x, 
                dog.legs[leg_num].desired_y, 
                dog.legs[leg_num].desired_z, 
                playtime)

            setpoint["UP"] = (
                dog.legs[leg_num].desired_x, 
                dog.legs[leg_num].desired_y, 
                dog.legs[leg_num].desired_z - self.step_lift_amount, 
                playtime)

            # We need the "OUT" and "IN" sub step states to account for rotation.  
            # During a rotation, during state 2, the legs all point inwards, and during state 4, the legs all point outwards.
            setpoint["UP_EXT_OUT"] = (
                dog.legs[leg_num].desired_x + x_rotational_offset + self.direction_x, 
                dog.legs[leg_num].desired_y - self.direction_y, 
                dog.legs[leg_num].desired_z - self.step_lift_amount, 
                playtime)

            setpoint["UP_EXT_IN"] = (
                dog.legs[leg_num].desired_x - x_rotational_offset + self.direction_x, 
                dog.legs[leg_num].desired_y - self.direction_y, 
                dog.legs[leg_num].desired_z - self.step_lift_amount, 
                playtime)

            setpoint["DOWN_EXT_OUT"] = (
                dog.legs[leg_num].desired_x + x_rotational_offset - self.direction_x, 
                dog.legs[leg_num].desired_y + self.direction_y, 
                dog.legs[leg_num].desired_z, 
                playtime)

            setpoint["DOWN_EXT_IN"] = (
                dog.legs[leg_num].desired_x - x_rotational_offset - self.direction_x, 
                dog.legs[leg_num].desired_y + self.direction_y, 
                dog.legs[leg_num].desired_z, 
                playtime)

                # TODO: FACTOR IN setpoint_modifiers!!!
            

    def walk(self, dog, direction):
        """ Allows the dog to walk when commanded a desired X-speed, Y-speed, and Turn-speed (Yaw-speed).
            When calculating leg positions, this walking gait also considers dog.desired_* variables, so the dog can walk but maintain a desired body-orientation.
            Optionally, dynamic balancing can be enabled to read IMU data and correct for natural purturbances.

        Args:
            direction (tuple): Tuple of desired X-speed (sideway step), Y-speed (forward/backward step), Yaw-speed (rotation)
        """

        if direction == Walk.STILL:
            self.state = 0
            direction = [0, 0, 0]
        else:
            if self.state == 0:
                self.state = 1
        self.calc_setpoints(dog, direction)

        if self.state == 0:
            dog.motion.request_absolute_leg(Leg.FL, *self.setpoints[Leg.FL]["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *self.setpoints[Leg.FR]["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *self.setpoints[Leg.RL]["DOWN"])
            dog.motion.request_absolute_leg(Leg.RR, *self.setpoints[Leg.RR]["DOWN"])
            dog.motion.request_delay(self.substep_time)
            return # We want to stay in state 0 unless we are forced to state 1 (start walking)
        
        elif self.state == 1:
            dog.motion.request_absolute_leg(Leg.FL, *self.setpoints[Leg.FL]["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *self.setpoints[Leg.FR]["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *self.setpoints[Leg.RL]["DOWN"])
            dog.motion.request_absolute_leg(Leg.RR, *self.setpoints[Leg.RR]["UP"])
            dog.motion.request_delay(self.substep_time)

        elif self.state == 2:
            dog.motion.request_absolute_leg(Leg.FL, *self.setpoints[Leg.FL]["UP_EXT_OUT"])
            dog.motion.request_absolute_leg(Leg.FR, *self.setpoints[Leg.FR]["DOWN_EXT_OUT"])
            dog.motion.request_absolute_leg(Leg.RL, *self.setpoints[Leg.RL]["DOWN_EXT_OUT"])
            dog.motion.request_absolute_leg(Leg.RR, *self.setpoints[Leg.RR]["UP_EXT_OUT"])
            dog.motion.request_delay(self.substep_time)

        elif self.state == 3:
            dog.motion.request_absolute_leg(Leg.FL, *self.setpoints[Leg.FL]["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *self.setpoints[Leg.FR]["UP"])
            dog.motion.request_absolute_leg(Leg.RL, *self.setpoints[Leg.RL]["UP"])
            dog.motion.request_absolute_leg(Leg.RR, *self.setpoints[Leg.RR]["DOWN"])
            dog.motion.request_delay(self.substep_time)
        
        elif self.state == 4:
            dog.motion.request_absolute_leg(Leg.FL, *self.setpoints[Leg.FL]["DOWN_EXT_IN"])
            dog.motion.request_absolute_leg(Leg.FR, *self.setpoints[Leg.FR]["UP_EXT_IN"])
            dog.motion.request_absolute_leg(Leg.RL, *self.setpoints[Leg.RL]["UP_EXT_IN"])
            dog.motion.request_absolute_leg(Leg.RR, *self.setpoints[Leg.RR]["DOWN_EXT_IN"])
            dog.motion.request_delay(self.substep_time)

        self.state += 1
        if self.state > 4:
            self.state = 1