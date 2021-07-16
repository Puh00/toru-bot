""" Toru Database
TODO: add proper module documentation

the intended scheme for the collection 'users'
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
from typing import Dict
from pymongo import MongoClient

dotenv.load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")


# create a connection to the database
client = MongoClient(MONGODB_URL, 27017)
logging.info(f"Server info: {client.server_info}")

# retrieve/create the database object
db = client.toru
# TODO: this is a temporary measure, remove it next time
db.drop_collection()

# retrieve/create the primary collection object
users = db.users

# create the indices to speed up the queries
users.create_index([("user", pymongo.ASCENDING)], unique=True)
users.create_index(
    [("user", pymongo.ASCENDING), ("servers.server", pymongo.ASCENDING)], unique=True
)


def user_exists(user: int):
    return users.find_one({"user": user}) is not None


def user_has_server(user: int, server: int):
    return users.find_one({"user": user, "servers.server": server}) is not None


def get_details(user: int, server: int):
    if not user_has_server(user, server):
        return None

    result = users.find_one({"user": user, "servers.server": server})

    for detail in result["servers"]:
        if detail["server"] == server:
            return detail
        
    return None


def register(user: int, server: int):
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


def unregister(user: int, server: int):
    return (
        users.update_one(
            {"user": user}, {"$pull": {"servers": {"server": server}}}
        ).modified_count
    ) > 0


def update(user: int, server: int, detail: Dict[str, int]):
    if not (user_has_server(user, server) and validate_detail(detail)):
        return False

    return (
        users.update_one(
            {"user": user, "servers.server": server},
            {"$set": {"servers.$": detail}},
            upsert=True,
        ).modified_count
    ) > 0


def validate_detail(detail: Dict[str, int]):
    detail_keys = {"server", "current_exp", "required_exp", "level"}
    return detail_keys <= detail.keys()
