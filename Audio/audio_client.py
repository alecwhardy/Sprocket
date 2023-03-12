# From https://gist.github.com/fopina/3cefaed1b2d2d79984ad7894aef39a68

import pyaudio
import socket
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 4096

HOST = '192.168.0.12'
PORT = 4444

OUTPUT_DEVICE = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, output_device_index = OUTPUT_DEVICE, frames_per_buffer=CHUNK)

try:
    while True:
        data = s.recv(CHUNK)
        stream.write(data)
except KeyboardInterrupt:
    pass

print('Shutting down')
s.close()
stream.close()
audio.terminate()