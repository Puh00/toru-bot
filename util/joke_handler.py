"""Joke Handler

This script creates a simplified interface for the JokeAPI, see the
following link: https://v2.jokeapi.dev/.

On top of the basic CRUD operations, this script also contains some
other functionalities meant to annoy people with, such as:

    * A regex pattern that matches on lines similar to `im bla bla` so
      that you can annoy people with `Hi bla bla, I'm dad`.
    * A random greeting function to make your like with dad jokes even
      easier.
    * And more if I ever come up with them!
"""

import re
import json
import random
import requests
from typing import Dict, Union

# the endpoint of the API we are working with
JOKE_API_DOMAIN = "https://v2.jokeapi.dev/joke"

DAD_PATTERN = re.compile(
    r"""
        # create a named group that matches after im, i'm, i am or iam
        (?P<iam>i(?:'?m|\s*am)) 
        # create a named group that matchs until the character class [.,;!?],
        # will not match if there is only space characters inbetween
        [\s]+(?P<name>[^\s.,;!?][^.,;!?]*[^\s.,;!?]?)
    """,
    re.IGNORECASE | re.VERBOSE,
)

# a predefined set of greetings, this is really scuffed, but will do for now
GREETINGS = ["Hi", "Hello", "What's up", "Good day", "How are you doing"]


def joke(type: str = None):
    """Gets a random joke, depending on the given type

    Parameters
    ----------
    type : str, optional
        The type of the joke, it must be valid according to the JokeAPI
        specifications, if not provided it will any type

    Returns
    -------
    Dict[str, Union[str, bool]]
        A dict containing the joke with varying keys depending on if
        the joke is two part, see below

        Two part:
            {
                "setup": "the setup"
                "delivery": "the punchline"
                "twopart": True
            }

        One part:
            {
                "joke": "the joke"
                "twopart": False
            }

    Raises
    ------
    HTTPError
        If the HTTP request failed for whatever reason
    """
    endpoint = JOKE_API_DOMAIN
    if type is not None:
        endpoint += f"/{type}"
    else:
        endpoint += "/Any"

    response = requests.get(endpoint)
    # raise an requests.models.HTTPError if unsuccessful
    response.raise_for_status()

    # converts the JSON response into a dictionary
    joke = json.loads(response.text)
    if joke["type"] == "twopart":
        return {
            "setup": joke["setup"],
            "delivery": joke["delivery"],
            "twopart": True,
        }
    else:
        return {
            "joke": joke["joke"],
            "twopart": False,
        }


def is_two_part(joke: Dict[str, Union[str, bool]]):
    """Checks whether a joke is two part or not

    Parameters
    ----------
    joke : Dict[str, Union[str, bool]]
        The joke dictionary return by the joke() function

    Returns
    -------
    bool
        True if the joke is two part else False
    """
    return joke["twopart"]


def search_for_iam(line: str):
    """Searches through a string to check for occurence of the word `im`

    Parameters
    ----------
    line : str
        The string to search using the DAD_PATTERN

    Returns
    -------
    Dict[str, str]
        A dictionary with keys ["iam","name"] if the pattern matched,
        else None
    """
    if result := DAD_PATTERN.search(line):
        result = result.groupdict()

    return result


def random_greeting():
    """Returns a random greeting

    Returns
    -------
    str
        A random greeting such as `Hello`, `Hi` etc
    """
    return random.choice(GREETINGS)
