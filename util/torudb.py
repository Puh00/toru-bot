import pymongo

""" 
the intended scheme for the collection 'users'
{
    "user": user_id
    "servers": [
        {
            "server": server_id1
            "chat_exp": 69
            "level": 2
        },
        {
            "server": server_id2
            "chat_exp": 420
            "level": 4
        }
    ]
}
"""

# TODO: error handling for those database calls and risky None values
class ToruDb:
    def __init__(self) -> None:
        # connect to the database
        self.client = pymongo.MongoClient("localhost", 27017)
        # the database object
        self.db = self.client.toru
        # the connection object
        self.users = self.db.users

        # create indices to speed up the queries
        self.users.create_index([("user", pymongo.ASCENDING)], unique=True)
        self.users.create_index([("servers.server", pymongo.ASCENDING)])

    def user_exists(self, user_id):
        return self.users.find_one({"user": user_id}) is not None

    def user_has_server(self, user_id, server_id):
        query = self.users.find_one({"user": user_id, "servers.server": server_id})
        return query is not None

    def get_chat_info(self, user_id, server_id):
        if not self.user_has_server(user_id, server_id):
            return None

        query = self.users.find_one({"user": user_id, "servers.server": server_id})

        # wtf
        return list(
            filter(
                lambda server: server.get("server") == server_id, query.get("servers")
            )
        )[0]

    # inserts the user into database if the user does not exists,
    # creates a server for the user if the user does not have the server,
    # if chat_info is specified then also update the server info for the user
    def update(self, user_id, server_id, chat_info=None):
        if not self.user_exists(user_id):
            user = {"user": user_id, "servers": []}

            self.users.insert_one(user)

        if not self.user_has_server(user_id, server_id):
            server = {"server": server_id, "chat_exp": 0, "level": 1}

            self.users.update_one({"user": user_id}, {"$push": {"servers": server}})

        if chat_info is not None:
            chat_info.setdefault("server", server_id)

            self.users.update_one(
                {"user": user_id, "servers.server": server_id},
                {"$set": {"servers.$": chat_info}},
            )

    # used for when the user leaves a server
    # why do we reset everything?
    # becuase fuck you that's why
    def remove(self, user_id, server_id):
        self.users.update_one(
            {"user": user_id}, {"$pull": {"servers": {"server": server_id}}}
        )
