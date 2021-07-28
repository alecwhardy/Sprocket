from os import truncate
import serial
from XYZrobotServo import XYZrobotServo

ser = serial.Serial('/dev/ttyS0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

servo = XYZrobotServo(ser, 1, debug=True)
servo.readStatus()