import time, os, psutil
from Motion import Motion
from Walk import Walk
from Recordings import MotionPlayback
import Audio

class Command:
    """ Really simple data type to pass into command queues. 
    """
    
    def __init__(self, command, args = None):
        self.command = command
        self.args = args

    def __repr__(self) -> str:
        return f"Command: {str(self.command)}  Args: {str(self.args)}"


class Commands:

    def __init__(self, dog):
        self.dog = dog

    def reboot(self):
        # Reboot the servos
        for servo in self.dog.legs[0].servos:
            servo.reboot()
        time.sleep(2)

    def die(self):
        self.dog.die()

    def sleep_async(self):
        print("Dog going to sleep")
        self.dog.go_position(0, 0, 35, 0, 0, 0, 100)
        time.sleep(1)
        self.dog.die()

    def toggle_xbox(self):
        self.dog.command_handler.xbox_controller_enable = not self.dog.command_handler.xbox_controller_enable
        print("XBOX control: ", end='')
        print(self.dog.command_handler.xbox_controller_enable)

    def reset_position(self):
        self.dog.motion.current_motion = Motion.STATIONARY
        self.end_playback()
        self.dog.wake_up()

    def print_resource_usage(self):
        process = psutil.Process(os.getpid())
        print("Memory Usage (MB): " + str(process.memory_info().rss/1024/2014))
        print("CPU Usage: "+str(psutil.cpu_percent()))
        print("Voltage: {}V".format(self.dog.get_voltage()))

    def print_servo_errors(self):
        for servo in self.dog.legs[0].servos:
            status = servo.readStatus()
            print("Servo {}: {}".format(servo.id, status.statusError))

    def speed(self, args):
        self.dog.speed = int(args[0])

    def calc_absolute_position(self, args):
        x = 0 
        y = 0
        roll = 0
        pitch = 0
        yaw = 0
        z = self.dog.NEUTRAL_HEIGHT
        speed = self.dog.NEUTRAL_SPEED
        try:
            x = float(args[0])
            y = float(args[1])
            z = float(args[2])
            roll = float(args[3])
            pitch = float(args[4])
            yaw = float(args[5])
            speed = int(args[6])
        except IndexError:
            pass

        self.dog.calc_position(x, y, z, roll, pitch, yaw, speed)

    def calc_leg_position(self, args):
        """ Calculate the new position for a leg.  When  dog.go_position() is called, the leg's leg.desired_speed is used.

        Args:
            args (array): Leg number, X, Y, Z
        """
        leg_num = int(args[0])
        x = float(args[1])
        y = float(args[2])
        z = float(args[3])

        self.dog.legs[leg_num].calc_position(x, y, z)

    def calc_move(self, args = None):
        self.dog.go_calculated_positions()

    def absolute_move(self, args):
        
        # self.dog.motion.current_motion = Motion.STATIONARY

        x = 0 
        y = 0
        roll = 0
        pitch = 0
        yaw = 0
        z = self.dog.NEUTRAL_HEIGHT
        speed = self.dog.NEUTRAL_SPEED
        try:
            x = float(args[0])
            y = float(args[1])
            z = float(args[2])
            roll = float(args[3])
            pitch = float(args[4])
            yaw = float(args[5])
            speed = int(args[6])
        except IndexError:
            pass

        self.dog.motion.request_absolute_position(x, y, z, roll, pitch, yaw, speed)
        # print("Position: {: 3.0f}  {: 3.0f}  {: 3.0f}  {: 3.0f} {: 3.0f} {: 3.0f} {: 3.0f}".format(x, y, z, roll, pitch, yaw, speed))

    def relative_move(self, args):
        x = 0 
        y = 0
        z = 0
        roll = 0
        pitch = 0
        yaw = 0
        speed = 0

        try:
            x = float(args[0])
            y = float(args[1])
            z = float(args[2])
            roll = float(args[3])
            pitch = float(args[4])
            yaw = float(args[5])
            speed = int(args[6])
        except IndexError:
            pass

        self.dog.motion.request_relative_position(x, y, z, roll, pitch, yaw, speed)
        print("Position: {: 3.0f}  {: 3.0f}  {: 3.0f}  {: 3.0f} {: 3.0f} {: 3.0f} {: 3.0f}".format(x, y, z, roll, pitch, yaw, speed))


    def absolute_leg_move(self, args):
        """ Move an single leg to an absolute position, coorindates relative to shoulder joint

        Args:
            args (List): (int(leg), float(x, y, z))
        """
        
        leg = int(args[0])
        x = float(args[1])
        y = float(args[2])
        z = float(args[3])
        speed = self.dog.NEUTRAL_SPEED

        try:
            speed = int(args[4])
        except IndexError:
            pass

        self.dog.motion.request_absolute_leg(leg, x, y, z, speed)
        print("Leg {} moved to: {: 3.0f}  {: 3.0f}  {: 3.0f}".format(leg, x, y, z))

    def prance(self):
        self.dog.motion.steps_remaining = -1
        self.dog.motion.do_prance()

    def prance_n(self, n):
        self.dog.motion.steps_remaining = n
        self.dog.motion.do_prance()

    def walk(self, args = None):

        if self.dog.motion.walk.gait.NAME == "CRUDE_BALANCED_GAIT":
            n = int(args[0])
            walk_x = float(args[1])
            walk_y = float(args[2])
            walk_yaw = float(args[3])
            
            # If not already walking, call do_walk initially.  Then, the motion handler will call do_walk on the correct timer
            if self.dog.motion.current_motion != Motion.WALK:
                self.dog.motion.steps_remaining = n
                self.dog.motion.walk.walk_init(self.dog)
                self.dog.motion.do_walk((walk_x, walk_y, walk_yaw))
            # If we are already walking, don't call do_walk.  Just update the direction
            else:
                self.dog.motion.update_walk((walk_x, walk_y, walk_yaw))

        if self.dog.motion.walk.gait.NAME == "CRUDE_GAIT":

            if args is None or len(args) == 0:
                direction = 'f'
            else:
                direction = args[0]

            if direction == '': direction = Walk.FORWARD
            elif direction == 'f': direction = Walk.FORWARD
            elif direction == 'b': direction = Walk.BACKWARD
            elif direction == 'tl': direction = Walk.TURN_LEFT
            elif direction == 'tr': direction = Walk.TURN_RIGHT
            elif direction == 'sl': direction = Walk.SIDE_LEFT
            elif direction == 'sr': direction = Walk.SIDE_RIGHT
            elif direction == 'p': direction = Walk.IN_PLACE
            n = -1
            try:
                n = int(args[1])
            except (IndexError, TypeError):
                pass
            self.dog.motion.steps_remaining = n
            self.dog.motion.do_walk(direction)

    def walk_params(self, args):
        step_len = int(args[0])
        lift_amount = int(args[1])
        playtime = int(args[2])
        try:
            r_trim = float(args[3])
        except:
            r_trim = 0.0
        try:
            f_trim = float(args[4])
        except:
            f_trim = 0
        self.dog.motion.walk.gait.update_set_positions(self.dog, step_len, lift_amount, playtime, r_trim, f_trim)

    def stop(self):
        self.dog.motion.stop_walk()

    def start_dataplot(self):
        self.dog.dataplot.start_recording()

    def stop_dataplot(self):
        self.dog.dataplot.stop_recording()

    def show_dataplot(self):
        self.dog.dataplot.show_plot()

    def start_playback(self, args = None):
        # args must contain which playback sequence to play.
        # Start with the test command

        loop = False

        self.dog.command_handler.motion_playback = MotionPlayback()

        # No args provided, play test recording
        if args is None or len(args) == 0:
            self.dog.command_handler.motion_playback.load_test()
            print("Playing test recording.")
            return

        # filename provided, no loop
        if len(args) > 0 and args[0] != 'loop':
            print("Attempting to play recording: " + str(args[0]))
            self.dog.command_handler.motion_playback.load_from_file(args[0])
            
        # no filename provided, looping the test recording
        if len(args) == 1 and args[0] == 'loop':
            self.dog.command_handler.motion_playback.load_test()
            self.dog.command_handler.motion_playback_loop = True

        # filename provided, looping
        if len(args) >= 2 and args[0] == 'loop':
            print("Attempting to loop play recording: " + str(args[1]))
            self.dog.command_handler.motion_playback.load_from_file(args[1])
            self.dog.command_handler.motion_playback_loop = True
    
    def end_playback(self):
        self.dog.command_handler.motion_playback_loop = False
        self.dog.command_handler.motion_playback = None
        
    def read_voltage(self):
        try:
            self.dog.voltage = self.dog.legs[0].servos[0].getVoltage()
        except:
            # Sometimes we don't get voltage quick enough
            pass
        
    def play_wav(self, args):
        if type(args) == str:
            Audio.play_wav_async(args)
        else:
            Audio.play_wav_async(args[0])
        
    def bark(self):
        self.play_wav("Audio/bark.wav")
        

    def down(self):
        self.absolute_move(args=[0, 0, 30, 0, 0, 0, 50])

    def sit(self):
        self.absolute_move(args=[0, 0, 150, 0, 25, 0, 50])

    def run(self):
        pass
