import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import time, serial
from XYZrobotServo import *


def try_to_change_ID(old_ID, new_ID, baud = 115200):

    ser_old = serial.Serial('/dev/ttyS0', baudrate = baud, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
    servo_old = XYZrobotServo(ser_old, old_ID)

    ser_new = serial.Serial('/dev/ttyS0', baudrate = baud, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1)
    servo_new = XYZrobotServo(ser_new, new_ID)

    # Make sure we can communicate with the servo with its current ID
    status = servo_old.readStatus()
    if servo_old.lastComError != XYZrobotServo.CommunicationError.NoError:
        print("Error communicating with servo using ID {} and baudrate {}.".format(old_ID, baud))
        print(servo_old.lastComError)
        return False

    # Set the ACK policy to default so we can later read back values from EEPROM
    servo_old.writeAckPolicyRam(XYZrobotServo.ServoAckPolicy.ONLY_READ_AND_STAT)

    # Make sure there is not another servo using the new ID
    status_new = servo_new.readStatus()
    if servo_new.lastComError != XYZrobotServo.CommunicationError.HeaderTimeout:
        print("There is already a servo using the new ID {}".format(new_ID))
        return False

    # Change ID in EEPROM and RAM
    servo_old.writeIDEEPROM(new_ID)
    time.sleep(.01)
    servo_old.writeIDRAM(new_ID)
    time.sleep(.01)

    # Make sure the servo is responding to the new ID
    status = servo_new.readStatus()
    if servo_new.lastComError != XYZrobotServo.CommunicationError.NoError:
        print("Error communicating with servo using the new ID.".format(old_ID))
        print(servo_new.lastComError)
        return False

    # Make sure the ID in EEPROM is correct
    EEPROM_ID = servo_new.readIDEEPROM()
    if servo_new.lastComError != XYZrobotServo.CommunicationError.NoError:
        print("Failed to read ID from EEPROM.")
        print(servo_new.lastComError)
        return False
    if EEPROM_ID != new_ID:
        print("Incorrect new ID in EEPROM")
        return False

    return True


if __name__ == '__main__':
    success = try_to_change_ID(1, 2, 115200)
    