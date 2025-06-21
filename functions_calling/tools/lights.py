from yeelight import discover_bulbs, Bulb
from functions_calling.tool_decorator import tool
from typing import Literal

bulbs = []


def get_bulbs():
    global bulbs
    if len(bulbs) == 0 or not bulbs[0].get_properties():
        bulbs = [Bulb(b["ip"], auto_on=True) for b in discover_bulbs()]
    return bulbs


@tool
def set_lights_brightness(percent: int, operation: Literal["set", "add", "sub"] = "set"):
    """
    Set chamber's lights brightness. If the user want to increase or decrease add don't specify percent, put 20%.
    :param percent: (int) lights brightness
    :param operation: (Literal["set", "add", "sub"]) The operation to apply with the given percent. Default is "set".
    """
    if operation == "add":
        percent = int(get_bulbs()[0].get_properties()["current_brightness"]) + percent
    elif operation == "sub":
        percent = int(get_bulbs()[0].get_properties()["current_brightness"]) - percent

    percent = max(0, min(100, percent))

    for bulb in get_bulbs():
        bulb.set_brightness(percent)


@tool
def set_lights_rgb(r: int, g: int, b: int):
    """
    Set chamber's lights color using RGB values
    :param r: (int) lights red
    :param g: (int) lights green
    :param b: (int) lights blue
    """
    for bulb in get_bulbs():
        bulb.set_rgb(r, g, b)


@tool
def set_lights_state(state: bool):
    """
    Set chamber's lights state
    :param state: (bool) lights boolean state: True for on or False for off
    """
    for bulb in get_bulbs():
        if state:
            bulb.turn_on()
        else:
            bulb.turn_off()
