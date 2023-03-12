import pyaudio
import wave

from threading import Thread

#pip install pyaudio
# sudo apt-get install python3-pyaudio 

OUTPUT_DEVICE = 0

class AudioFile:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True,
            output_device_index = OUTPUT_DEVICE
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()

def play_wav_sync(wav_filename):
    a = AudioFile(wav_filename)
    a.play()
    a.close()
    

def play_wav_async(wav_filename):
    t = Thread(target = play_wav_sync, args=(wav_filename, ))
    t.start()

if __name__ == '__main__':
    play_wav_async("Audio/pee.wav")
