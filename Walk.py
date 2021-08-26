import time

IN_PLACE = 0
FORWARD = 1
SIDE_RIGHT = 2
SIDE_LEFT = 3
TURN_RIGHT = 4
TURN_LEFT = 5

# Leg IDs, for using dog.legs[]
RR = 4-1
RF = 2-1
LR = 3-1
LF = 1-1


def crude_walk(dog, direction, num_steps, step_len, lift_amount, playtime):

    cur_step = 0
    cur_z = dog.z

    # set all legs to neutral position
    for leg in dog.legs:
        leg.go_position(0, 0, cur_z, 20)

    # Tuples of go_position arguments  
    UP         = (        0,         0, cur_z-lift_amount, playtime)
    DOWN       = (        0,         0,             cur_z, playtime)
    FRONT      = (        0, -step_len, cur_z-lift_amount, playtime)
    BACK       = (        0,  step_len,             cur_z, playtime)
    IN_UP_R    = (-step_len,         0, cur_z-lift_amount, playtime)
    IN_DOWN_R  = (-step_len,         0,             cur_z, playtime)
    IN_UP_L    = ( step_len,         0, cur_z-lift_amount, playtime)
    IN_DOWN_L  = ( step_len,         0,             cur_z, playtime)
    OUT_UP_R   = ( step_len,         0, cur_z-lift_amount, playtime)
    OUT_DOWN_R = ( step_len,         0,             cur_z, playtime)
    OUT_UP_L   = (-step_len,         0, cur_z-lift_amount, playtime)
    OUT_DOWN_L = (-step_len,         0,             cur_z, playtime)

    # Tuples of UP, DOWN, FRONT, BACK XYZ coordinates
    # We can now unpack the tuple and use it as arguments with the * operator
    # for example: dog.legs[RR].go_position(*set_positions["FRONT"])
    set_positions = {
        "UP": UP, 
        "DOWN": DOWN, 
        "FRONT": FRONT, 
        "BACK": BACK, 
        "IN_UP_R": IN_UP_R,
        "IN_UP_L": IN_UP_L,
        "IN_DOWN_L": IN_DOWN_L,
        "IN_DOWN_R": IN_DOWN_R,
        "OUT_UP_R": OUT_UP_R, 
        "OUT_UP_L": OUT_UP_L, 
        "OUT_DOWN_R": OUT_DOWN_R, 
        "OUT_DOWN_L": OUT_DOWN_L
    }

    sleeptime = playtime/100

    while cur_step < num_steps:

        # I can override the set_positions dictionary entries for UP, DOWN, IN, etc. here
        # Do something like set_positions["IN"] = (X, Y, Z, speed)
        if direction == FORWARD:
            _crude_step_forward(dog, set_positions, sleeptime)

        elif direction == IN_PLACE:
            _crude_step_in_place(dog, set_positions, sleeptime)

        elif direction == SIDE_LEFT:
            _crude_step_side_left(dog, set_positions, sleeptime)

        elif direction == SIDE_RIGHT:
            _crude_step_side_right(dog, set_positions, sleeptime)

        elif direction == TURN_LEFT:
            _crude_step_turn_left(dog, set_positions, sleeptime)

        elif direction == TURN_RIGHT:
            _crude_step_turn_right(dog, set_positions, sleeptime)
            
        cur_step += 1


def _crude_step_forward(dog, set_positions, sleeptime):
    #  RR leg UP         RF leg DOWN       LR leg DOWN            LF leg UP
    dog.legs[RR].go_position(*set_positions["UP"])
    dog.legs[RF].go_position(*set_positions["DOWN"])
    dog.legs[LR].go_position(*set_positions["DOWN"])
    dog.legs[LF].go_position(*set_positions["UP"])
    time.sleep(sleeptime)

    #  RR leg FRONT      RF leg BACK       LR leg BACK            LF leg FRONT
    dog.legs[RR].go_position(*set_positions["FRONT"])
    dog.legs[RF].go_position(*set_positions["BACK"])
    dog.legs[LR].go_position(*set_positions["BACK"])
    dog.legs[LF].go_position(*set_positions["FRONT"])
    time.sleep(sleeptime)

    #  RR leg DOWN       RF leg UP         LR leg UP              LF leg DOWN
    dog.legs[RR].go_position(*set_positions["DOWN"])
    dog.legs[RF].go_position(*set_positions["UP"])
    dog.legs[LR].go_position(*set_positions["UP"])
    dog.legs[LF].go_position(*set_positions["DOWN"])
    time.sleep(sleeptime)

    #  RR leg BACK       RF leg FRONT      LR leg FRONT           LF leg BACK
    dog.legs[RR].go_position(*set_positions["BACK"])
    dog.legs[RF].go_position(*set_positions["FRONT"])
    dog.legs[LR].go_position(*set_positions["FRONT"])
    dog.legs[LF].go_position(*set_positions["BACK"])
    time.sleep(sleeptime)

def _crude_step_in_place(dog, set_positions, sleeptime):

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


def _crude_step_side_left(dog, set_positions, sleeptime):
    
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


def _crude_step_side_right(dog, set_positions, sleeptime):
    
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

def _crude_step_turn_left(dog, set_positions, sleeptime):
    
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

def _crude_step_turn_right(dog, set_positions, sleeptime):
    
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
