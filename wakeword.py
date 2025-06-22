import os
import time

import pvporcupine

import config
from Recorder import get_recorder


porcupine: pvporcupine.Porcupine|None = None

def get_porcupine() -> pvporcupine.Porcupine:
    global porcupine
    if not porcupine:
        if config.lang == "fr":
            porcupine = pvporcupine.create(
                access_key=os.environ.get("PICOVOICE_ACCESS_KEY"),
                keyword_paths=["./models/Artemis_fr_linux_v3_0_0.ppn"],
                model_path="./models/porcupine_params_fr.pv"
            )
        else:
            porcupine = pvporcupine.create(
                access_key=os.environ.get("PICOVOICE_ACCESS_KEY"),
                keyword_paths=["./models/Artemis_en_linux_v3_0_0.ppn"]
            )
    return porcupine


def wait_for_wakeword():
    processed_frame_id = None
    while True:
        if not len(get_recorder().frames) or processed_frame_id == get_recorder().last_frame_id:
            time.sleep(0.01)
            continue
        frame = get_recorder().frames[-1]
        processed_frame_id = get_recorder().last_frame_id
        if get_porcupine().process(frame) != -1:
            break
