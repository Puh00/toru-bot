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


def user_exists(user_id):
    return users.find_one({"user": user_id}) is not None


def user_has_server(user_id, server_id):
    return users.find_one({"user": user_id, "servers.server": server_id}) is not None


def get_chat_info(user_id, server_id):
    if not user_has_server(user_id, server_id):
        return None

    query = users.find_one({"user": user_id, "servers.server": server_id})

    # wtf
    return list(
        filter(lambda server: server.get("server") == server_id, query.get("servers"))
    )[0]


# inserts the user into database if the user does not exists,
# creates a server for the user if the user does not have the server,
# if chat_info is specified then also update the server info for the user
def update(user_id, server_id, chat_info=None):
    if not user_exists(user_id):
        user = {"user": user_id, "servers": []}

        users.insert_one(user)

    if not user_has_server(user_id, server_id):
        server = {"server": server_id, "chat_exp": 0, "level": 1}

        users.update_one({"user": user_id}, {"$push": {"servers": server}})

    if chat_info is not None:
        chat_info.setdefault("server", server_id)

        users.update_one(
            {"user": user_id, "servers.server": server_id},
            {"$set": {"servers.$": chat_info}},
        )


def remove(user_id, server_id):
    users.update_one({"user": user_id}, {"$pull": {"servers": {"server": server_id}}})
