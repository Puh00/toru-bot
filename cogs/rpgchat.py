import math
from util.torudb import ToruDb
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
        new_exp = RpgChat.expof(msg) + self.get_exp(user, server)
        new_level = RpgChat.calc_level(new_exp)
        new_info = {"chat_exp": new_exp, "level": new_level}

        self.db.update(user, server, new_info)

    def get_exp(self, user, server):
        chat_info = self.db.get_chat_info(user, server)

        if chat_info is None:
            return 0

        return chat_info.get("chat_exp", 0)

    def get_level(self, user, server):
        chat_info = self.db.get_chat_info(user, server)

        if chat_info is None:
            return 0

        return chat_info.get("level", 1)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.register(member.id, member.guild.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.client.get_context(message)
        if not ctx.valid:
            self.chat(message.author.id, message.guild.id, message.content)

    @commands.command()
    async def exp(self, ctx):
        await ctx.send(
            f"Your current exp is: {self.get_exp(ctx.author.id, ctx.guild.id)}"
        )

    @commands.command()
    async def level(self, ctx):
        await ctx.send(f"Your level is: {self.get_level(ctx.author.id, ctx.guild.id)}")

    def calc_level(exp):
        # yes, the exp required to level up is literally just x^2
        return math.ceil(math.sqrt(exp))

    def expof(msg):
        # let's say you can get at most 50 exp
        return min(len(msg), 50)


def setup(client):
    client.add_cog(RpgChat(client))
