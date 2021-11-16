import time, os, psutil
from Motion import Motion
from Walk import Walk

class Command:
    """ Really simple data type to pass into command queues. 
    """
    
    def __init__(self, command, args):
        self.command = command
        self.args = args


class Commands:

    def __init__(self, dog):
        self.dog = dog

    def die(self):
        self.dog.die()

    def sleep_async(self):
        print("Dog going to sleep")
        self.dog.go_position(0, 0, 35, 0, 0, 0, 100)
        time.sleep(1)
        self.dog.die()

    def reset_position(self):
        self.dog.motion.current_motion = Motion.STATIONARY
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
        print("Position: {: 3.0f}  {: 3.0f}  {: 3.0f}  {: 3.0f} {: 3.0f} {: 3.0f} {: 3.0f}".format(x, y, z, roll, pitch, yaw, speed))

    def absolute_leg_move(self, args):
        
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


        if args is None:
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

        n = -1
        try:
            n = int(args[1])
        except (IndexError, TypeError):
            pass

        self.dog.motion.steps_remaining = -1
        self.dog.motion.do_walk(direction)

    def walk_params(self, args):
        step_len = int(args[0])
        lift_amount = int(args[1])
        playtime = int(args[2])
        self.dog.motion.walk.gait.update_set_positions(self.dog, step_len, lift_amount, playtime)

    def stop(self):
        self.dog.motion.stop_walk()

    def down(self):
        pass

    def sit(self):
        pass

    def run(self):
        pass
