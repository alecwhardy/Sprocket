import adafruit_bno055     #pip3 install adafruit-circuitpython-bno055
import board
import time
import math

class IMU:

    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_bno055.BNO055_I2C(self.i2c)

    def get_euler(self):
        return self.sensor.euler

    def get_linear_rss(self):
        accel = self.sensor.linear_acceleration
        try:
            rss = math.sqrt(accel[0]*accel[0] + accel[1]*accel[1] + accel[2]*accel[2])
        except TypeError:
            # Sensor wasn't ready for another update
            return -1
        return rss


if __name__ == "__main__":
    
    imu = IMU()
    while True:
        print(imu.get_linear_rss())
        time.sleep(1)