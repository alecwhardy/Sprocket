import threading

from flask import Flask, Response, render_template
from flask_socketio import SocketIO, emit

from threading import Lock

import WebCam

app = Flask(__name__)
dog = None  # Loaded after start_server_thread call
socketio = SocketIO(app)
thread = None
thread_lock = Lock()

# For MJPG (with Matplotlib), see https://tree.rocks/a-simple-way-for-motion-jpeg-in-flask-806b8bfefa96

@app.route("/")
def main():
    pass
    print(dog)
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route("/webcam_stream")
def mjpeg():
    return Response(WebCam.gather_webcam_img(), mimetype='multipart/x-mixed-replace; boundary=frame')


def start_server_thread(dog_in):
    global dog
    dog = dog_in
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False, host='0.0.0.0')).start()

@socketio.on('connect')
def on_connect(auth):
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(send_data)
    emit('connect', {'data': 'Connected', 'count': 0})

def send_data():
    """Example of how to send server generated events to clients."""
    global dog
    count = 0
    socketio.emit('log', {'data': 'Successful connection to socket.  Receiving dog_data', 'count': str(count)})
    while True:
        socketio.sleep(0.1) #Send data every 0.1 seconds
        count += 1
        # socketio.emit('my_response',
        #               {'data': 'Bitcoin current price (USD): ' + str(price), 'count': str(count)})
        socketio.emit('dog_data',
                        {
                            'x': "{:.2f}".format(dog.x),
                            'y': "{:.2f}".format(dog.y),
                            'z': "{:.2f}".format(dog.z),
                            'roll': "{:.2f}".format(dog.roll),
                            'pitch': "{:.2f}".format(dog.pitch),
                            'yaw': "{:.2f}".format(dog.yaw),
                            'desired_x': "{:.2f}".format(dog.desired_x),
                            'desired_y': "{:.2f}".format(dog.desired_y),
                            'desired_z': "{:.2f}".format(dog.desired_z),
                            'desired_roll': "{:.2f}".format(dog.desired_roll),
                            'desired_pitch': "{:.2f}".format(dog.desired_pitch),
                            'desired_yaw': "{:.2f}".format(dog.desired_yaw),
                        })
        

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')