import subprocess

def play(file):
    player = subprocess.Popen(["mplayer", "-ao", "alsa:device=hw=0,0", file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == '__main__':
    play('Audio/OceanMan.wav')
    while(True):
        print("Hi")