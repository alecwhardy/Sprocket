import threading, time

x = 0

def inc():
    global x
    
    while True:
        x = x+1
        time.sleep(1)

if __name__ == "__main__":

    t1 = threading.Thread(target=inc, args=())
    t1.start()

    while True:
        print(x)
        
