import time

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

    state = 0

    def __init__(self, set_positions = None):

        if set_positions is not None:
            self.manual_set_positions(set_positions)

    def manual_set_positions(self, set_positions):
        """ Manually specify the set_positions table with raw values

        Args:
            set_positions (dictionary): set_positions
        """
        self.set_positions = set_positions

    def update_set_positions(self, dog, step_len, lift_amount, playtime):
        """ Automatically calculate the set_positions table from the provided arguments.  Use dog for cur_z value.

        Args:
            dog ([type]): [description]
            step_len ([type]): [description]
            lift_amount ([type]): [description]
            playtime ([type]): [description]
        """
        cur_z = dog.z

        # Tuples of UP, DOWN, FRONT, BACK XYZ coordinates
        # We can now unpack the tuple and use it as arguments with the * operator
        # for example: dog.legs[RR].go_position(*set_positions["FRONT"])
        self.set_positions = {
            "UP"         : (        0,         0, cur_z-lift_amount, playtime), 
            "DOWN"       : (        0,         0,             cur_z, playtime), 
            "FRONT"      : (        0, -step_len, cur_z-lift_amount, playtime), 
            "BACK"       : (        0,  step_len,             cur_z, playtime), 
            "IN_UP_R"    : (-step_len,         0, cur_z-lift_amount, playtime),
            "IN_UP_L"    : ( step_len,         0, cur_z-lift_amount, playtime),
            "IN_DOWN_L"  : ( step_len,         0,             cur_z, playtime),
            "IN_DOWN_R"  : (-step_len,         0,             cur_z, playtime),
            "OUT_UP_R"   : ( step_len,         0, cur_z-lift_amount, playtime), 
            "OUT_UP_L"   : (-step_len,         0, cur_z-lift_amount, playtime), 
            "OUT_DOWN_R" : ( step_len,         0,             cur_z, playtime), 
            "OUT_DOWN_L" : (-step_len,         0,             cur_z, playtime)
        }


    def crude_walk(self, dog, direction, num_steps):
        """ Walks a pre-defined number of steps in the specified direction.  The dog will NOT stop walking until all of the steps are done.

        Args:
            dog ([type]): [description]
            direction ([type]): [description]
            num_steps ([type]): [description]
        """

        cur_step = 0
        cur_z = dog.z

        global state

        # set all legs to neutral position
        for leg in dog.legs:
            leg.go_position(0, 0, cur_z, 20)

        playtime = self.set_positions["UP"][3]
        sleeptime = playtime/100

        state = 1

        while cur_step < num_steps:

            # I can override the set_positions dictionary entries for UP, DOWN, IN, etc. here
            # Do something like set_positions["IN"] = (X, Y, Z, speed)
            if direction == self.FORWARD:
                self._crude_step_forward(dog, self.set_positions, sleeptime)

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
                
            state += 1
            if state > 4:
                state = 1
                cur_step += 1


    def _crude_step_forward(self, dog, set_positions, sleeptime):
        
        global state
        
        if state == 1:
            #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
            dog.legs[RR].go_position(*set_positions["UP"])
            dog.legs[RF].go_position(*set_positions["DOWN"])
            dog.legs[LR].go_position(*set_positions["DOWN"])
            dog.legs[LF].go_position(*set_positions["UP"])
            time.sleep(sleeptime)

        if state == 2:
            #  RR leg FRONT      RF leg BACK       LR leg BACK            LF leg FRONT
            dog.legs[RR].go_position(*set_positions["FRONT"])
            dog.legs[RF].go_position(*set_positions["BACK"])
            dog.legs[LR].go_position(*set_positions["BACK"])
            dog.legs[LF].go_position(*set_positions["FRONT"])
            time.sleep(sleeptime)

        if state == 3:
            #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
            dog.legs[RR].go_position(*set_positions["DOWN"])
            dog.legs[RF].go_position(*set_positions["UP"])
            dog.legs[LR].go_position(*set_positions["UP"])
            dog.legs[LF].go_position(*set_positions["DOWN"])
            time.sleep(sleeptime)

        if state == 4:
            #  RR leg BACK       RF leg FRONT      LR leg FRONT           LF leg BACK
            dog.legs[RR].go_position(*set_positions["BACK"])
            dog.legs[RF].go_position(*set_positions["FRONT"])
            dog.legs[LR].go_position(*set_positions["FRONT"])
            dog.legs[LF].go_position(*set_positions["BACK"])
            time.sleep(sleeptime)

    def _crude_step_in_place(self, dog, set_positions, sleeptime):

        #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
        dog.legs[RR].go_position(*set_positions["UP"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["UP"])
        time.sleep(sleeptime)
        
        #  RR leg DOWN       RF leg DOWN       LR leg DOWN            LF leg DOWN  
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)

        #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN 
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["UP"])
        dog.legs[LR].go_position(*set_positions["UP"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)

        #  RR leg DOWN       RF leg DOWN       LR leg DOWN            LF leg DOWN 
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)


    def _crude_step_side_left(self, dog, set_positions, sleeptime):
        
        #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["UP"])
        dog.legs[LR].go_position(*set_positions["UP"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)

        #  RR leg OUT        RF leg IN         LR leg OUT             LF leg IN
        dog.legs[RR].go_position(*set_positions["OUT_DOWN_R"])
        dog.legs[RF].go_position(*set_positions["IN_UP_R"])
        dog.legs[LR].go_position(*set_positions["OUT_UP_L"])
        dog.legs[LF].go_position(*set_positions["IN_DOWN_L"])
        time.sleep(sleeptime)

        #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
        dog.legs[RR].go_position(*set_positions["UP"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["UP"])
        time.sleep(sleeptime)

        #  RR leg IN         RF leg OUT        LR leg IN              LF leg OUT
        dog.legs[RR].go_position(*set_positions["IN_UP_R"])
        dog.legs[RF].go_position(*set_positions["OUT_DOWN_R"])
        dog.legs[LR].go_position(*set_positions["IN_DOWN_L"])
        dog.legs[LF].go_position(*set_positions["OUT_UP_L"])
        time.sleep(sleeptime)   


    def _crude_step_side_right(self, dog, set_positions, sleeptime):
        
        #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
        dog.legs[RR].go_position(*set_positions["UP"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["UP"])
        time.sleep(sleeptime)
        
        #  RR leg OUT        RF leg IN         LR leg OUT             LF leg IN 
        dog.legs[RR].go_position(*set_positions["OUT_UP_R"])
        dog.legs[RF].go_position(*set_positions["IN_DOWN_R"])
        dog.legs[LR].go_position(*set_positions["OUT_DOWN_L"])
        dog.legs[LF].go_position(*set_positions["IN_UP_L"])
        time.sleep(sleeptime)
        
        #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN 
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["UP"])
        dog.legs[LR].go_position(*set_positions["UP"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)
        
        #  RR leg IN         RF leg OUT        LR leg IN              LF leg OUT 
        dog.legs[RR].go_position(*set_positions["IN_DOWN_R"])
        dog.legs[RF].go_position(*set_positions["OUT_UP_R"])
        dog.legs[LR].go_position(*set_positions["IN_UP_L"])
        dog.legs[LF].go_position(*set_positions["OUT_DOWN_L"])
        time.sleep(sleeptime)

    def _crude_step_turn_left(self, dog, set_positions, sleeptime):
        
        #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
        dog.legs[RR].go_position(*set_positions["UP"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["UP"])
        time.sleep(sleeptime)
        
        #  RR leg OUT        RF leg OUT        LR leg OUT             LF leg OUT
        dog.legs[RR].go_position(*set_positions["OUT_UP_R"])
        dog.legs[RF].go_position(*set_positions["OUT_DOWN_R"])
        dog.legs[LR].go_position(*set_positions["OUT_DOWN_L"])
        dog.legs[LF].go_position(*set_positions["OUT_UP_L"])
        time.sleep(sleeptime)
        
        #  RR leg DOWN       RF leg UP         LR leg UP            LF leg DOWN 
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["UP"])
        dog.legs[LR].go_position(*set_positions["UP"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)
        
        #  RR leg IN         RF leg IN         LR leg IN              LF leg IN
        dog.legs[RR].go_position(*set_positions["IN_DOWN_R"])
        dog.legs[RF].go_position(*set_positions["IN_UP_R"])
        dog.legs[LR].go_position(*set_positions["IN_UP_L"])
        dog.legs[LF].go_position(*set_positions["IN_DOWN_L"])
        time.sleep(sleeptime) 

    def _crude_step_turn_right(self, dog, set_positions, sleeptime):
        
        #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
        dog.legs[RR].go_position(*set_positions["DOWN"])
        dog.legs[RF].go_position(*set_positions["UP"])
        dog.legs[LR].go_position(*set_positions["UP"])
        dog.legs[LF].go_position(*set_positions["DOWN"])
        time.sleep(sleeptime)

        #  RR leg OUT        RF leg OUT        LR leg OUT             LF leg OUT
        dog.legs[RR].go_position(*set_positions["OUT_DOWN_R"])
        dog.legs[RF].go_position(*set_positions["OUT_UP_R"])
        dog.legs[LR].go_position(*set_positions["OUT_UP_L"])
        dog.legs[LF].go_position(*set_positions["OUT_DOWN_L"])
        time.sleep(sleeptime)
        
        #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
        dog.legs[RR].go_position(*set_positions["UP"])
        dog.legs[RF].go_position(*set_positions["DOWN"])
        dog.legs[LR].go_position(*set_positions["DOWN"])
        dog.legs[LF].go_position(*set_positions["UP"])
        time.sleep(sleeptime)
        
        #  RR leg IN         RF leg IN         LR leg IN              LF leg IN 
        dog.legs[RR].go_position(*set_positions["IN_UP_R"])
        dog.legs[RF].go_position(*set_positions["IN_DOWN_R"])
        dog.legs[LR].go_position(*set_positions["IN_DOWN_L"])
        dog.legs[LF].go_position(*set_positions["IN_UP_L"])
        time.sleep(sleeptime)
