import os
import time

from dotenv import load_dotenv

load_dotenv(".env", override=True)
if os.path.exists(".env.local"):
    load_dotenv(".env.local", override=True)
time.sleep(1)
api_endpoint = os.getenv("API_ENDPOINT")
websocket_endpoint = os.getenv("WEBSOCKET_ENDPOINT")
device_name = os.getenv("DEVICE_NAME")
have_gui = int(os.getenv("HAVE_GUI"))
lang = os.getenv("LANG")
