def add_docstring(docstring: str):
    def decorator(func):
        func.__doc__ = docstring
        return func

    return decorator


def singleton(cls):
    _instances = {}

    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]

    return get_instance
