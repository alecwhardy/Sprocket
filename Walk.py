import time

# Forward
# // RR 4                RF 2                LR 3                     LF 1
# // RR leg UP        // RF leg DOWN      // LR leg DOWN           // LF leg UP
# // RR leg FRONT     // RF leg BACK      // LR leg BACK           // LF leg FRONT
# // RR leg DOWN      // RF leg UP        // LR leg UP             // LF leg DOWN
# // RR leg BACK      // RF leg FRONT     // LR leg FRONT          // LF leg BACK


def crude_walk_forward(dog, num_steps, step_len, speed):

    cur_step = 0
    cur_z = dog.z

    # set all legs to neutral position
    for leg in dog.legs:
        leg.go_position(0, 0, cur_z, 20)

    # Tuples of go_position arguments
    UP = (0, 0, cur_z-step_len, speed)
    DOWN = (0, 0, cur_z, speed)
    FRONT = (0, -step_len, cur_z-step_len, speed)
    BACK = (0, step_len, cur_z-step_len, speed)

    RR = 4-1
    RF = 2-1
    LR = 3-1
    LF = 1-1

    sleeptime = .25

    while cur_step < num_steps:

        # // RR leg UP        // RF leg DOWN      // LR leg DOWN           // LF leg UP
        dog.legs[RR].go_position(*UP)
        dog.legs[RF].go_position(*DOWN)
        dog.legs[LR].go_position(*DOWN)
        dog.legs[LF].go_position(*UP)
        time.sleep(sleeptime)

        # // RR leg FRONT     // RF leg BACK      // LR leg BACK           // LF leg FRONT
        dog.legs[RR].go_position(*FRONT)
        dog.legs[RF].go_position(*BACK)
        dog.legs[LR].go_position(*BACK)
        dog.legs[LF].go_position(*FRONT)
        time.sleep(sleeptime)

        # // RR leg DOWN      // RF leg UP        // LR leg UP             // LF leg DOWN
        dog.legs[RR].go_position(*DOWN)
        dog.legs[RF].go_position(*UP)
        dog.legs[LR].go_position(*UP)
        dog.legs[LF].go_position(*DOWN)
        time.sleep(sleeptime)

        # // RR leg BACK      // RF leg FRONT     // LR leg FRONT          // LF leg BACK
        dog.legs[RR].go_position(*BACK)
        dog.legs[RF].go_position(*FRONT)
        dog.legs[LR].go_position(*FRONT)
        dog.legs[LF].go_position(*BACK)
        time.sleep(sleeptime)

        
        # # FL and RR lift
        # dog.legs[1-1].go_position(0, 0, cur_z-step_len, speed)
        # dog.legs[4-1].go_position(0, 0, cur_z-step_len, speed)
        # time.sleep(.25)
        
        # # FR and RL go normal, FL and RR extend out
        # dog.legs[2-1].go_position(0, 0, cur_z, speed)
        # dog.legs[3-1].go_position(0, 0, cur_z, speed)
        
        # dog.legs[1-1].go_position(0, -step_len, cur_z-step_len, speed)
        # dog.legs[4-1].go_position(0, -step_len, cur_z-step_len, speed)
        # time.sleep(.25)
        # dog.legs[1-1].go_position(0, -step_len, cur_z, speed)
        # dog.legs[4-1].go_position(0, -step_len, cur_z, speed)

        # # FR and RL lift, FL and RR go normal
        # dog.legs[2-1].go_position(0, 0, cur_z-step_len, speed)
        # dog.legs[3-1].go_position(0, 0, cur_z-step_len, speed)

        # dog.legs[1-1].go_position(0, 0, cur_z, speed)
        # dog.legs[4-1].go_position(0, 0, cur_z, speed)
        # time.sleep(.25)

        # # FR and RL extend out
        # dog.legs[2-1].go_position(0, -step_len, cur_z-step_len, speed)
        # dog.legs[3-1].go_position(0, -step_len, cur_z-step_len, speed)
        # time.sleep(.25)
        # dog.legs[2-1].go_position(0, -step_len, cur_z, speed)
        # dog.legs[3-1].go_position(0, -step_len, cur_z, speed)

        # time.sleep(.25)
        # cur_step += 1

