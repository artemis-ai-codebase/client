def tool(_func=None, enabled=True):
    def decorator(func):
        if enabled:
            setattr(func, '__tool__', True)
        return func

    if _func is None:
        return decorator
    else:
        return decorator(_func)
