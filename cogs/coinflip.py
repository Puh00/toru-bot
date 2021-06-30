from random import randint

from discord.ext.commands.context import Context
from discord.ext import commands


class CoinFlip(commands.Cog):
    def __init__(self, client):
        self.client = client

    def flip(self):
        side = "tails" if randint(0, 1) == 0 else "heads"
        return f"I flipped a :coin: and it landed on __**{side}**__"

    @commands.command()
    async def coinflip(self, ctx: Context):
        await ctx.send(self.flip())


def setup(client):
    client.add_cog(CoinFlip(client))
