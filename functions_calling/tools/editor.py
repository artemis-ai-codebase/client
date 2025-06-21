import os
import subprocess

import config
from functions_calling.tool_decorator import tool


@tool(enabled=config.have_gui and os.path.exists(".editor"))
def open_in_editor(text: str, extension: str = "txt") -> str:
    """
    Instead, use that function to open a popup in the user computer containing the given text.
    Use that function for links, code, long text or things user might want to copy.
    If it was the only user instruction, please immediately end the conversation instead of saying anything.
    If the given file extension is a code file, the code keywords will be highlighted.
    :param text: (str) The text to display to user
    :param extension: (str) The file extension to use. Default is txt. (e.g., txt, py, cpp)
    """
    with open(".editor", "r") as f:
        editor_path = f.read().strip()

    file_path = "/tmp/artemis/text." + extension
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w+") as f:
        f.write(text)

    subprocess.Popen([editor_path, file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return "successfully opened"
