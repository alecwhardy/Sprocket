from os import truncate
import serial
from XYZrobotServo import XYZrobotServo

ser = serial.Serial('/dev/ttyS0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

servos = []
for i in range(12):
    servos.append(XYZrobotServo(ser, i+1, debug=True))
    st = servos[i].readStatus()
    print(st.position)

servos[0].setPosition(512, 0)
servos[9].setPosition(512, 0)