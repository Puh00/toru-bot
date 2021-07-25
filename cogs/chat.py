from util.toru_rpg import ToruRpg
from util.error_handler import async_ignore_multiple_errors

from discord import Member, Message
from discord.ext import commands
from discord.ext.commands import Context, errors

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class RpgChat(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.handler = ToruRpg()

    @commands.Cog.listener()
    @async_ignore_multiple_errors([ServerSelectionTimeoutError, ConnectionFailure])
    async def on_member_join(self, member: Member):
        self.handler.register(member.id, member.guild.id)

    @commands.Cog.listener()
    @async_ignore_multiple_errors([ServerSelectionTimeoutError, ConnectionFailure])
    async def on_member_remove(self, member: Member):
        self.handler.unregister(member.id, member.guild.id)

    @commands.Cog.listener()
    @async_ignore_multiple_errors([ServerSelectionTimeoutError, ConnectionFailure])
    async def on_message(self, message: Message):
        ctx = await self.client.get_context(message)
        # check if the message is a command
        if not ctx.valid:
            self.handler.add_exp(
                message.author.id, message.guild.id, len(message.content)
            )

    @commands.command()
    async def exp(self, ctx: Context, member: Member = None):
        if member is None:
            member = ctx.author

        exp = self.handler.get_exp(member.id, ctx.guild.id)
        await ctx.send(
            f"{member.mention} has: `{exp['current_exp']}/{exp['required_exp']}` xp"
        )

    @commands.command()
    async def level(self, ctx: Context, member: Member = None):
        if member is None:
            member = ctx.author

        level = self.handler.get_level(member.id, ctx.guild.id)
        await ctx.send(f"{member.mention}'s level is: `{level}`")

    @exp.error
    @level.error
    async def chat_error(self, ctx: Context, error):
        message = ":x: "
        if isinstance(error, errors.CommandInvokeError):
            cause = error.__cause__
            if isinstance(cause, (ServerSelectionTimeoutError, ConnectionFailure)):
                message += "The database is currently taking a nap, try again later!"
        elif isinstance(error, errors.MemberNotFound):
            message += "I've never seen that person in my life!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)


def setup(client):
    client.add_cog(RpgChat(client))
