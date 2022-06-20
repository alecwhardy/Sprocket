import time
from Walk import Crude_Gait, Walk


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

    desired_x = 0
    desired_y = 0
    desired_z = 0
    desired_roll = 0
    desired_pitch = 0
    desired_yaw = 0
    desired_speed = 0

    def __init__(self, dog):
        self.dog = dog
        self.walk = Walk(self.dog, Crude_Gait)

    def request_absolute_position(self, x, y, z, roll, pitch, yaw, speed):
        
        if self.current_motion == self.STATIONARY:
            self.dog.go_position(x, y, z, roll, pitch, yaw, speed)

        # Do we want to update desired_* here?
        self.dog.x     = self.desired_x = x
        self.dog.y     = self.desired_y = y
        self.dog.z     = self.desired_z = z
        self.dog.roll  = self.desired_roll = roll
        self.dog.pitch = self.desired_pitch = pitch
        self.dog.yaw   = self.desired_yaw = yaw
    
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
        self.dog.x     = self.desired_x = new_x
        self.dog.y     = self.desired_y = new_y
        self.dog.z     = self.desired_z = new_z
        self.dog.roll  = self.desired_roll = new_roll
        self.dog.pitch = self.desired_pitch = new_pitch
        self.dog.yaw   = self.desired_yaw = new_yaw
        self.dog.speed = self.desired_speed = new_speed

    def request_absolute_leg(self, leg, x, y, z, speed):
        if self.current_motion == self.STATIONARY:
            # If we are stationary and request an absolute position, go there immediately
            self.dog.legs[leg].go_position(x, y, z, speed)

        else:
            # If we are walking/prancing, set the desired position and let update_motion move us there accordingly
            self.dog.legs[leg].set_desired(x, y, z, speed)

    def request_delay(self, delay):
        self.motion_delay = True
        self.motion_delay_time = delay

    def stop_walk(self):
        # Call this function when we are done walking so we reset back to a neutral position


        # TODO: DELETE THIS!!
        self.dog.dataplot.stop_recording()
        self.dog.dataplot.print_average_filtered()

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

    def do_walk(self, direction):

        """
        Make sure to call self.walk.gait.update_set_positions(dog, step_len, lift_amount, playtime) before calling this function!

        """

        self.last_motion = time.time()

        self.current_motion = self.WALK
        self.direction = direction

        self.walk.walk(direction)
        self.steps_remaining -= 1

    def update_motion(self):

        if not self.motion_enable:
            return

        # If we have a desired leg position that has not yet been handled
        for leg in self.dog.legs:
            if not leg.desired_done:
                leg.go_desired()
        
        if self.current_motion != self.STATIONARY:

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
        for leg in self.dog.legs:
            if not leg.desired_done:
                leg.go_desired()

            

class MotionRecordingServoPositionFrame:

    def __init__(self, servo_positions, duration_ms):
        self.positions = servo_positions
        self.duration = duration_ms

    
