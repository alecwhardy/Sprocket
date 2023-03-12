from Controls.ConsoleControl import ConsoleControl
from Controls.XboxControl import XboxControl
from Commands import *
import functions

from collections import deque
from Recordings import MotionPlayback

PLAYBACK_VERBOSE = True

class CommandHandler:
    """ Grabs the desired commands from the different controllers and enqueues them
    """

    xbox_controller_enable = True
    
    motion_playback = None
    motion_playback_loop = False

    def __init__(self, dog):
        self.dog = dog
        self.commands = Commands(self.dog)
        self.command_queue = deque()

        self.console_controller = ConsoleControl(self.dog)
        self.xbox_controller = XboxControl(self.dog)
        if not self.xbox_controller.CONNECTED:
            self.xbox_controller_enable = False

    def get_new_commands(self):

        # TODO: If multiple commands of the same type in the queue, delete less important ones
        console_command = self.console_controller.get_commands()
        if console_command is not None:
            self.command_queue.append(console_command)

        if self.xbox_controller_enable:
            # Handle XBOX commands here
            xbox_command = self.xbox_controller.get_commands()
            if xbox_command is not None and xbox_command != [None]:
                for command in xbox_command:
                    self.command_queue.append(command)

        if self.motion_playback is not None:
            # We are doing a motion playback.  Handle those commands.
            # Note: This can be easily be ammended to handle non-motion commands as well.  Do so here.
            playback_command = self.motion_playback.get_command()

            if playback_command is not None:
                if self.motion_playback_loop and playback_command.command == "end_playback":
                    self.motion_playback.rewind()
                    return
                self.command_queue.append(playback_command)
                if PLAYBACK_VERBOSE:
                    print(str(int(functions.millis())) + " " + str(playback_command))


        # Handle Behavior commands here

    def handle_commands(self):
        # TODO: If multiple commands of the same type in the queue, delete less important ones
        while len(self.command_queue) > 0:
            self.handle_command()

    def handle_command(self):
        if len(self.command_queue) > 0:
            self.current_command = self.command_queue.popleft()
            if self.current_command.command != 'read_voltage':
                self.dog.cmd_logger.info(self.current_command)
            command_method = getattr(self.commands, self.current_command.command)
            if self.current_command.args is None:
                result = command_method()
            else:
                result = command_method(self.current_command.args)
            
            

