from discord.ext.commands.context import Context
from discord.ext import commands


class Channel(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def purge(self, ctx, amount=None):
        if amount != None:
            try:
                amount = int(amount)
            except:
                await ctx.send("The amount is not an integer!")
                return

        await ctx.channel.purge(limit=amount)


def setup(client):
    client.add_cog(Channel(client))
