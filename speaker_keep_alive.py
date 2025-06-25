import threading
import time

from pydub import AudioSegment

from Speaker import speaker

MS = 100

num_samples = 44100 * MS // 1000
beep = AudioSegment(bytes([8, 0] * num_samples), frame_rate=44100, sample_width=2, channels=1)
beep.export("noise.mp3", format="mp3")


def start():
    print("speaker keep alive started")
    threading.Thread(target=loop).start()


def loop():
    while True:
        if not speaker.is_playing:
            speaker.play("noise.mp3")
        time.sleep(60)
