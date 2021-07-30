"""Hacky Methods

This script contains ehm... hacks that should normally not be used but
we use anyways because reasons.
"""


def stringify_residue_args(
    _locals: dict, args_name: str = "args", kwargs_name: str = "kwargs"
) -> str:
    """Stringify and concatenate all *args and **kwargs arguments

    Parameters
    ----------
    _locals : dict
        The dictionary obtained by calling locals() inside a function,
        the * and ** args should be named as *args and **kwargs for it
        to work properly.

        Note that whatever objects in the *args and **kwargs must be
        have implemented the __str__ methods.

    args_name : str, OPTIONAL
        Defaults to 'args', this needs to be assigned if your *args are
        called something else

    kwargs_name : str, OPTIONAL
        Defaults to 'kwargs', this needs to be assigned if your **kwargs
        are called something else

    Returns
    -------
    str
        A string containing all *args and **kwargs separared with a
        space
    """

    _args = list(_locals.get(args_name, ()))
    _kwargs = list(_locals.get(kwargs_name, {}).values())

    all_args = _args + _kwargs

    return " ".join(map(lambda i: str(i), all_args))
