import time
from Walk import Crude_Balanced_Gait, Walk
from Walk_CrudeGait import Crude_Gait
from XYZrobotServo import XYZrobotServo


''' 
Immediate (stationary) moves can be immediate, but walking or other rfunctions that require constant, continuous calculation must be handled by this Motion handler
so that other things can happen in the "background".

'''

class Motion:

    STATIONARY = 0
    PRANCE = 1
    WALK = 2

    motion_enable = True
    
    current_motion = STATIONARY

    active_euler_correction = False
    
    walking = False
    steps_remaining = 0 # make this -1 for walking indefinitely
    direction = 0

    recording = False

    motion_delay = False
    motion_delay_time = 0
    last_motion = 0

    # The current positions are part of dog.x, dog.y, etc...

    IMU_history = []

    def __init__(self, dog):
        self.dog = dog
        # self.walk = Walk(self.dog, Crude_Gait)
        self.walk = Walk(self.dog, Crude_Balanced_Gait)

    def request_absolute_position(self, x, y, z, roll, pitch, yaw, speed):
        
        if self.current_motion == self.STATIONARY:
            self.dog.go_position(x, y, z, roll, pitch, yaw, speed)

        # Do we want to update desired_* here?
        self.dog.x     = x
        self.dog.y     = y
        self.dog.z     = z
        self.dog.roll  = roll
        self.dog.pitch = pitch
        self.dog.yaw   = yaw
    
    def request_relative_position(self, x, y, z, roll, pitch, yaw, speed):

        new_x = self.dog.x + x
        new_y = self.dog.y + y
        new_z = self.dog.z + z
        new_roll = self.dog.roll + roll
        new_pitch = self.dog.pitch + pitch
        new_yaw = self.dog.yaw + yaw
        new_speed = self.dog.speed + speed

        if self.current_motion == self.STATIONARY:
            self.dog.go_position(new_x, new_y, new_z, new_roll, new_pitch, new_yaw, new_speed)

        # TODO: If we are walking or prancing, update desired_* variables so that the walking algorithm takes into consideration the desired offsets.
        self.dog.x     = new_x
        self.dog.y     = new_y
        self.dog.z     = new_z
        self.dog.roll  = new_roll
        self.dog.pitch = new_pitch
        self.dog.yaw   = new_yaw
        self.dog.speed = new_speed

    def request_absolute_leg(self, leg, x, y, z, playtime):
        if self.current_motion == self.STATIONARY:
            # If we are stationary and request an absolute position, go there immediately
            self.dog.legs[leg].go_position(x, y, z, playtime)

        else:
            # If we are walking/prancing, set the desired position and let update_motion move us there accordingly
            self.dog.legs[leg].set_desired(x, y, z, playtime)

    def request_delay(self, delay):
        self.motion_delay = True
        self.motion_delay_time = delay

    def stop_walk(self):
        # Call this function when we are done walking so we reset back to a neutral position

        self.walk.walk(Walk.STILL)
        self.walk.reset()
        self.steps_remaining = 0

        self.current_motion = self.STATIONARY


    def stop_prance(self):
        self.stop_walk()

    def do_prance(self):

        self.last_motion = time.time()

        self.current_motion = self.PRANCE

        step_len = 30
        lift_amount = 50
        playtime = 12
        
        self.walk.gait.update_set_positions(self.dog, step_len, lift_amount, playtime)
        self.walk.walk(Walk.IN_PLACE)
        self.steps_remaining -= 1

    def update_walk(self, direction):
        self.direction = direction

    def do_walk(self, direction):

        """
        Make sure to call self.walk.gait.update_set_positions(dog, step_len, lift_amount, playtime) before calling this function!

        """

        # Calling Commands.walk rapidly resets last_motion every time, causing insufficient walk time per step.
        # Need to figure out how to call this function WITHOUT actually "doing" the walk
        self.last_motion = time.time()

        self.current_motion = self.WALK
        self.direction = direction

        self.walk.walk(direction)
        self.steps_remaining -= 1

    def move_legs_to_desired_sync(self):
        goto_positions = []
        for leg in self.dog.legs:
            if not leg.desired_done:
                leg.x = leg.desired_x
                leg.y = leg.desired_y
                leg.z = leg.desired_z
                leg.speed = leg.desired_speed
                
                theta_shoulder, theta_thigh, theta_knee = leg.verify_desired()
                
                goto_positions.append({'id': leg.shoulder_ID, 
                                       'goal': leg.get_shoulder_raw_pos(theta_shoulder), 
                                       'playtime': leg.desired_speed})
                
                goto_positions.append({'id': leg.knee_ID, 
                                       'goal': leg.get_knee_raw_pos(theta_knee), 
                                       'playtime': leg.desired_speed})
                
                goto_positions.append({'id': leg.thigh_ID, 
                                       'goal': leg.get_thigh_raw_pos(theta_thigh), 
                                       'playtime': leg.desired_speed})
                
                self.dog.servos.broadcast_setPosition(goto_positions)
                leg.desired_done = True
                #leg.go_desired()
                
        

    def update_motion(self):

        if not self.motion_enable:
            return

        # If we have a desired leg position that has not yet been handled
        self.move_legs_to_desired_sync()

        
        if self.current_motion == self.WALK or self.current_motion == self.PRANCE:

            # if we have a delay request, handle that
            if self.motion_delay:

                if self.last_motion + self.motion_delay_time >= time.time():
                    # Not ready to do movement
                    return
                else:
                    self.last_motion = time.time()
                    self.motion_delay = False

            # If we have remaining steps left, do them
            if self.steps_remaining != 0:
                if self.current_motion == self.PRANCE:
                    self.do_prance()
                if self.current_motion == self.WALK:
                    self.do_walk(self.direction)
            elif self.steps_remaining == 0:
                self.stop_walk()

        # Go to the new desired leg positions
        self.move_legs_to_desired_sync()

