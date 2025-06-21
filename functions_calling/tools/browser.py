import config
from functions_calling.tool_decorator import tool
import subprocess

@tool(enabled=config.have_gui)
def open_browser_url(url: str) -> str:
    """
    Open an url on the user's browser.
    :param url: (str) The url to open.
    """
    subprocess.Popen(["firefox", "--new-tab", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return "browser url tab opened for: " + url

@tool(enabled=config.have_gui)
def open_browser_search(query: str) -> str:
    """
    Open a new search tab on the user's browser.
    :param query: (str) The search query.
    """
    open_browser_url("https://duckduckgo.com/?q=" + query)
    return "browser search tab opened for: " + query
