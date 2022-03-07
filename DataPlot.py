from functions import *
import plotext as plt
import numpy as np

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
        if len(self.recorded_data) > 1:
            l = np.array(self.recorded_data)
            self.recorded_data = l[(l>np.quantile(l,0.1)) & (l<np.quantile(l,0.9))].tolist()

    def print_average_filtered(self):
        if len(self.recorded_data) > 1:
            avg = sum(self.recorded_data) / len(self.recorded_data)
            print("Performance: {}".format(avg))

    def show_plot(self):
        plt.clf()
        plt.plot(self.recorded_data)
        plt.show()







    

