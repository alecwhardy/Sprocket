from xbox360controller import Xbox360Controller
from functions import *
from Walk import Walk
import os
import time
from Commands import Command

# NOTE:  Make sure to run chmod 666 "brightness" file
#        /sys/class/leds/xpad0 $ sudo chmod 666 brightness
#        sudo chmod 666 /sys/class/leds/xpad0/brightness
# Microsoft X-Box 360 pad at index 0
# Axes: 5
#         axis_l
#         axis_r
#         hat
#         trigger_l
#         trigger_r
# Buttons: 11
#         button_a
#         button_b
#         button_x
#         button_y
#         button_trigger_l
#         button_trigger_r
#         button_select
#         button_start
#         button_mode  (Player Select)
#         button_thumb_l
#         button_thumb_r
# Rumble: no
# Driver version: 2.1.0 1.0.1

class XboxControl:

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

    def __init__(self, controller_id = 0, axis_threshold = 0.3):

        self.controller_id = controller_id
        self.mode = self.MODE_STATIONARY
        self.axis_threshold = axis_threshold

        os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')

        self.controller = Xbox360Controller(controller_id, axis_threshold=axis_threshold)

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
            # Add a really tiny time.sleep so that the xbox controller position can update.  
            # The axes seem to "stick" without this, possibly because the xbox controller driver runs on a seperate thread.
            time.sleep(.00000001)
            return None

        # Update internal axes
        self.update_axes()
        
        if self.mode == self.MODE_STATIONARY:
            self.last_update = cur_millis
            return [self.commands_stationary()]
        
        # elif self.mode == self.MODE_WALK:
        #     self.commands_walk(self.dog)

    # def commands_walk(self, dog):

    #     # Right stick is for walking forward/backward and turning
    #     # Left stick is for walking sideways and Z-height

    #     dog.go_position(0, 0, dog.z, 0, 0, 0, 20)

    #     walk = Walk()
    #     step_len = 30
    #     lift_amount = 70
    #     playtime = 12
    #     # walk.update_set_positions(dog, step_len, lift_amount, playtime)

    #     while self.mode == self.MODE_WALK:
            
    #         MIN_PLAYTIME_WALK = 5
    #         MIN_PLAYTIME_TURN = 8
    #         MAX_PLAYTIME = 50
            
    #         des_wf_speed = int(-100*self.controller.axis_r.y)
    #         des_turn_speed = int(100*self.controller.axis_r.x)

    #         # wf_playtime = int(lin_interp(100, des_wf_speed, 0, MIN_PLAYTIME_WALK, MAX_PLAYTIME))
    #         wf_playtime = 10
    #         step_len = int(-100*self.controller.axis_r.y)
    #         wturn_playtime = int(lin_interp(100, abs(des_turn_speed), 0, MIN_PLAYTIME_TURN, MAX_PLAYTIME))

    #         if step_len > 100:
    #             lift_amount += step_len//5


    #         if des_wf_speed > 10:
    #             walk.update_set_positions(dog, step_len, lift_amount, wf_playtime)

    #             # Apply correction factor to "BACK_DOWN_L"
    #             old = walk.set_positions["BACK_DOWN_L"]
    #             corrected_position = (old[0], 1.3*old[1], old[2], old[3])
    #             walk.set_positions["BACK_DOWN_L"] = corrected_position

    #             walk.crude_walk(dog, Walk.FORWARD)
    #             print("WF: Steplen {}".format(step_len))

    #         elif des_wf_speed < -10:
    #             step_len = -step_len
    #             walk.update_set_positions(dog, step_len, lift_amount, wf_playtime)
    #             walk.crude_walk(dog, Walk.BACKWARD)
    #             print("WB: Steplen {}".format(step_len))

    #         elif des_turn_speed > 20:
    #             step_len = 30
    #             walk.update_set_positions(dog, step_len, lift_amount, wturn_playtime)
    #             walk.crude_walk(dog, Walk.TURN_RIGHT)
    #             print("TURN_R: Playtime {}".format(wturn_playtime))

    #         elif des_turn_speed < -20:
    #             step_len = 30
    #             walk.update_set_positions(dog, step_len, lift_amount, wturn_playtime)
    #             walk.crude_walk(dog, Walk.TURN_LEFT)
    #             print("TURN_L: Playtime {}".format(wturn_playtime))

    #         else:
    #             walk.update_set_positions(dog, step_len, lift_amount, wf_playtime)
    #             walk.crude_walk(dog, Walk.STILL)
    #             print("Standing Still")

    def commands_stationary(self):
   
        des_x = 0
        des_y = 0
        des_z = 150

        des_roll = 0
        des_pitch = 0
        des_yaw = 0

        des_speed = 20

        # TODO: Send REBOOT command
        # self.controller.button_y.when_pressed = self.reboot
        
        while self.mode == self.MODE_STATIONARY:
            #des_x = -80*self.controller.axis_r.x
            des_x = -80*self.axis_r['x']
            
            if not self.controller.button_trigger_r.is_pressed:
                #des_y = 40*-self.controller.axis_r.y
                des_y = 40*-self.axis_r['y']
            else:
                #des_z -= 30*self.controller.axis_r.y
                des_z -= 30*-self.axis_r['y']


            # TODO: Make these constants
            if des_z > 230:
                des_z = 230

            elif des_z < 30:
                des_z = 30

            #des_pitch = -20*self.controller.axis_l.y
            des_pitch = -20*self.axis_l['y']

            if not self.controller.button_trigger_l.is_pressed:
                #des_roll = 30*self.controller.axis_l.x
                des_roll = 30*self.axis_l['x']
            else:
                des_yaw += 2*self.controller.axis_l.x
                des_yaw += 2*self.axis_l['x']

            print("{:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f}".format(des_x, des_y, des_z, des_roll, des_pitch, des_yaw))

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


# if __name__ == '__main__':
#     os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')
#     controller = Xbox360Controller(0, axis_threshold=0.2)
#     while True:
#         print("{:3.5f} {:3.5f}".format(controller.axis_r.x,controller.axis_r.y))
#         time.sleep(.1)