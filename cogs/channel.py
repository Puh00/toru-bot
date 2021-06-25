from discord.ext.commands.context import Context
from discord.ext import commands


class Channel(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, amount=None):
        if amount != None:
            amount = int(amount)

        await ctx.channel.purge(limit=amount)

    @purge.error
    async def purge_error(self, ctx, error):
        message = ":x: "
        print(type(error))
        if isinstance(error, commands.CommandInvokeError):
            cause = error.__cause__
            if isinstance(cause, ValueError):
                # since for whatever reason they don't just provide you
                # with the goddamn argument you kinda have to do this
                prefix = ctx.prefix + ctx.command.name
                arg = ctx.message.content[len(prefix) + 1 :]
                message += f"{arg!r} is not a valid value!"
            else:
                message += f"Command failed to invoke due to: `{cause}`"
        elif isinstance(error, commands.MissingPermissions):
            message += "You don't have the permissions to purge!"

        await ctx.send(message)


def setup(client):
    client.add_cog(Channel(client))
