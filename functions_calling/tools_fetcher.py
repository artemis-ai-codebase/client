import importlib.util
import os

from functions_calling.functions_parser import parse_function

directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
arg_types = {"int": "integer", "str": "string"}

tool_modules = []
tool_functions = {}
tools = []


def import_module_from_path(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fetch_modules():
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename != os.path.basename(__file__) and not filename.startswith("!"):
            filepath = os.path.join(directory, filename)
            module = import_module_from_path(filepath)
            tool_modules.append(module)


def fetch_tools():
    for module in tool_modules:
        for func_name in dir(module):
            func = getattr(module, func_name)
            if hasattr(func, "__tool__"):
                tool_functions[func_name] = func
                tools.append(parse_function(func))


fetch_modules()
fetch_tools()
