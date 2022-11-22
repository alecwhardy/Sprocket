import os
import time
from collections import deque

from xbox360controller import Xbox360Controller

from Commands import Command
from functions import *
from Walk import Walk
from Motion import Motion

from Dog import Dog

# NOTE:  IF XBOX CONTROL IS ENABLED AND IN WALK MODE, CONSOLE COMMANDS WILL NOT WORK!!!

class XboxControl:

    CONNECTED = True

    MODE_STATIONARY = 1
    MODE_WALK = 2

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

    def __init__(self, dog, controller_id = 0, axis_threshold = 0.2):

        self.dog = dog

        self.controller_id = controller_id
        self.mode = self.MODE_STATIONARY
        self.axis_threshold = axis_threshold

        os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')

        try:
            self.controller = Xbox360Controller(controller_id, axis_threshold=axis_threshold)
        except Exception:
            self.CONNECTED = False
            return

        self.controller.button_mode.when_pressed = self.changeMode
        self.update_mode_led()

        self.last_update = millis()

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
        if self.mode > 4:
            self.mode = 1
        self.update_mode_led()
        
    def update_mode_led(self):
        self.controller.set_led(Xbox360Controller.LED_OFF)
        
        if self.mode == 1:
            LED_mode = Xbox360Controller.LED_TOP_LEFT_ON
        elif self.mode == 2:
            LED_mode = Xbox360Controller.LED_TOP_RIGHT_ON
        elif self.mode == 3:
            LED_mode = Xbox360Controller.LED_BOTTOM_LEFT_ON
        elif self.mode == 4:
            LED_mode = Xbox360Controller.LED_BOTTOM_RIGHT_ON

        self.controller.set_led(LED_mode)

    def get_commands(self):

        cur_millis = millis()

        if not self.last_update + self.UPDATE_PERIOD < cur_millis:
            # If it's not time to update positions or send a command, return None
            # Do a time.sleep(0) to let the xbox controller driver thread run so we actually get updated positions
            time.sleep(0)
            return None
        self.last_update = cur_millis

        # Update internal axes
        self.update_axes()
        
        if self.mode == self.MODE_STATIONARY:
            
            # commands_stationary will always only give a single command, so add it to a list with only its one command
            return [self.commands_stationary()]
        
        elif self.mode == self.MODE_WALK:
           return self.commands_walk()

    def commands_walk(self):

        MIN_PLAYTIME_WALK = 5
        MIN_PLAYTIME_TURN = 8
        MAX_PLAYTIME = 50

        command_queue = deque()

        lift_amount = 51
        playtime = 13

        des_walk_speed = int(-100*self.axis_r['y'])
        des_turn_speed = int(100*self.axis_r['x'])

        step_len = int(-70*self.axis_r['y'])
        # wturn_playtime = int(lin_interp(100, abs(des_turn_speed), 0, MIN_PLAYTIME_TURN, MAX_PLAYTIME))
        wturn_playtime = 13

        if step_len > 100:
            lift_amount += step_len//5

         # Clear the y-offset (set below) so the robot leans forward (so the knees don't hit the ground)
         # TODO: Move this to a better spot!
        self.dog.motion.desired_y = 0

        # Walk forward
        if des_walk_speed > 10:
        
            # The offset to keep the robot straight is applied in the Walk gait now
            # Let's apply the y-offset here so the robot leans forward (so the knees don't hit the ground)
            self.dog.motion.desired_y = 30
            command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, playtime)))
            if not self.dog.motion.current_motion == Motion.WALK:
                command_queue.append(Command(command = 'walk', args=['f']))

        elif des_walk_speed < -10:
            step_len = -step_len
            command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, playtime)))
            if not self.dog.motion.current_motion == Motion.WALK:
                command_queue.append(Command(command = 'walk', args=['b']))

        elif des_turn_speed > 10:
            step_len = 30
            command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, wturn_playtime)))
            if not self.dog.motion.current_motion == Motion.WALK:
                command_queue.append(Command(command = 'walk', args=['tr']))
        
        elif des_turn_speed < -10:
            step_len = 30
            command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, wturn_playtime)))
            if not self.dog.motion.current_motion == Motion.WALK:
                command_queue.append(Command(command = 'walk', args=['tl']))

        # Stop walking
        else:
            if not self.dog.motion.current_motion == Motion.STATIONARY:
                command_queue.append(Command(command = 'walk_params', args=(step_len, lift_amount, playtime)))
                command_queue.append(Command(command = 'stop', args=None))
            else:
                return None

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
            des_x = -80*self.axis_r['x']
            
            if not self.controller.button_trigger_r.is_pressed:
                des_y = 40*-self.axis_r['y']
            else:
                des_z += 10*-self.axis_r['y']


            # TODO: Make these constants
            if des_z > 230:
                des_z = 230

            elif des_z < 40:
                des_z = 40

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
                des_z = Dog.NEUTRAL_HEIGHT

                des_roll = 0
                des_pitch = 0
                des_yaw = 0


if __name__ == '__main__':
    os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')
    controller = Xbox360Controller(0, axis_threshold=0.2)
    while True:
        print("{:3.5f} {:3.5f}".format(controller.hat.x,controller.hat.y))
        time.sleep(.1)