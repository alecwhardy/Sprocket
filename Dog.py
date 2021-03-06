import math
from Leg import Leg
import time
from CommandHandler import CommandHandler
from Motion import Motion
from IMU import IMU
from DataPlot import DataPlot
from XYZrobotServo import XYZrobotServo
from functions import *

class Dog:
    """ Contains all of the necessary code to determine the current state of the dog.  All behavior is handled by the Behavior class

    Returns:
        [type]: [description]
    """

    LENGTH = 200
    WIDTH = 117

    NEUTRAL_HEIGHT = 150
    NEUTRAL_SPEED = 30

    SHUTOFF_VOLTAGE = 8.5

    scheduled_events = [] # tuples of (function, event period ms, last execution time)

    # The most recent x, y, z, r, p, yaw values that the dog moved to after a go_position() call
    # I.E. the position the dog 'thinks' it's in
    x = 0
    y = 0
    z = 0
    roll = 0
    pitch = 0
    yaw = 0
    speed = 0

    # Used for "balance" mode - IMU compensation.  
    desired_x = 0
    desired_y = 0
    desired_z = 0
    desired_roll = 0
    desired_pitch = 0
    desired_yaw = 0

    # The true roll, pitch, and yaw, as determined by the IMU
    sensor_roll = 0
    sensor_pitch = 0
    sensor_yaw = 0

    def __init__(self, servos):
        """[summary]

        Args:
            legs (List of Legs): Follow order Front Left, Front Right, Rear Left, Rear Right
        """
        self.servos = servos

        # Create a Leg object for each leg in an array, following the order used by the Dog class initializer (FL, FR, RL, RR)
        # The Leg class already knows what servo ID corresponds to what joint
        # Example Usage: legs[Leg.FR].set_thigh_position(0, 0)
        self.legs = [Leg("FL", servos), Leg("FR", servos), Leg("RL", servos), Leg("RR", servos)]
        
        self.command_handler = CommandHandler(self)
        self.motion = Motion(self)
        self.imu = IMU()
        self.dataplot = DataPlot()


    def get_voltage(self):
        return self.legs[0].servos[0].getVoltage()

    def flatten_shoulders(self, speed):
        for leg in self.legs:
            leg.go_shoulder_angle(0, speed)

    def calc_position(self, X, Y, Z, roll, pitch, yaw, speed):
        """ Calculates and updates the calc_position value for each of the leg servos. 

        Args:
            X (float): X position
            Y (float): Y position
            Z (float): Z position
            roll (float): Roll position
            pitch (float): Pitch position
            yaw (float): Yaw position
            speed (int): Time for the position, in units of 10ms

        Returns:
            Bool: Returns true if a valid position was calculated for each joint.  If this returns false, the dog cannot move to this calculated position.
        """
        if roll == 0:
            roll = 0.001
        if pitch == 0:
            pitch = 0.001
        if yaw == 0:
            yaw = 0.001

        for leg in self.legs:
            leg.desired_x = X
            leg.desired_y = Y
            leg.desired_z = Z
            leg.desired_speed = speed

        # Take care of pitch first
        # TODO: Determine if we *can* even go to the desired pitch (at the given height at we are at)

        Z_front_offset = (Dog.LENGTH/2)*math.tan(math.radians(pitch))
        for leg in self.legs:
            if leg.end == 'F':
                leg.desired_z += Z_front_offset
            if leg.end == 'R':
                leg.desired_z -= Z_front_offset

        # Now take care of roll
        # TODO: Determine if we *can* even go to the desired roll (at the given height at we are at)

        Z_left_offset = (Dog.WIDTH/2)*math.tan(math.radians(roll))
        for leg in self.legs:
            if leg.side == 'R':
                leg.desired_z -= Z_left_offset
            if leg.side == 'L':
                leg.desired_z += Z_left_offset

        # Now take care of yaw
        # TODO: Determine if we *can* even go to the desired yaw (at the given height at we are at)

        X_front_offset = (Dog.LENGTH/2)*math.tan(math.radians(yaw))
        for leg in self.legs:
            if leg.end == 'F':
                leg.desired_x += X_front_offset
            if leg.end == 'R':
                leg.desired_x -= X_front_offset
        
        # Calculate where each leg needs to go
        # Return true is all of the legs have a valid position
        return self.legs[0].calc_desired() and self.legs[1].calc_desired() and self.legs[2].calc_desired() and self.legs[3].calc_desired()
        
    def go_calculated_positions(self):
        """
        Moves each of the legs to their calculated positions.  
        
        Make sure to call dog.calc_position() or leg.calc_position() first before calling this function.
        """
        for leg in self.legs:
            leg.go_shoulder_angle(leg.calc_theta_shoulder, leg.desired_speed)
        # Go to the calculated thigh angles
        for leg in self.legs:
            leg.go_thigh_angle(leg.calc_theta_thigh, leg.desired_speed)
        # Go to the calculated knee angles
        for leg in self.legs:
            leg.go_knee_angle(leg.calc_theta_knee, leg.desired_speed)


    def go_position(self, X, Y, Z, roll, pitch, yaw, speed):
        """ Calculates the positions for each leg given the dog's desired X, Y, Z, roll, pitch, yaw, speed parameters, and then moves there immediately.

        Args:
            X (float): X position
            Y (float): Y position
            Z (float): Z position
            roll (float): Roll position
            pitch (float): Pitch position
            yaw (float): Yaw position
            speed (int): Time for the position, in units of 10ms
        """

        if self.calc_position(X, Y, Z, roll, pitch, yaw, speed):
            # If we can successfully calculate the desired position for each leg, update the current position valus before we move to them
                self.x = X
                self.y = Y
                self.z = Z
                self.roll = roll
                self.pitch = pitch
                self.yaw = yaw
                self.speed = speed

        # Go to the calculated shoulder angles
        self.go_calculated_positions()

    def die(self):
        print("Dog is dying...")
        self.motion.motion_enable = False
        for leg in self.legs:
            for servo in leg.servos:
                servo.torqueOff()

    def wake_up(self):
        print("Resetting position 'waking up'")
        self.motion.motion_enable = True
        self.go_position(0, 0, 150, 0, 0, 0, self.NEUTRAL_SPEED)

        # Reset the LED policy for the servos, because if we died, then they are user-controlled and blue       
        for leg in self.legs:
            for servo in leg.servos:
                servo.set_LED(XYZrobotServo.LED_Color.WHITE)
                time.sleep(0.01)  # Need to wait before setting the LED color after changing the policy
                servo.reset_LED_alarm_policy()

                
        #TODO: Calibrate Euler angles here

    def servo_reboot(self):
        for servo in self.legs[0].servos:
            servo.reboot()

    def check_voltage(self):
            try:
                if self.legs[0].servos[0].getVoltage() < self.SHUTOFF_VOLTAGE:
                    self.die()
                    print("Batteries Dead!")
            except:
                # Sometimes we don't get voltage quick enough
                pass

    def update_orientation(self):
        self.sensor_yaw, self.sensor_pitch, self.sensor_roll = self.imu.get_euler()  # Todo: Only do this once a second
        # invert pitch
        try:
            self.sensor_pitch = -self.sensor_pitch
        except:
            pass  # No IMU data
        

    def schedule_event(self, function, per_ms):
        self.scheduled_events.append((function, per_ms, 0))

    def run_scheduled_events(self):
        cur_millis = millis()

        for i in range(len(self.scheduled_events)):
            event = self.scheduled_events[i]
            event_fn = event[0]
            event_freq = event[1]  # Event "frequency", even though it's tecnically event period
            event_last = event[2]

            if event_last + event_freq < cur_millis:
                # run the event
                event_fn()

                # update the event entry
                self.scheduled_events[i] = (event_fn, event_freq, cur_millis)


    def live(self, verbose = False):
        """ Main loop.  Update sensor data, update servos, and respond to behaviors and controls
        """

        while True:

            # get new commands
            self.command_handler.get_new_commands()
            
            # handle commands
            self.command_handler.handle_commands()

            # update sensors
            self.run_scheduled_events()

            # Todo: move this elsewhere
            latest_rss = self.imu.get_gyro_rss()
            self.dataplot.record_loop(latest_rss)

            # update motion
            self.motion.update_motion()

            time.sleep(0)

            #print(self.legs[0].servos[1].readStatus().pwm)