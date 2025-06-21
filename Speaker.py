import threading

import pygame


class Speaker:
    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.Lock()
        self._playing = False

    def play(self, file_path: str):
        self.stop()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        self._playing = True

    def stop(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self._playing = False

    @property
    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def wait_until_finished(self):
        while self.is_playing:
            pass


speaker = Speaker()
