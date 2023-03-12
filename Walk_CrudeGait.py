from Leg import Leg
from functions import *    

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
            self.compass_dir = dog.sensor_heading

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
