import adafruit_bno055     #pip3 install adafruit-circuitpython-bno055
import board

class IMU:

    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_bno055.BNO055_I2C(self.i2c)

    def get_euler(self):
        return self.sensor.euler


if __name__ == "__main__":
    
    imu = IMU()
    while True:
        print(imu.get_euler())