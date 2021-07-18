"""Error Handler

!!WORK IN PROGRESS!!

This script provides useful decorators/methods for handling errors.
"""

import logging
import functools
from typing import Type


def async_ignore_an_error(error_to_ignore: Type[Exception]):
    """Decorator used to ignore a specific error for an async function

    Parameters
    ----------
    error_to_ignore : Type[Exception]
        The type of the error to be ignored
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except error_to_ignore:
                logging.info(f"Ignored an error: {error_to_ignore}")

        return wrapper

    return decorator


def ignore_an_error(error_to_ignore: Type[Exception]):
    """Decorator used to ignore a specific error for a blocking function

    Parameters
    ----------
    error_to_ignore : Type[Exception]
        The type of the error to be ignored
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except error_to_ignore:
                logging.info(f"Ignored an error: {error_to_ignore}")

        return wrapper

    return decorator


def async_ignore_multiple_errors(errors_to_ignore: list[Type[Exception]]):
    """Decorator used to ignore a list of errors for an async function

    Parameters
    ----------
    errors_to_ignore : list[Type[Exception]]
        The list of error types to ignore
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except tuple(errors_to_ignore) as e:
                logging.info(f"Ignored an error: {e}")

        return wrapper

    return decorator


def ignore_multiple_errors(errors_to_ignore: list[Type[Exception]]):
    """Decorator used to ignore a list of errors for a blocking function

    Parameters
    ----------
    errors_to_ignore : list[Type[Exception]]
        The list of error types to ignore
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except tuple(errors_to_ignore) as e:
                logging.info(f"Ignored an error: {e}")

        return wrapper

    return decorator
