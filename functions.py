import time

def lin_interp(x1, x2, x3, y1, y3):
    return (((x2-x1)*(y3-y1))/(x3-x1))+y1

def millis():
    return time.time()*1000