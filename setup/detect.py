# So we can import modules from the top level directory
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import time, serial
from XYZrobotServo import XYZrobotServo

MAX_SERVO_ID = 20
FLASH_LED = True

def detect_servos(serial_stream):

    for servo_ID in range(MAX_SERVO_ID):
        servo_ID += 1
        detected = detect_servo(servo_ID, serial_stream)
        if detected and FLASH_LED:
            servo = XYZrobotServo(serial_stream, servo_ID)
            servo.set_LED_alarm_policy()     # Allow user-configurable LEDs
            time.sleep(0.01)
            servo.set_LED(XYZrobotServo.LED_Color.MAGENTA)     # Set LED to magenta
            time.sleep(1)
            servo.set_LED(XYZrobotServo.LED_Color.WHITE)       # Set LED back to white
            time.sleep(0.01)
            servo.reset_LED_alarm_policy()   # Reset LED control back to Alarm


def detect_servo(servo_ID, serial_stream):
    '''
    Returns TRUE if the servo_ID is detected
    '''

    servo = XYZrobotServo(serial_stream, servo_ID)
    status = servo.readStatus()
    if servo.lastComError is None or servo.lastComError == XYZrobotServo.CommunicationError.NoError:
        # We detected the servo and there is no error!
        print("Servo detected. ID: {}".format(servo_ID))
        return True
    elif servo.lastComError == XYZrobotServo.CommunicationError.HeaderTimeout:
        # Servo not detected, return false
        return False
    else:
        # We detected a servo, but there is an error with that servo
        print("Servo detected.  ID: {}  Error code: {}".format(servo_ID, servo.lastComError))
        return True

def do_detect():
    print("Detecting Servos")

    # Detect at 9600 baud
    print("Searching at 9600 Baud: ")
    ser = serial.Serial('/dev/ttyS0', baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
    detect_servos(ser)
    ser.close

    # Detect at 19200 baud
    print("Searching at 19200 Baud: ")
    ser = serial.Serial('/dev/ttyS0', baudrate = 19200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
    detect_servos(ser)
    ser.close

    # Detect at 57600 baud
    print("Searching at 57600 Baud: ")
    ser = serial.Serial('/dev/ttyS0', baudrate = 57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
    detect_servos(ser)
    ser.close

    # Detect at 115200 baud
    print("Searching at 115200 Baud: ")
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
    detect_servos(ser)
    ser.close


if __name__ == '__main__':
    do_detect()