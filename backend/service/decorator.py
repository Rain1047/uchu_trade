def add_docstring(docstring: str):
    def decorator(func):
        func.__doc__ = docstring
        return func

    return decorator


def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        env = kwargs.get('env', 'MARKET')
        if env not in instances:
            instances[env] = cls(*args, **kwargs)
        return instances[env]
    return get_instance