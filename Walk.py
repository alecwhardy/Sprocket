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

    
class Crude_Gait:
    """Takes a direction "IN_PLACE", "FORWARD", "SIDE_RIGHT", ... etc.

    Returns:
        _type_: _description_
    """

    NAME = "CRUDE_GAIT"

    IN_PLACE = 0
    FORWARD = 1
    SIDE_RIGHT = 2
    SIDE_LEFT = 3
    TURN_RIGHT = 4
    TURN_LEFT = 5
    BACKWARD = 6
    STILL = 10

    state = 1
    direction = STILL

    compass_dir = None

    def reset(self):
        self.state = 1
    
    def walk(self, dog, direction):
        """ All Gait classes must define walk()

        Args:
            dog ([type]): [description]
            direction ([type]): [description]
        """
        self.crude_walk(dog, direction)

        # Update the compass dur if it isn't set
        if direction == self.STILL:
            self.compass_dir = None
        elif self.compass_dir is None and direction == self.FORWARD:
            # We are not still but the compass dir is None, so we must be starting a new walk
            # Record the compass direction so we can auto-trim to maintain it.
            self.compass_dir = dog.sensor_yaw

    # This will ultimately be "get variable"
    def get_set_position(self, position):
        return self.set_positions[position]

    # This will ultimately be "update variable"
    def update_set_position(self, position, values):
        self.set_positions[position] = values

    # This will ultimately be "update_variables"
    def update_set_positions(self, dog, step_len, lift_amount, playtime, r_trim = 0, f_trim=0):
        """ Automatically calculate the set_positions table from the provided arguments.  Use dog for cur_z value.

        f_trim: extra lift for front UP movements.  Make this positive? if the back lifts more

        Args:
            dog ([type]): [description]
            step_len ([type]): [description]
            lift_amount ([type]): [description]
            playtime ([type]): [description]
        """
        cur_z = dog.z
        y_offset = dog.desired_y

        # Tuples of UP, DOWN, FRONT, BACK XYZ coordinates
        # We can now unpack the tuple and use it as arguments with the * operator
        # for example: dog.legs[RR].go_position(*set_positions["FRONT"])
        self.set_positions = {
            "UP"           : (        0,         0+y_offset       , cur_z-lift_amount       , playtime),
            "UP_F"         : (        0,         0+y_offset       , cur_z-lift_amount-f_trim, playtime),  # Front
            "DOWN"         : (        0,         0+y_offset       ,             cur_z       , playtime), 
            "FORWARD_UP"   : (        0, -step_len+y_offset       , cur_z-lift_amount       , playtime),
            "FORWARD_UP_F" : (        0, -step_len+y_offset       , cur_z-lift_amount       , playtime),  # Front
            "FORWARD_DOWN" : (        0, -step_len+y_offset       ,             cur_z       , playtime), 
            "BACK_DOWN_L"  : (        0,  step_len+y_offset       ,             cur_z       , playtime),
            "BACK_DOWN_R"  : (        0,  step_len+y_offset+r_trim,             cur_z       , playtime),
            "BACK_UP"      : (        0,  step_len+y_offset       , cur_z-lift_amount       , playtime), 
            "BACK_UP_F"    : (        0,  step_len+y_offset       , cur_z-lift_amount       , playtime),  # Front
            "IN_UP_R"      : (-step_len,         0+y_offset       , cur_z-lift_amount       , playtime),
            "IN_UP_L"      : ( step_len,         0+y_offset       , cur_z-lift_amount       , playtime),
            "IN_DOWN_L"    : ( step_len,         0+y_offset       ,             cur_z       , playtime),
            "IN_DOWN_R"    : (-step_len,         0+y_offset       ,             cur_z       , playtime),
            "OUT_UP_R"     : ( step_len,         0+y_offset       , cur_z-lift_amount       , playtime), 
            "OUT_UP_L"     : (-step_len,         0+y_offset       , cur_z-lift_amount       , playtime), 
            "OUT_DOWN_R"   : ( step_len,         0+y_offset       ,             cur_z       , playtime), 
            "OUT_DOWN_L"   : (-step_len,         0+y_offset       ,             cur_z       , playtime)
        }


    def manual_set_positions(self, set_positions):
        """ Manually specify the set_positions table with raw values

        Args:
            set_positions (dictionary): set_positions
        """
        self.set_positions = set_positions
    
    
    def crude_walk(self, dog, direction):
        """ 

        Args:
            dog ([type]): [description]
            direction ([type]): [description]
            
        """

        cur_z = dog.z

        # set all legs to neutral position
        # for leg in dog.legs:
        #     leg.go_position(0, 0, cur_z, 20)

        playtime = self.set_positions["UP"][3]
        sleeptime = playtime/100  # Playtime is in terms of 10ms, so this sets sleeptime = playtime

        sleeptime += 0.01         # Give the motors 1ms extra to get to their new positions

        # See what direction we were going last time, if different reset state
        if direction != self.direction:
            self.state = 1
        
        # Update what direction we are traveling/traveled so we can use it later
        self.direction = direction
        
        # Override the set_positions dictionary entries for UP, DOWN, IN, etc. here
        # Do something like set_positions["IN"] = (X, Y, Z, speed)
        if direction == self.FORWARD:
            '''
            forward_set_positions = self.set_positions.copy()
            
            # Apply an offset to correct robot turning slightly while walking forward
            old = forward_set_positions["BACK_DOWN_L"]
            corrected_position = (old[0], int(1.05*old[1]), old[2], old[3])
            forward_set_positions["BACK_DOWN_L"] = corrected_position

             self._crude_step_forward(dog, forward_set_positions, sleeptime)
            '''

            self._crude_step_forward(dog, self.set_positions, sleeptime)

        if direction == self.BACKWARD:
            self._crude_step_backward(dog, self.set_positions, sleeptime)

        elif direction == self.IN_PLACE:
            self._crude_step_in_place(dog, self.set_positions, sleeptime)

        elif direction == self.SIDE_LEFT:
            self._crude_step_side_left(dog, self.set_positions, sleeptime)

        elif direction == self.SIDE_RIGHT:
            self._crude_step_side_right(dog, self.set_positions, sleeptime)

        elif direction == self.TURN_LEFT:
            self._crude_step_turn_left(dog, self.set_positions, sleeptime)

        elif direction == self.TURN_RIGHT:
            self._crude_step_turn_right(dog, self.set_positions, sleeptime)

        elif direction == self.STILL:
            self._crude_still(dog, self.set_positions, sleeptime)
            
        self.state += 1
        if self.state > 4:
            self.state = 1


    def _crude_still(self, dog, set_positions, sleeptime):
        
        self.state = 1

        dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
        dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
        dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
        dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
        dog.motion.request_delay(sleeptime)

        # dog.legs[RR].go_position(*set_positions["DOWN"])
        # dog.legs[RF].go_position(*set_positions["DOWN"])
        # dog.legs[LR].go_position(*set_positions["DOWN"])
        # dog.legs[LF].go_position(*set_positions["DOWN"])
        # time.sleep(sleeptime)


    def _crude_step_forward(self, dog, set_positions, sleeptime):
        
        if self.state == 1:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)

        if self.state == 2:
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["FORWARD_UP_F"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["BACK_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["BACK_DOWN_L"])
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["FORWARD_UP"])
            dog.motion.request_delay(sleeptime)

        if self.state == 3:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)

        if self.state == 4:
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["BACK_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["FORWARD_UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["FORWARD_UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["BACK_DOWN_L"])
            dog.motion.request_delay(sleeptime)
            

    def _crude_step_backward(self, dog, set_positions, sleeptime):
        
        if self.state == 1:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)

        if self.state == 2:
            #  RR leg FRONT      RF leg BACK       LR leg BACK            LF leg FRONT
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["BACK_UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["FORWARD_DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["FORWARD_DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["BACK_UP_F"])
            dog.motion.request_delay(sleeptime)

        if self.state == 3:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)

        if self.state == 4:
            #  RR leg BACK       RF leg FRONT      LR leg FRONT           LF leg BACK
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["FORWARD_DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["BACK_UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["BACK_UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["FORWARD_DOWN"])
            dog.motion.request_delay(sleeptime)

    def _crude_step_in_place(self, dog, set_positions, sleeptime):

        if self.state == 1:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 2:
            #  RR leg DOWN       RF leg DOWN       LR leg DOWN            LF leg DOWN  
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)
            
        if self.state == 3:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)

        if self.state == 4:
            #  RR leg DOWN       RF leg DOWN       LR leg DOWN            LF leg DOWN 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)
            

    def _crude_step_side_left(self, dog, set_positions, sleeptime):
        
        if self.state == 1:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)

        if self.state == 2:
            #  RR leg OUT        RF leg IN         LR leg OUT             LF leg IN
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["OUT_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["IN_UP_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["OUT_UP_L"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["IN_DOWN_L"])
            dog.motion.request_delay(sleeptime)

        if self.state == 3:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)

        if self.state == 4:
            #  RR leg IN         RF leg OUT        LR leg IN              LF leg OUT
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["IN_UP_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["OUT_DOWN_R"])  # F Right leg is down and swings outwards (+x for Right side)
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["IN_DOWN_L"])   # R Left  leg is down and swings inwards  (+x for Left side)
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["OUT_UP_L"])
            dog.motion.request_delay(sleeptime)


    def _crude_step_side_right(self, dog, set_positions, sleeptime):
        
        if self.state == 1:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 2:
            #  RR leg OUT        RF leg IN         LR leg OUT             LF leg IN 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["OUT_UP_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["IN_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["OUT_DOWN_L"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["IN_UP_L"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 3:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 4:
            #  RR leg IN         RF leg OUT        LR leg IN              LF leg OUT 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["IN_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["OUT_UP_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["IN_UP_L"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["OUT_DOWN_L"])
            dog.motion.request_delay(sleeptime)   
            

    def _crude_step_turn_left(self, dog, set_positions, sleeptime):
        
        if self.state == 1:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 2:
            #  RR leg OUT        RF leg OUT        LR leg OUT             LF leg OUT
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["OUT_UP_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["OUT_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["OUT_DOWN_L"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["OUT_UP_L"])
            dog.motion.request_delay(sleeptime)
            
        
        if self.state == 3:
            #  RR leg DOWN       RF leg UP         LR leg UP            LF leg DOWN 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 4:
            #  RR leg IN         RF leg IN         LR leg IN              LF leg IN
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["IN_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["IN_UP_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["IN_UP_L"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["IN_DOWN_L"])
            dog.motion.request_delay(sleeptime)
            

    def _crude_step_turn_right(self, dog, set_positions, sleeptime):
        
        if self.state == 1:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["UP_F"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["DOWN"])
            dog.motion.request_delay(sleeptime)

        if self.state == 2:
           
            
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["OUT_DOWN_L"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["OUT_UP_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["OUT_UP_L"])
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["OUT_DOWN_R"])
            dog.motion.request_delay(sleeptime)
            
        
        if self.state == 3:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["UP"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["DOWN"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["UP_F"])
            dog.motion.request_delay(sleeptime)
        
        if self.state == 4:
            #  RR leg IN         RF leg IN         LR leg IN              LF leg IN 
            dog.motion.request_absolute_leg(Leg.RR, *set_positions["IN_UP_R"])
            dog.motion.request_absolute_leg(Leg.FR, *set_positions["IN_DOWN_R"])
            dog.motion.request_absolute_leg(Leg.RL, *set_positions["IN_DOWN_L"])
            dog.motion.request_absolute_leg(Leg.FL, *set_positions["IN_UP_L"])
            dog.motion.request_delay(sleeptime)

class Crude_Balanced_Gait:

    NAME = "CRUDE_BALANCED_GAIT"

    MAX_EXTENSION_X = 30 # Max amount the leg can move in or out in the X-direction
    MAX_EXTENSION_Y = 50 # Max amount the leg can move forward or backwards in Y-direction
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
        # Note:  If we do not explitly define all 4 different dictionaries (ie. using [{}]*4, then all dictionaries have the same ID (same object))
        {
            "DOWN"     : [0, 0, 0, 0],
            "UP"       : [0, 0, 0, 0],
            "UP_EXT"   : [0, 0, 0, 0],
            "DOWN_EXT" : [0, 0, 0, 0]
        },
        {
            "DOWN"     : [0, 0, 0, 0],
            "UP"       : [0, 0, 0, 0],
            "UP_EXT"   : [0, 0, 0, 0],
            "DOWN_EXT" : [0, 0, 0, 0]
        },
        {
            "DOWN"     : [0, 0, 0, 0],
            "UP"       : [0, 0, 0, 0],
            "UP_EXT"   : [0, 0, 0, 0],
            "DOWN_EXT" : [0, 0, 0, 0]
        },
        {
            "DOWN"     : [0, 0, 0, 0],
            "UP"       : [0, 0, 0, 0],
            "UP_EXT"   : [0, 0, 0, 0],
            "DOWN_EXT" : [0, 0, 0, 0]
        },
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
        },
        {
            "DOWN"         : (0, 0, 150, 10),
            "UP"           : (0, 0, 100, 10),
            "UP_EXT_IN"    : (0, 0, 100, 10),
            "UP_EXT_OUT"   : (0, 0, 100, 10),
            "DOWN_EXT_IN"  : (0, 0, 150, 10),
            "DOWN_EXT_OUT" : (0, 0, 150, 10)
        },
        {
            "DOWN"         : (0, 0, 150, 10),
            "UP"           : (0, 0, 100, 10),
            "UP_EXT_IN"    : (0, 0, 100, 10),
            "UP_EXT_OUT"   : (0, 0, 100, 10),
            "DOWN_EXT_IN"  : (0, 0, 150, 10),
            "DOWN_EXT_OUT" : (0, 0, 150, 10)
        },
        {
            "DOWN"         : (0, 0, 150, 10),
            "UP"           : (0, 0, 100, 10),
            "UP_EXT_IN"    : (0, 0, 100, 10),
            "UP_EXT_OUT"   : (0, 0, 100, 10),
            "DOWN_EXT_IN"  : (0, 0, 150, 10),
            "DOWN_EXT_OUT" : (0, 0, 150, 10)
        }
    ]

    def reset(self):
        self.state = 1

    def calc_setpoints(self, dog, direction):

        # Determine what positions the legs would be in if the dog was stationary
        # Now, dog.legs[*].desired_* will be updated
        dog.calc_position(
            dog.x,
            dog.y,
            dog.z,
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