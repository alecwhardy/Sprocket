import socket
import time
import random
import pickle, struct, json
import cv2
from Networking.SensorDataPacket import SensorDataPacket

# https://gist.github.com/kittinan/e7ecefddda5616eab2765fdb2affed1b


host = '192.168.0.141'
#host = 'hardydog'
port = 1241

cam = cv2.VideoCapture(2)
#Set 480p
cam.set(3, 320)
cam.set(4, 240)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

cam.set(cv2.CAP_PROP_EXPOSURE,-4) # Set exposure to 80ms https://www.principiaprogramatica.com/2017/06/11/setting-manual-exposure-in-opencv/

sdp = SensorDataPacket()

WEBCAM = False
DATA = True

def run_socket_server(dog, servos):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print("Socket server is awaiting a connection...")
    conn, addr = s.accept()

    with conn:
        print(f"Connected by {addr}")
        while True:
            
            if WEBCAM:
                ret, frame = cam.read()
                result, frame = cv2.imencode('.jpg', frame, encode_param)
                data = pickle.dumps(frame, 0)
                size = len(data)
                conn.sendall(struct.pack(">L", size) + data)

            
            if DATA:

                pwms = []
                for servo in servos:
                    pwm_stat = servo.readStatus().pwm
                    pwms.append(pwm_stat)
                sdp.pwms = tuple(pwms)
                
                data = sdp.toJSON().encode('utf-8')
                send_sz = '%d\n' % len(data)
                conn.send(send_sz.encode('utf-8'))
                conn.sendall(data)



            #data = bytes('A', 'utf-8')
            #conn.sendall(data)

            

            time.sleep(1) # 1 updates per second



if __name__ == '__main__':
    run_socket_server(None, None)