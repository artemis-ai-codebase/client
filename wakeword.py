import os
import time

import pvporcupine

from Recorder import get_recorder
from config import get_platform

porcupine: pvporcupine.Porcupine | None = None


def get_porcupine() -> pvporcupine.Porcupine:
    global porcupine
    if not porcupine:
        porcupine = pvporcupine.create(
            access_key=os.environ.get("PICOVOICE_ACCESS_KEY"),
            keyword_paths=[f"./models/Artemis_fr_{get_platform()}_v3_0_0.ppn"],
            model_path="./models/porcupine_params_fr.pv"
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
