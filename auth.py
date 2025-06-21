import os
import time

import requests
from gtts import gTTS

from Speaker import speaker
from config import api_endpoint


def request_api(url, json = None, allow_errors = False):
    res = requests.post(
        url=api_endpoint + url,
        headers={"Content-Type": "application/json"},
        json=json or {},
        verify=api_endpoint.startswith("https://")
    )
    if not res.ok:
        if allow_errors:
            return None
        with open("error.html", "wb") as f:
            f.write(res.content)
        print("Error while fetching", url)
        os._exit(1)
    else:
        return res.json()


def say(text: str):
    tts = gTTS(text, lang="en")
    tts.save("temp.mp3")
    speaker.play("temp.mp3")
    speaker.wait_until_finished()


def get_refresh_token(recursion = False):
    refresh_token = None
    if os.path.exists(".refresh_token"):
        with open(".refresh_token", "r") as f:
            refresh_token = f.read()
    else:
        data = request_api("/device/code")
        code, secret = data["code"], data["secret"]
        success = False
        print("The code is", code)
        for _ in range(10):
            say("The code is " + ", ".join(code))
            time.sleep(5)
            data = request_api("/device/token", {"code": code, "secret": secret}, allow_errors=True)
            if data:
                refresh_token = data["refreshToken"]
                with open(".refresh_token", "w") as f:
                    f.write(refresh_token)
                print("Code validated ! token refreshed")
                success = True
                say("Code validated !")
                break
            else:
                print("Code invalid")
        if not success:
            say("Failed to validate code, exiting.")
            print("Failed to validate code, exiting.")
            os._exit(1)
    data = request_api("/refresh", {"refreshToken": refresh_token}, allow_errors=True)
    if not data:
        print("Refresh token invalid")
        os.remove(".refresh_token")
        if not recursion:
            return get_refresh_token(recursion=True)
        else:
            print("Error while refreshing token")
            os._exit(1)
    print("Refresh token validated !")
    return refresh_token

def get_websocket_token():
    data = request_api("/websocket-token", {"refreshToken": get_refresh_token()})
    return data["websocketToken"]
