import math
import functools
from util.torudb import ToruDb
from discord.ext import commands


class RpgChat(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

        self.try_connect()

    def try_connect(self):
        # if the server is non-existent then we
        # just pretend everything is not working
        try:
            self.db = ToruDb()
            self.is_connected = True
        except:
            self.db = None
            self.is_connected = False

        return self.is_connected

    # decorator for handling an error, created for
    # those pesky listeners since i don't know if
    # there is a built-in error handling function
    def handle_error(func):
        @functools.wraps(func)
        async def inner(self, *args, **kwargs):
            # TODO: this just ignores the error for now, change later
            try:
                await func(self, *args, **kwargs)
            except:
                pass

        return inner

    def register(self, user, server):
        self.db.update(user, server)

    def unregister(self, user, server):
        self.db.remove(user, server)

    def chat(self, user, server, msg):
        new_exp = RpgChat.expof(msg) + self.get_exp(user, server)
        new_level = RpgChat.calc_level(new_exp)
        new_info = {"chat_exp": new_exp, "level": new_level}

        self.db.update(user, server, new_info)

    def get_chat_info(self, user, server):
        chat_info = self.db.get_chat_info(user, server)
        if chat_info is None:
            chat_info = {"chat_exp": 0, "level": 1}

        return chat_info

    def get_exp(self, user, server):
        return self.get_chat_info(user, server).get("chat_exp", 0)

    def get_level(self, user, server):
        return self.get_chat_info(user, server).get("level", 1)

    @commands.Cog.listener()
    @handle_error
    async def on_member_join(self, member):
        self.register(member.id, member.guild.id)

    @commands.Cog.listener()
    @handle_error
    async def on_member_remove(self, member):
        self.unregister(member.id, member.guild.id)

    @commands.Cog.listener()
    @handle_error
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

    @level.error
    @exp.error
    async def error_handler(self, ctx, error):
        # try to connect to the database, if success
        # then next command invoke will succeed
        self.try_connect()

        await ctx.send("Unable to connect to database, please try again later")

    def calc_level(exp):
        # yes, the exp required to level up is literally just x^2
        return math.ceil(math.sqrt(exp))

    def expof(msg):
        # let's say you can get at most 50 exp
        return min(len(msg), 50)


def setup(client):
    client.add_cog(RpgChat(client))
