import sys, select, time
from Commands import Command
from Leg import Leg


class ConsoleControl:

    def __init__(self, dog):
        self.dog = dog

    def get_commands(self):
        """ Returns the command from the console. """
        
        # Non-blocking read input from stdin
        response = self.get_raw_command()
        if response is None:
            return
        
        response_tokens = response.split(' ')

        if response_tokens[0] == 'help':
            self.print_help()
            return

        elif response_tokens[0] == '':
            return Command(command = "reset_position", args = None)

        elif response_tokens[0] == 'stop':
            # self.dog.dataplot.stop_recording()
            # avg = sum(self.dog.dataplot.recorded_data) / len(self.dog.dataplot.recorded_data)
            # print("Average linear acceleration: {}".format(avg))
            return Command(command = "stop", args = None)
        
        elif response_tokens[0] == 'die':
            return Command(command = "die", args = None)

        elif response_tokens[0] == 'sleep':
            return Command(command = "sleep_async", args = None)

        elif response_tokens[0] == 'reboot':
            return Command(command = 'reboot', args = None)

        elif response_tokens[0] == 'xbox':
            return Command(command = 'toggle_xbox', args = None)

        elif response_tokens[0] == 'res':
            return Command(command = "print_resource_usage", args = None)

        elif response_tokens[0] == 'error':
            return Command(command = "print_servo_errors", args = None)

        elif response_tokens[0] == 'A':
            return Command(command = "absolute_move", args = response_tokens[1:])

        elif response_tokens[0] == 'CA':  # Calc dog absolute position
            return Command(command = "calc_absolute_position", args = response_tokens[1:])

        elif response_tokens[0] == 'CL':  # Calc leg position
            return Command(command = "calc_leg_position", args = response_tokens[1:])

        elif response_tokens[0] == 'CM':  # Move to the calculated position (immediately)
            return Command(command = "calc_move", args = None)

        elif response_tokens[0] == 'R':
            return Command(command = "relative_move", args = response_tokens[1:])

        elif response_tokens[0] == 'speed':
             return Command(command = "speed", args = response_tokens[1:])

        elif response_tokens[0] == 'pos':
            print("Position: {: 3.0f}  {: 3.0f}  {: 3.0f}  {: 3.0f} {: 3.0f} {: 3.0f} {: 3.0f}".format(self.dog.x, self.dog.y, self.dog.z, self.dog.roll, self.dog.pitch, self.dog.yaw, self.dog.speed))

        elif response_tokens[0] == 'L':
            return Command(command = "absolute_leg_move", args = response_tokens[1:])

        elif response_tokens[0] == 'walk':
            self.dog.dataplot.start_recording(10)
            return Command(command = "walk", args = response_tokens[1:])

        elif response_tokens[0] == 'walk_p':
            return Command(command = "walk_params", args = response_tokens[1:])

        elif response_tokens[0] == 'record':
            return Command(command = "start_dataplot", args = None)

        elif response_tokens[0] == 'stop_record':
            return Command(command = "stop_dataplot", args = None)

        elif response_tokens[0] == 'show_record':
            return Command(command = "show_dataplot", args = None)

        elif response_tokens[0] == 'start_playback':
            return Command(command = "start_playback", args = response_tokens[1:])
        
        elif response_tokens[0] == 'stop_playback':
            return Command(command = "end_playback", args = None)

        elif response_tokens[0] == 'prance':
            
            if len(response_tokens) > 1:
                return Command(command = "prance_n", args = int(response_tokens[1]))
            else:
                return Command(command = "prance", args = None)


    def get_raw_command(self):
        """ Reads input from stdin and returns it if there is an input

        Returns:
            [String, None]: returned single-line contents from stdin or None
        """
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            raw_cmd = sys.stdin.readline()
            if raw_cmd:
                return raw_cmd[:-1]  # removes \n
        else:
           return None

    def print_help(self):
        print("[space]: Home")
        print("Dog absolute move: A [x] [y] [z] [roll, optional] [pitch, optional] [yaw, optional] [speed, optional]")
        # print("Dog relative move: R {x, y, z, roll, pitch, yaw} [value]")
        print("Leg absolute move: L [n] [x] [y] [z]")
        print("Prance: prance [num]")
        print("Walk: walk [f, b, tl, tr, sl, sr] [n]")
        print("Walk Parameters: walk_p [step_len] [lift_amnt] [playtime] [r trim, optional]")
        print("Sleep: sleep")
        print("Die: die")
        print("Resource usage: res")
        print("Reboot: reboot")
        print("Error: error")

            
# def cmd_control(dog):

#         if response_tokens[0] == 'R':
            
#             dog.set_desired_to_position()

#             if response_tokens[1] in {'x', 'y', 'z', 'roll', 'pitch', 'yaw'}:
#                 new_val = getattr(dog, 'desired_' + response_tokens[1]) + float(response_tokens[2])
#                 setattr(dog, 'desired_' + response_tokens[1], new_val)

#             dog.desired_speed = 20
#             dog.go_desired()
#             print("Relative move: {} {}".format(response_tokens[1], response_tokens[2]))
