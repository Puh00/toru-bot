import math
from torudb import ToruDb

from discord.ext import commands


class RpgChat(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.db = ToruDb()

    def register(self, user, server):
        self.db.update(user, server)

    def unregister(self, user, server):
        self.db.remove(user, server)

    def chat(self, user, server, msg):
        old_info = self.db.get_chat_info(user, server)

        new_exp = RpgChat.expof(msg) + old_info.get("chat_exp", 0)
        new_level = RpgChat.calc_level(new_exp)
        new_info = {"chat_exp": new_exp, "level": new_level}

        self.db.update(user, server, new_info)

    def calc_level(exp):
        # yes, the exp required to level up is literally just x^2
        return math.ceil(math.sqrt(exp))

    def expof(msg):
        # let's say you can get at most 50 exp
        return min(len(msg), 50)


def setup(client):
    client.add_cog(RpgChat(client))
