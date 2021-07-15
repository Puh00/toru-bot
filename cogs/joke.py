import random

from requests.models import HTTPError
import util.joke_handler as jh

from discord.ext import commands
from discord.ext.commands import Context


class Joke(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dad_active = False

    @commands.command(name="joke", aliases=["randomjoke"], help="Gets a random joke")
    async def _joke(self, ctx: Context):
        await ctx.send(self.get_joke())

    @commands.command(name="pun", aliases=["randompun"], help="Gets a random pun")
    async def _pun(self, ctx: Context):
        await ctx.send(self.get_joke(type="Pun"))

    @commands.command(
        name="darkjoke", help="Gets a random joke, but slightly more African"
    )
    async def dark_joke(self, ctx: Context):
        await ctx.send(self.get_joke(type="Dark"))

    @commands.command(
        name="nerdjoke",
        aliases=["programmerjoke", "programmingjoke"],
        help="Gets a random joke, but for programmers",
    )
    async def nerd_joke(self, ctx: Context):
        await ctx.send(self.get_joke(type="Programming"))

    @commands.command(
        name="dad",
        aliases=["hi_dad", "activate_dad"],
        help="Activates the dad functionality, now you will feel like at home",
    )
    async def _dad(self, ctx: Context):
        self.dad_active = True
        await ctx.send(f"{jh.random_greeting()} {ctx.author.mention}! Dad is here!")

    @commands.command(
        name="stop_dad",
        aliases=["stopdad, bye_dad", "no_dad"],
        help="Stops the dad functionality, dad will miss you",
    )
    async def stop_dad(self, ctx: Context):
        self.dad_active = False
        await ctx.send(f"Ok, I will not bother you anymore!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        # if the search found any matches and the dad function is activated
        if (iam_dict := jh.search_for_iam(message.content)) and self.dad_active:
            await message.channel.send(
                f"{jh.random_greeting()} **{iam_dict['name']}**, I'm Toru-chan!"
            )

    def get_joke(self, type: str = None):
        try:
            if type:
                joke = jh.joke(type=type)
            else:
                joke = jh.joke()

            if jh.is_two_part(joke):
                return f"{joke['setup']}\n\n||{joke['delivery']}||"
            else:
                return joke["joke"]
        except HTTPError:
            return "Sorry, too busy to come up any good jokes right now."


def setup(client):
    client.add_cog(Joke(client))
