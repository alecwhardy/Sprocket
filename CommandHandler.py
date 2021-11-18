from Controls.ConsoleControl import ConsoleControl
from Controls.XboxControl import XboxControl
from Commands import *

from collections import deque

class CommandHandler:
    """ Grabs the desired commands from the different controllers and enqueues them
    """

    xbox_controller_enable = True

    def __init__(self, dog):
        self.dog = dog
        self.commands = Commands(self.dog)
        self.command_queue = deque()

        self.console_controller = ConsoleControl(self.dog)
        self.xbox_controller = XboxControl(self.dog)

    def get_new_commands(self):

        console_command = self.console_controller.get_commands()
        if console_command is not None:
            self.command_queue.append(console_command)

        if self.xbox_controller_enable:
            # Handle XBOX commands here
            xbox_command = self.xbox_controller.get_commands()
            if xbox_command is not None and xbox_command != [None]:
                for command in xbox_command:
                    self.command_queue.append(command)


        # Handle Behavior commands here

    def handle_commands(self):
        while len(self.command_queue) > 0:
            self.handle_command()

    def handle_command(self):
        if len(self.command_queue) > 0:
            current_command = self.command_queue.popleft()
            command_method = getattr(self.commands, current_command.command)
            if current_command.args is None:
                result = command_method()
            else:
                result = command_method(current_command.args)
            
            

