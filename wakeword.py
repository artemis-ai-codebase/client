import os
import time

import pvporcupine

import config
from Recorder import recorder


def get_porcupine():
    if config.lang == "fr":
        return pvporcupine.create(
            access_key=os.environ.get("PICOVOICE_ACCESS_KEY"),
            keyword_paths=["./models/Artemis_fr_linux_v3_0_0.ppn"],
            model_path="./models/porcupine_params_fr.pv"
        )
    else:
        return pvporcupine.create(
            access_key=os.environ.get("PICOVOICE_ACCESS_KEY"),
            keyword_paths=["./models/Artemis_en_linux_v3_0_0.ppn"]
        )


def wait_for_wakeword():
    processed_frame_id = None
    while True:
        if not len(recorder.frames) or processed_frame_id == recorder.last_frame_id:
            time.sleep(0.01)
            continue
        frame = recorder.frames[-1]
        processed_frame_id = recorder.last_frame_id
        if porcupine.process(frame) != -1:
            break


porcupine = get_porcupine()
