# So we can import modules from the top level directory
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import time, serial
from XYZrobotServo import XYZrobotServo
from detect import do_detect
from changeId import try_to_change_ID

def clear_screen():
    if os.name == 'nt':
        system('cls')
    else:
       os.system('clear')

def print_usage():
    print("\nCommands: ")
    print("D: Detect Servos")
    print("C {Old ID} {New ID} {Optional: Baud.  Defaults to 115200}: Change ID")
    print("Q: Quit")

if __name__ == '__main__':
    
    clear_screen()
    print("Welcome to Sprocket Setup")
    
    while True:
        print_usage()
        command = input("\n")

        if len(command) < 1:
            continue

        if command[0] == 'D':
            do_detect()
            print("\nDone detecting Servos\n")

        elif command[0] == 'C':
            try:
                tokens = command.split(" ")
                old_ID = int(tokens[1])
                new_ID = int(tokens[2])
                if len(tokens) > 3:
                    baud = int(tokens[3])
                else:
                    baud = 115200
                
                success = try_to_change_ID(old_ID, new_ID, baud)
                if success:
                    print("\nSuccessfully changed ID")
                else:
                    print("\nID change failed.")

            except e:
                print("Invalid Command.  Enter Old ServoID and New ServoID.  Ex. 'C 1 4'")
                print("If using a baud-rate other than 115200, Enter baud-rate after New ServoID")

        elif command[0] == 'Q':
            exit()

        else:
            print("Invalid Command")
