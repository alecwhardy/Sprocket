from xbox360controller import Xbox360Controller
import os, time

if __name__ == '__main__':
    os.system('sudo chmod 666 /sys/class/leds/xpad0/brightness')
    controller = Xbox360Controller(0, axis_threshold=0.2)
    while True:
        print("{:3.5f} {:3.5f}".format(controller.hat.x,controller.hat.y))
        time.sleep(.1)