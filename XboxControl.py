from xbox360controller import Xbox360Controller
from functions import *
import Walk
import time

# NOTE:  Make sure to run chmod 666 "brightness" file
#        /sys/class/leds/xpad0 $ sudo chmod 666 brightness
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

    
    def __init__(self, dog, controller_id = 0):
        
        self.dog = dog

        self.controller_id = controller_id
        self.mode = self.MODE_STATIONARY
        self.controller = Xbox360Controller(controller_id, axis_threshold=0.2)

        self.controller.button_mode.when_pressed = self.changeMode
        self.update_mode_led()

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

    def behave(self):
        
        if self.mode == self.MODE_STATIONARY:
            self.mode_stationary(self.dog)
        
        if self.mode == self.MODE_WALK:
            self.mode_walk(self.dog)

    def mode_walk(self, dog):

        # Right stick is for walking forward/backward and turning
        # Left stick is for walking sideways and Z-height

        dog.go_position(0, 0, dog.z, 0, 0, 0, 20)

        while self.mode == self.MODE_WALK:
            
            MIN_PLAYTIME_WALK = 10
            MIN_PLAYTIME_TURN = 8
            MAX_PLAYTIME = 50
            
            des_wf_speed = int(-100*self.controller.axis_r.y)
            des_turn_speed = int(100*self.controller.axis_r.x)

            wf_playtime = int(lin_interp(100, des_wf_speed, 0, MIN_PLAYTIME_WALK, MAX_PLAYTIME))
            wturn_playtime = int(lin_interp(100, abs(des_turn_speed), 0, MIN_PLAYTIME_TURN, MAX_PLAYTIME))

            if des_wf_speed > 5:
                Walk.crude_walk(dog, Walk.FORWARD, 1, 30, 50, wf_playtime)
                print("WF: Playtime {}".format(wf_playtime))

            elif des_turn_speed > 20:
                Walk.crude_walk(dog, Walk.TURN_RIGHT, 1, 30, 50, wturn_playtime)
                print("TURN_R: Playtime {}".format(wturn_playtime))

            elif des_turn_speed < -20:
                Walk.crude_walk(dog, Walk.TURN_LEFT, 1, 30, 50, wturn_playtime)
                print("TURN_L: Playtime {}".format(wturn_playtime))


    def mode_stationary(self, dog):
   
        des_x = 0
        des_y = 0
        des_z = 150

        des_roll = 0
        des_pitch = 0
        des_yaw = 0
        

        while self.mode == self.MODE_STATIONARY:
            des_x = 80*self.controller.axis_r.x
            
            if not self.controller.button_trigger_r.is_pressed:
                des_y = 40*-self.controller.axis_r.y
            else:
                des_z -= 10*self.controller.axis_r.y
            # des_z = 100-(80*controller.axis_r.y)

            des_pitch = -20*self.controller.axis_l.y

            if not self.controller.button_trigger_l.is_pressed:
                des_roll = 30*self.controller.axis_l.x
            else:
                des_yaw += 2*self.controller.axis_l.x

            print("{:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f} {:3.0f}".format(des_x, des_y, des_z, des_roll, des_pitch, des_yaw))

            try:
                dog.go_position(des_x, des_y, des_z, des_roll, des_pitch, des_yaw, 20)
                time.sleep(.2)
            except ValueError:
                
                if self.controller.has_rumble:
                    self.controller.set_rumble(0.5, 0.5, 1000)

                des_x = 0
                des_y = 0
                des_z = 150

                des_roll = 0
                des_pitch = 0
                des_yaw = 0