"""Toru Database

This script provides simple backend functions for Toru-chan's RPG chat
feature using MongoDB.

Currently the functionalities are limited, and only basic CRUD
operations for the users are provided.

Below shows an example of the schema for the only collection the
database utilises, for now:

    {
        "user": user_id
        "servers": [
            {
                "server": server_id1
                "current_exp": 69
                "required_exp": 420
                "level": 2
            },
            {
                "server": server_id2
                "current_exp": 0
                "required_exp": 1377
                "level": 4
            }
        ]
    }
"""

import os
import dotenv
import logging
import pymongo
from typing import Dict, Union
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

dotenv.load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")


# create a connection to the database
client = MongoClient(MONGODB_URL, 27017, serverSelectionTimeoutMS=1000)
logging.info(f"Server info: {client.server_info}")

# retrieve/create the database object
db = client.toru

# retrieve/create the primary collection object
users = db.users

# in case the server wasn't running, just ignore it
try:
    # create the indices to speed up the queries
    users.create_index([("user", pymongo.ASCENDING)], unique=True)
    users.create_index(
        [("user", pymongo.ASCENDING), ("servers.server", pymongo.ASCENDING)],
        unique=True,
    )
except ServerSelectionTimeoutError:
    pass


def user_exists(user: int) -> bool:
    """Checks if a given user exists in the database

    Parameters
    ----------
    user : int
        The unique user id

    Returns
    -------
    bool
        True if the user does exist, else False
    """
    return users.find_one({"user": user}) is not None


def user_has_server(user: int, server: int) -> bool:
    """Checks if a given user is registered on the given server

    Parameters
    ----------
    user : int
        The unique user id

    server : int
        The unique server id

    Returns
    -------
    bool
        If the user does not exist or is not registered on the given
        server then False, else True
    """
    return users.find_one({"user": user, "servers.server": server}) is not None


def get_detail(user: int, server: int) -> Union[dict[str, int], None]:
    """Retrieves the details the given user has on the given server

    Parameters
    ----------
    user : int
        The unique user id

    server : int
        The unique server id

    Returns
    -------
    Union[dict[str, int], None]
        A dictionary representing the detail if the user has the given
        server, else None
    """
    if not user_has_server(user, server):
        return None

    result = users.find_one({"user": user, "servers.server": server})

    for detail in result["servers"]:
        if detail["server"] == server:
            return detail

    return None


def register(user: int, server: int) -> bool:
    """Registers a given user on the given server

    Parameters
    ----------
    user : int
        The unique user id

    server : int
        The unique server id

    Returns
    -------
    bool
        True if successfully registers the user, else False when the
        user is already registered on the given server
    """
    if not user_has_server(user, server):
        users.find_one_and_update(
            {"user": user},
            {
                "$push": {
                    "servers": {
                        "server": server,
                        "current_exp": 0,
                        "required_exp": 100,
                        "level": 1,
                    }
                }
            },
            upsert=True,
        )
        return True

    return False


def unregister(user: int, server: int) -> bool:
    """Unregisters a given user on the given server

    Parameters
    ----------
    user : int
        The unique user id

    server : int
        The unique server id

    Returns
    -------
    bool
        True if sucessfully unregisters the user, else False when the
        user is not registered to begin with
    """
    return (
        users.update_one(
            {"user": user}, {"$pull": {"servers": {"server": server}}}
        ).modified_count
    ) > 0


def update(user: int, server: int, detail: Dict[str, int]) -> bool:
    """Updates the given user's detail in a server with the given
    details

    Parameters
    ----------
    user : int
        The unique user id

    server : int
        The unique server id

    detail : Dict[str, int]
        The detail to be updated to

    Returns
    -------
    bool
        True if update executed successfully, else False when the user
        does not have the server, validate_detail() returns False on
        the given detail or other unknown reasons
    """
    if not (user_has_server(user, server) and validate_detail(detail)):
        return False

    return (
        users.update_one(
            {"user": user, "servers.server": server},
            {"$set": {"servers.$": detail}},
            upsert=True,
        ).modified_count
    ) > 0


def validate_detail(detail: Dict[str, int]) -> bool:
    """Validates the given detail

    Parameters
    ----------
    detail : Dict[str, int]
        The detail to be validated

    Returns
    -------
    bool
        True if the detail follows the schema, else False
    """
    detail_keys = {"server", "current_exp", "required_exp", "level"}
    return detail_keys <= detail.keys()
