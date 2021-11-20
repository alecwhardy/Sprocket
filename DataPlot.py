from functions import *
import plotext as plt

class DataPlot:
    
    last_update = 0
    update_period = 0
    recording = False
    recorded_data = []

    def start_recording(self, update_period = 100):
        self.recording = True
        self.last_update = millis()
        self.update_period = update_period
        self.recorded_data = []

    def record_loop(self, data):
        """ Run this in a loop and pass in data.  When appropriate, the data will be recorded

        Args:
            data ([type]): [description]
        """

        if not self.recording:
            return

        cur_millis = millis()
        if not self.last_update + self.update_period < cur_millis:
            # Return if we are not ready to record another data point
            return
        self.last_update = cur_millis

        self.recorded_data.append(data)

    def stop_recording(self):
        self.recording = False

    def show_plot(self):
        plt.clf()
        plt.plot(self.recorded_data)
        plt.show()







    

