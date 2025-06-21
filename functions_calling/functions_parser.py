import inspect
import json
import re

arg_types = {"int": "integer", "str": "string", "bool": "boolean"}


def parse_docstring(func):
    docstring = func.__doc__
    description = ""
    parameters = {}
    for line in docstring.strip().split('\n'):
        line = line.strip()
        if line:
            if line.startswith(':param'):
                arg_name, arg_type, arg_desc = re.search(":param (\w*): \((.*)\) (.*)", line).groups()

                enum = None
                if arg_type.startswith("Literal"):
                    enum = json.loads(arg_type.replace("Literal", ""))
                    arg_type = str(type(enum[0]).__name__)

                if arg_type in arg_types:
                    arg_type = arg_types[arg_type]

                parameters[arg_name] = {
                    "type": arg_type,
                    "description": arg_desc,
                }
                if enum is not None:
                    parameters[arg_name]["enum"] = enum
            else:
                description += line
    return description, parameters


def parse_function(func):
    description, parameters = parse_docstring(func)
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": inspect.getfullargspec(func).args
            }
        }
    }
