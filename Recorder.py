import os
import struct
import threading
import time
import wave

import pvcobra
import pvrecorder

from Style import Style


class Recorder:
    def __init__(self):
        self.frames = []
        self.last_frame_id = 0
        self.is_voice_active = False
        self.running = False
        self.is_recording = False

        self.recorder = pvrecorder.PvRecorder(device_index=-1, frame_length=512)
        self.cobra = pvcobra.create(access_key=os.environ.get("PICOVOICE_ACCESS_KEY"))

    def recorder_task(self):
        self.recorder.start()

        while self.running:
            frame = self.recorder.read()
            self.frames.append(frame)
            if len(self.frames) > 30:
                self.frames.pop(0)
            self.last_frame_id += 1
            self.is_voice_active = self.cobra.process(frame) >= 0.5

        self.recorder.stop()

    async def record_while_speaking(self, output_path: str, record_before_speaking: bool):
        if not self.running:
            self.start()

        self.is_recording = True
        start_speaking = False
        frame_not_speak = 0
        processed_frame_id = None

        wav_file = wave.open(output_path, 'wb')
        wav_file.setnchannels(1)  # Mono recording
        wav_file.setsampwidth(2)  # Sample width in bytes (16-bit = 2 bytes)
        wav_file.setframerate(self.recorder.sample_rate)

        if record_before_speaking:
            for frame in self.frames:
                frame_bytes = struct.pack('<' + ('h' * len(frame)), *frame)
                wav_file.writeframes(frame_bytes)

        print(Style.GRAY + "Recording")

        while not start_speaking or frame_not_speak < 30:
            if processed_frame_id == self.last_frame_id:
                time.sleep(0.01)
                continue

            frame = self.frames[-1]
            processed_frame_id = self.last_frame_id

            if not start_speaking and self.is_voice_active:
                start_speaking = True
                print(Style.GRAY + "Listening")

            if start_speaking or record_before_speaking:
                frame_bytes = struct.pack('<' + ('h' * len(frame)), *frame)
                wav_file.writeframes(frame_bytes)

            if self.is_voice_active:
                frame_not_speak = 0
            else:
                frame_not_speak += 1
        self.is_recording = False

    def start(self):
        self.running = True
        threading.Thread(target=self.recorder_task).start()

    def stop(self):
        self.running = False


recorder: Recorder | None = None


def get_recorder() -> Recorder:
    global recorder
    if not recorder:
        recorder = Recorder()
        recorder.start()
    return recorder
