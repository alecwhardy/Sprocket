from xbox360controller import Xbox360Controller
import os, time, serial
from XYZrobotServo import XYZrobotServo

if __name__ == '__main__':
    # os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')
    # controller = Xbox360Controller(0, axis_threshold=0.2)
    # while True:
    #     print("{:3.5f} {:3.5f}".format(controller.hat.x,controller.hat.y))

    #     if controller.button_trigger_r.is_pressed:
    #         print("Button Trigger R")

    #     time.sleep(.1)

    # Servo Response Check
    pass
    ser = serial.Serial('/dev/ttyS0', baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)
    servo_list = []
    for i in range(12):
        servo_list.append(XYZrobotServo(ser, i+1, debug=False))
    

    start_time = time.time()
    
    for servo in servo_list:
        servo.readStatus()

    print("--- %s seconds ---" % (time.time() - start_time))