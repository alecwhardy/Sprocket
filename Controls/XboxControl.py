import os
import time
from collections import deque

from xbox360controller import Xbox360Controller

from Commands import Command
from functions import *
from Walk import Walk
from Motion import Motion

# NOTE:  IF XBOX CONTROL IS ENABLED AND IN WALK MODE, CONSOLE COMMANDS WILL NOT WORK!!!

class XboxControl:

    CONNECTED = True
    CONTROL_ENABLE = False

    MODE_STATIONARY = 1
    MODE_WALK = 2

    STATIONARY_X_MULTIPLIER = 80
    STATIONARY_Y_MULTIPLIER = 80
    STATIONARY_Z_MULTIPLIER = 10

    # How long to wait (in ms) between each Controller command
    UPDATE_PERIOD = 50

    last_update = 0

    axis_r = {
        'x' : 0,
        'y' : 0
    }
    axis_l = {
        'x' : 0,
        'y' : 0
    }

    do_sleep = False
    do_reboot = False
    do_reset_position = False

    walk_in_place = False

    def __init__(self, dog, controller_id = 0, axis_threshold = 0.1):

        self.dog = dog

        self.controller_id = controller_id
        self.mode = self.MODE_STATIONARY
        self.axis_threshold = axis_threshold

        os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')

        try:
            self.controller = Xbox360Controller(controller_id, axis_threshold=axis_threshold)
        except Exception:
            self.CONNECTED = False
            self.CONTROL_ENABLE = False
            return

        self.controller.button_mode.when_pressed = self.changeMode
        self.controller.button_select.when_pressed = self.button_select  # Back button, do servo reset
        self.controller.button_start.when_pressed = self.button_start    # Start Button, Connect or disconnect Xbox controller
        self.controller.button_x.when_pressed = self.button_x            # X button, toggle walk in place
        self.controller.button_y.when_pressed = self.button_y            # Y button, do sleep
        self.controller.button_a.when_pressed = self.button_a            # A button, do reset position
        self.controller.hat.when_moved = self.hat_pressed                # The D-pad is being pressed
        self.update_mode_led()

        self.last_update = millis()

    def button_select(self, button):
        if not self.CONTROL_ENABLE:
            return
        self.do_reboot = True
    
    def button_y(self, button):
        if not self.CONTROL_ENABLE:
            return
        self.do_sleep = True
    
    def button_x(self, button):
        if not self.CONTROL_ENABLE:
            return
        self.walk_in_place = not self.walk_in_place
        print(f"Walking in place: {self.walk_in_place}")

    def button_start(self, button):
        self.CONTROL_ENABLE = not self.CONTROL_ENABLE
        print("Xbox Controller Control Enable: {}".format(self.CONTROL_ENABLE))

    def button_a(self, button):
        if not self.CONTROL_ENABLE:
            return
        self.do_reset_position = True

    def hat_pressed(self, hat):
        
        if not self.CONTROL_ENABLE:
            return
        
        # if self.controller.button_trigger_r.is_pressed and (hat.y == 1 or hat.y == -1):
        #     # Pressed UP or DOWN with R trigger button
        #     self.front_trim += hat.y
        #     print("Front Step Length Trim: {}".format(self.front_trim))
        #     return

        # elif self.controller.button_trigger_l.is_pressed and (hat.y == 1 or hat.y == -1):
        #     # Pressed UP or DOWN with L trigger button
        #     self.y_offset += hat.y
        #     print("Y-Offset: {}".format(self.y_offset))
        #     return
        
        # elif hat.y == 1 or hat.y == -1:
        #     # Pressed UP or DOWN
        #     self.step_height += hat.y
        #     print("Step height: {}".format(self.step_height))
        #     return
        
        # elif hat.x == 1 or hat.x == -1:
        #     # Pressed RIGHT or LEFT
        #     self.playtime += hat.x
        #     print("Playtime: {}".format(self.playtime))
        #     return

        if self.mode == self.MODE_WALK:
            # UP/DOWN           = "Playtime"
            # L/R               = "Step Height"
            # R_Trig + UP/DOWN  = "Z-height"
            # R_Trig + L/R      = "Y-position"

            if self.controller.button_trigger_r.is_pressed:
                if abs(hat.x) == 1:
                    # Dog Y-position
                    self.dog.desired_y += hat.x
                    print(f"Setting dog desired_y to {self.dog.desired_y}")
                elif abs(hat.y) == 1:
                    # Dog Z-position
                    self.dog.desired_z += hat.y
                    print(f"Setting dog desired_z to {self.dog.desired_z}")
            else:
                if abs(hat.x) == 1:
                    # Servo Playtime
                    self.dog.motion.walk.gait.substep_motion_playtime += hat.x
                    self.dog.motion.walk.gait.substep_time = self.dog.motion.walk.gait.substep_motion_playtime / 100
                    print(f"Setting playtime to {self.dog.motion.walk.gait.substep_motion_playtime}, substep_time to {self.dog.motion.walk.gait.substep_time}")
                elif abs(hat.y) == 1:
                    # Step Height
                    self.dog.motion.walk.gait.step_lift_amount += hat.y
                    print(f"Setting step lift amount to {self.dog.motion.walk.gait.step_lift_amount}")
                




    def update_axes(self):
        """ Updates the axis positions, taking into account the axis_threshold

        The xbox360 library does not account for axis_threshold for immediate axis positions, only for event callbacks.
        """
        self.axis_r['x'] = 0
        self.axis_r['y'] = 0
        self.axis_l['x'] = 0
        self.axis_l['y'] = 0
        if not -self.axis_threshold < self.controller.axis_l.x < self.axis_threshold:
            self.axis_l['x'] = self.controller.axis_l.x
        if not -self.axis_threshold < self.controller.axis_l.y < self.axis_threshold :
            self.axis_l['y'] = self.controller.axis_l.y
        if not -self.axis_threshold < self.controller.axis_r.x < self.axis_threshold :
            self.axis_r['x'] = self.controller.axis_r.x
        if not -self.axis_threshold < self.controller.axis_r.y < self.axis_threshold:
            self.axis_r['y'] = self.controller.axis_r.y

    def changeMode(self, button):
        self.mode += 1
        if self.mode > 2:
            self.mode = 1
        
        # Call the controller's init function
        if self.mode == self.MODE_STATIONARY:
            self.init_stationary_mode()
        elif self.mode == self.MODE_WALK:
            self.init_walk_mode()
        self.update_mode_led()
        
    def init_stationary_mode(self):
        pass

    def init_walk_mode(self):
        # TODO: Set all desired variables here?
        self.dog.desired_y = self.dog.y
        self.dog.desired_z = self.dog.z

    def update_mode_led(self):
        self.controller.set_led(Xbox360Controller.LED_OFF)
        
        if self.mode == 1:
            LED_mode = Xbox360Controller.LED_TOP_LEFT_ON
            print("XBOX Controller: Stationary Mode")
        elif self.mode == 2:
            LED_mode = Xbox360Controller.LED_TOP_RIGHT_ON
            print("XBOX Controller: Walk Mode")
        elif self.mode == 3:
            LED_mode = Xbox360Controller.LED_BOTTOM_LEFT_ON
        elif self.mode == 4:
            LED_mode = Xbox360Controller.LED_BOTTOM_RIGHT_ON

        self.controller.set_led(LED_mode)

    def get_commands(self):

        if not self.CONTROL_ENABLE:
            return

        cur_millis = millis()

        if not self.last_update + self.UPDATE_PERIOD < cur_millis:
            # If it's not time to update positions or send a command, return None
            # Do a time.sleep(0) to let the xbox controller driver thread run so we actually get updated positions
            time.sleep(0)
            return None
        self.last_update = cur_millis

        # Update internal axes
        self.update_axes()

        # Do we need to handle a button press (Non mode dependant)
        if self.do_sleep:
            command_queue = deque()
            command_queue.append(Command(command = "sleep_async", args = None))
            self.do_sleep = False
            return command_queue
        
        if self.do_reboot:
            command_queue = deque()
            command_queue.append(Command(command = "reboot", args = None))
            self.do_reboot = False
            return command_queue

        if self.do_reset_position:
            command_queue = deque()
            command_queue.append(Command(command = "reset_position", args = None))
            self.do_reset_position = False
            return command_queue
        
        if self.mode == self.MODE_STATIONARY:
            
            # commands_stationary will always only give a single command, so add it to a list with only its one command
            return [self.commands_stationary()]
        
        elif self.mode == self.MODE_WALK:
           return self.commands_walk()

    # OLD COMMANDS_WALK CODE
    # playtime = 15
    # step_height = 50
    # front_trim = 0
    # y_offset = 0
    # def commands_walk(self):

    #     MIN_PLAYTIME_WALK = 5
    #     MIN_PLAYTIME_TURN = 8
    #     MAX_PLAYTIME = 50

    #     command_queue = deque()

    #     playtime = self.playtime
    #     lift_amount = self.step_height
    #     trim_f = self.front_trim    # Lift up the front legs higher because it drags

    #     des_walk_speed = int(-100*self.axis_r['y'])
    #     des_turn_speed = int(100*self.axis_r['x'])

    #     step_len = int(-70*self.axis_r['y'])
    #     # wturn_playtime = int(lin_interp(100, abs(des_turn_speed), 0, MIN_PLAYTIME_TURN, MAX_PLAYTIME))
    #     wturn_playtime = 13

    #     # if step_len > 100:
    #     #     lift_amount += step_len//5

    #     # Walk forward
    #     if des_walk_speed > 10:
        
    #         # The offset to keep the robot straight is applied in the Walk gait now
    #         # Let's apply the y-offset here so the robot leans forward (so the knees don't hit the ground)
    #         self.dog.desired_y = self.y_offset
    #         trim_r = 0.5*-des_turn_speed
    #         command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, playtime, trim_r, trim_f)))
           
    #         if not self.dog.motion.current_motion == Motion.WALK:
    #             command_queue.append(Command(command = 'walk', args=['f']))

    #     elif des_walk_speed < -10:
    #         step_len = -step_len
    #         command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, playtime)))
    #         if not self.dog.motion.current_motion == Motion.WALK:
    #             command_queue.append(Command(command = 'walk', args=['b']))

    #     elif des_turn_speed > 10:
    #         step_len = 30
    #         command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, wturn_playtime)))
    #         if not self.dog.motion.current_motion == Motion.WALK:
    #             command_queue.append(Command(command = 'walk', args=['tr']))
        
    #     elif des_turn_speed < -10:
    #         step_len = 30
    #         command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, wturn_playtime)))
    #         if not self.dog.motion.current_motion == Motion.WALK:
    #             command_queue.append(Command(command = 'walk', args=['tl']))

    #     # Stop walking
    #     else:
    #         if not self.dog.motion.current_motion == Motion.STATIONARY:
    #             command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, playtime)))
    #             command_queue.append(Command(command = 'stop', args=None))
    #         else:
    #             return None

    #     if not len(command_queue) > 0:
    #         return None
    #     else:
    #         return command_queue

    def commands_walk(self):
        WALK_AXIS_THRESHOLD = 0.2
        walk_x = self.axis_r['x']
        walk_y = -self.axis_r['y']
        walk_yaw = self.axis_l['x']
        command_queue = deque()
        
        if abs(walk_x) > WALK_AXIS_THRESHOLD or abs(walk_y) > WALK_AXIS_THRESHOLD or abs(walk_yaw) > WALK_AXIS_THRESHOLD:
            #print(f"WALKING: {walk_x}, {walk_y}, {walk_yaw}")
            self.dog.motion.current_motion == Motion.WALK
            command_queue.append(Command(command = 'walk', args=[-1, walk_x, walk_y, walk_yaw]))
        else:
            # No walk command.  Either walk in place or stop walking
            #if not self.walk_in_place:
            if True:
                command_queue.append(Command(command = 'stop', args=None))
                self.dog.motion.current_motion == Motion.STATIONARY
                #print(f"Stopping Walk")


        if not len(command_queue) > 0:
            return None
        else:
            return command_queue
            

    def commands_stationary(self):
   
        des_x = 0
        des_y = 0
        des_z = self.dog.z

        des_roll = 0
        des_pitch = 0
        des_yaw = 0

        des_speed = self.dog.speed

        # TODO: Send REBOOT command
        # self.controller.button_y.when_pressed = self.reboot
        
        while self.mode == self.MODE_STATIONARY:
            des_x = -self.STATIONARY_X_MULTIPLIER*self.axis_r['x']
            
            if not self.controller.button_trigger_r.is_pressed:
                des_y = self.STATIONARY_Y_MULTIPLIER*-self.axis_r['y']
            else:
                des_z += self.STATIONARY_Z_MULTIPLIER*-self.axis_r['y']


            # TODO: Make these constants
            if des_z > 230:
                des_z = 230

            elif des_z < 30:
                des_z = 30

            des_pitch = -20*self.axis_l['y']

            if not self.controller.button_trigger_l.is_pressed:
                des_roll = 30*self.axis_l['x']
            else:
                des_yaw += 20*self.axis_l['x']

            # print("{:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f}".format(des_x, des_y, des_z, des_roll, des_pitch, des_yaw))

            try:
                # Absolute move command:
                command = Command(command = "absolute_move", args = (des_x, des_y, des_z, des_roll, des_pitch, des_yaw, des_speed))
                
                return command
            except ValueError:
                
                if self.controller.has_rumble:
                    self.controller.set_rumble(0.5, 0.5, 1000)

                des_x = 0
                des_y = 0
                des_z = 150

                des_roll = 0
                des_pitch = 0
                des_yaw = 0


if __name__ == '__main__':
    os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')
    controller = Xbox360Controller(0, axis_threshold=0.1)
    while True:
        print("{:3.5f} {:3.5f}".format(controller.axis_r.x, controller.axis_r.y))
        time.sleep(.1)