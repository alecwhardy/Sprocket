import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
import threading

from flask import Flask, Response

app = Flask(__name__)
dog = None  # Loaded after start_server_thread call

# For MJPG (with Matplotlib), see https://tree.rocks/a-simple-way-for-motion-jpeg-in-flask-806b8bfefa96

@app.route("/")
def main():
    pass
    print(dog)
    return "<h1>Hello from Sprocket</h1>"

def random_noise_img():
    while True:
        time.sleep(0.01)
        img = np.random.randint(0, 255, size=(512, 512, 3), dtype=np.uint8)
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

def random_data_plot_img():

    def generate_random_data_plot_img():
        x1 = np.random.randn(5)
        x2 = np.random.randn(10)
        
        fig = plt.figure(figsize=(10, 10))
        plt.plot(x1)
        plt.plot(x2)
        plt.close(fig)
        fig.canvas.draw()
        return np.array(fig.canvas.buffer_rgba())

    while True:
        time.sleep(0.05)
        img = generate_random_data_plot_img()
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

@app.route("/mjpeg")
def mjpeg():
    return Response(gather_webcam_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

# setup camera and resolution
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
def gather_webcam_img():
    while True:
        time.sleep(0.1)
        _, img = cam.read()
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

def start_server_thread(dog_in):
    global dog
    dog = dog_in
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False, host='0.0.0.0')).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0')