def tool(_func=None, enabled=True):
    def decorator(func):
        setattr(func, '__tool__', enabled)
        return func

    if _func is None:
        return decorator
    else:
        return decorator(_func)
