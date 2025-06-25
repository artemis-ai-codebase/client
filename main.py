import os

import urllib3

import speaker_keep_alive
from Agent import Agent
from Style import Style
from auth import get_websocket_token

urllib3.disable_warnings()
speaker_keep_alive.start()
try:
    token = get_websocket_token()
    agent = Agent(token)
    agent.run_agent()
except KeyboardInterrupt:
    print(Style.RED + "\nKeyboard interrupt, exiting")
    os._exit(0)
