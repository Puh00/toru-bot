import functools


def async_ignore_an_error(error_to_ignore):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except error_to_ignore:
                pass

        return wrapper

    return decorator


def ignore_an_error(error_to_ignore):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except error_to_ignore:
                pass

        return wrapper

    return decorator
