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
    
    def get_heading(self):
        try:
            return self.sensor.euler[0]
        except:
            return 0

    def get_gyro_rss(self):
        
        gyro = self.sensor.gyro
        try:
            rss = math.sqrt(gyro[0]*gyro[0] + gyro[1]*gyro[1] + gyro[2]*gyro[2])
        except TypeError:
            # Sensor wasn't ready for another update
            return -1
        return rss

    def get_accel_gyro_rss(self):
        accel = self.sensor.linear_acceleration
        gyro = self.sensor.gyro
        try:
            rss = math.sqrt(accel[0]*accel[0] + accel[1]*accel[1] + accel[2]*accel[2] + gyro[0]*gyro[0] + gyro[1]*gyro[1] + gyro[2]*gyro[2])
        except TypeError:
            # Sensor wasn't ready for another update
            return -1
        return rss

    def get_mag(self):
        return self.sensor.magnetic


if __name__ == "__main__":
    
    imu = IMU()
    while True:
        print(imu.get_euler())
        time.sleep(1)