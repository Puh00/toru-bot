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
db = client.db

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

    query = users.find_one({"user": user, "servers.server": server})

    # wtf
    return list(
        filter(lambda server: server.get("server") == server, query.get("servers"))
    )[0]


# inserts the user into database if the user does not exists,
# creates a server for the user if the user does not have the server,
# if chat_info is specified then also update the server info for the user
def update(user: int, server: int, details: Dict[str, int]):
    if not user_exists(user):
        user = {"user": user, "servers": []}

        users.insert_one(user)

    if not user_has_server(user, server):
        server = {"server": server, "chat_exp": 0, "level": 1}

        users.update_one({"user": user}, {"$push": {"servers": server}})

    if details is not None:
        details.setdefault("server", server)

        users.update_one(
            {"user": user, "servers.server": server},
            {"$set": {"servers.$": details}},
        )


def remove(user: int, server: int):
    users.update_one({"user": user}, {"$pull": {"servers": {"server": server}}})
