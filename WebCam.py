import cv2
import time

import numpy as np
import matplotlib.pyplot as plt

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
def gather_webcam_img():
    while True:
        time.sleep(0.1)
        _, img = cam.read()
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')
        
def random_noise_img():
    """Returns an image of random noise.
    
    Usage:
    Use as a Flask app route as follows:
    @app.route("/display_page_name")
    def display_random_noise_image:
        return Response(random_noise_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

    Yields:
        Bytes: JPEG motion image of random noise
    """
    while True:
        time.sleep(0.01)
        img = np.random.randint(0, 255, size=(512, 512, 3), dtype=np.uint8)
        _, frame = cv2.imencode('.jpg', img)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')


def random_data_plot_img():
    """Used to return an image of a plot (matplotlib) that generates and displays garbage data
    """

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