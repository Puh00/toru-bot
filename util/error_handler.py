"""Error Handler

!!WORK IN PROGRESS!!

This script provides useful decorators/methods for handling errors.
"""

import functools


def async_ignore_an_error(error_to_ignore: BaseException):
    """Decorator used to ignore a specific error for an async function
    
    Parameters
    ----------
    error_to_ignore : BaseException
        The type of the error to be ignored
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except error_to_ignore:
                pass

        return wrapper

    return decorator


def ignore_an_error(error_to_ignore: BaseException):
    """Decorator used to ignore a specific error for a blocking function
    
    Parameters
    ----------
    error_to_ignore : BaseException
        The type of the error to be ignored
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except error_to_ignore:
                pass

        return wrapper

    return decorator
