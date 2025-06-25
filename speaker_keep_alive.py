import os
import threading
import time

from pydub import AudioSegment

from Speaker import speaker

if not os.path.exists("silence.mp3"):
    silence = AudioSegment.silent(duration=100)
    silence.export("silence.mp3", format="mp3")


def start():
    print("speaker keep alive started")
    threading.Thread(target=loop).start()


def loop():
    while True:
        if not speaker.is_playing:
            speaker.play("silence.mp3")
        time.sleep(60)
