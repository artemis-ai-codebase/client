from . import tool_functions

def execute_tool_call(name: str, args: dict = None):
    function = tool_functions[name]

    print(f"Calling {name} with arguments: {args}")

    result = function(**(args or {}))
    if not result:
        result = "Done."

    print("Result:", result)

    return str(result)
