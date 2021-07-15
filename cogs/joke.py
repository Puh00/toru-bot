import random

from requests.models import HTTPError
import util.joke_handler as jh

from discord.ext import commands


class Joke(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="joke", aliases=["randomjoke"])
    async def _joke(self, ctx):
        await ctx.send(self.get_joke())

    @commands.command(name="pun", aliases=["randompun"])
    async def _pun(self, ctx):
        await ctx.send(self.get_joke(type="Pun"))

    @commands.command(name="darkjoke")
    async def dark_joke(self, ctx):
        await ctx.send(self.get_joke(type="Dark"))

    @commands.command(name="nerdjoke", aliases=["programmerjoke", "programmingjoke"])
    async def nerd_joke(self, ctx):
        await ctx.send(self.get_joke(type="Programming"))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return

        if iam_dict := jh.search_for_iam(message.content):
            # a predefined set of greetings, probably should refactor it somehow
            greetings = ["Hi", "Hello", "What's up", "Good day", "How are you doing"]
            await message.channel.send(
                f"{random.choice(greetings)} **{iam_dict['name']}**, I'm Toru-chan!"
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
