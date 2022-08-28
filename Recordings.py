from collections import deque
from functions import *
import Commands

class MotionPlayback:

    PLAYBACK_FROM_RAM = 1
    PLAYBACK_FROM_FILE = 2
    PLAYBACK_FROM_STREAM = 3 # Not yet implemented, for playback from web socket

    playback_source = None
    playback_queue = deque()
    playback_queue_copy = None

    playback_start_time = 0
    playback_cursor_time = 0 # The time (ms) at which the current frame should end (from the start of the playback)
    
    current_frame_raw = ""
    current_frame_start_time = 0
    current_frame_duration = 0



    def load_from_file(self, file):
        # self.playback_source = self.PLAYBACK_FROM_FILE

        # Let's cheat and just load the whole file into RAM
        # This can be updated in the future to save memory, if that becomes an issue.
        self.playback_source = self.PLAYBACK_FROM_RAM
        with open("Recordings/" + file + ".csv", 'r') as file:
            for line in file:
                if line[0] == '#' or line.strip() == '':
                    continue
                self.playback_queue.append(line.strip())

        # Save a copy of the entire queue so we can restore it if we do a rewind()
        # If we update this later to save memory, we will just rewind the file.
        self.playback_queue_copy = self.playback_queue.copy()


    def load_test(self):
        self.playback_source = self.PLAYBACK_FROM_RAM
        
        # Load the test commands
        self.playback_queue.append("1000, A, 0, 0, 100, 0, 0, 0, 50")  # Frame Duration (ms), "Absolute Move", args (x, y, z, roll, pitch, yaw)
        self.playback_queue.append("1000, A, 0, 0, 150, 0, 0, 0, 50")
        
        # Save a copy of the entire queue so we can restore it if we do a rewind()
        self.playback_queue_copy = self.playback_queue.copy()

    def rewind(self):
        if self.playback_source == self.PLAYBACK_FROM_RAM:
            self.playback_queue = self.playback_queue_copy.copy()
            self.current_frame_start_time = 0
        

    def get_next_frame(self):
        if self.playback_source == self.PLAYBACK_FROM_RAM:

            if len(self.playback_queue) <= 0:
                return None

            new_frame = self.playback_queue.popleft()
            # TODO: Check the frame is valid
            
            new_frame_tokens = new_frame.split(",")
            self.current_frame_duration = int(new_frame_tokens[0])
            self.playback_cursor_time += self.current_frame_duration
            return new_frame

    def generate_command(self, frame):
        """Generates a Command object from the contents of a frame string

        Args:
            frame (str): Frame string

        Returns:
            Command: Return command that can be handled by the CommandHandler
        """

        if frame is None:
            return Commands.Command(command = "end_playback")

        frame_tokens = frame.split(",")
        
        if frame_tokens[1].strip() == 'A':
            # Absolute move command
            return Commands.Command(command = "absolute_move", args = frame_tokens[2:])
        elif frame_tokens[1].strip() == 'CA':
            # Calculate dog absolute position
            return Commands.Command(command = "calc_absolute_position", args = frame_tokens[2:])
        elif frame_tokens[1].strip() == 'CL':
            # Calculate a leg's absolute position
            return Commands.Command(command = "calc_leg_position", args = frame_tokens[2:])
        elif frame_tokens[1].strip() == "CM":
            # Move to the calculated position
            return Commands.Command(command = "calc_move", args = None)


    def get_command(self):

        ret_cmd = None
        cur_millis = millis()

        if self.playback_start_time == 0:
            # We are starting a new playback
            self.playback_cursor_time = 0
            self.playback_start_time = cur_millis
            self.current_frame_start_time = self.playback_start_time
            self.current_frame_raw = self.get_next_frame()
            ret_cmd =  self.generate_command(self.current_frame_raw)

        if cur_millis >= self.playback_start_time + self.playback_cursor_time:
            self.current_frame_start_time = cur_millis
            self.current_frame_raw = self.get_next_frame()
            ret_cmd = self.generate_command(self.current_frame_raw)

        # if ret_cmd is not None:
        #     print("Returning Recording Command: " + str(ret_cmd))
        return ret_cmd


if __name__ == '__main__':
    mp = MotionPlayback()
    mp.load_test()
    while True:
        command = mp.get_command()
        if command is not None:
            print(command)
            if command.command == "end_playback":
                exit()


# TODO: Uptown Funk Dance!