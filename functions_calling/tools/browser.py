import config
from functions_calling.tool_decorator import tool
import subprocess

@tool(enabled=config.have_gui)
def open_browser_url(url: str) -> str:
    """
    Open an url on the user's browser. (This tool is not returning anything, it just opens the url)
    :param url: (str) The url to open.
    """
    subprocess.Popen(["firefox", "--new-tab", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return "browser url tab opened for: " + url
