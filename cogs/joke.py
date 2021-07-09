import requests
import json
import re
import random

from discord.ext import commands

JOKE_API_DOMAIN = "https://v2.jokeapi.dev/joke"


class Joke(commands.Cog):
    def __init__(self, client):
        self.client = client
        # initialize the pattern so that we don't keep recompiling
        # the same regex over and over again
        self.dadpattern = re.compile(
            r"(?P<iam>i(?:'?m|\s*am))[\s]+(?P<what>[^\s.,;!?][^.,;!?]*[^\s.,;!?]?)",
            re.IGNORECASE,
        )

    @commands.command(name="joke", aliases=["randomjoke"])
    async def _joke(self, ctx):
        await ctx.send(self.format_joke(self.joke()))

    @commands.command(name="pun", aliases=["randompun"])
    async def _pun(self, ctx):
        await ctx.send(self.format_joke(self.joke(type="Pun")))

    @commands.command(name="darkjoke")
    async def dark_joke(self, ctx):
        await ctx.send(self.format_joke(self.joke(type="Dark")))

    @commands.command(name="nerdjoke", aliases=["programmerjoke", "programmingjoke"])
    async def nerd_joke(self, ctx):
        await ctx.send(self.format_joke(self.joke(type="Programming")))

    @commands.Cog.listener("on_message")
    async def dad_on_message(self, message):
        if message.author == self.client.user:
            return

        # looks for a message that look like this "i'm bla bla bla"
        mo = self.dadpattern.search(message.content)

        # ignore message if it does not meet the "dad criteria"
        if mo is None:
            return

        name = mo.group("what")
        if len(name) == 0:
            return

        greetings = ["Hi", "Hello", "What's up", "Good day", "How are you doing"]
        await message.channel.send(
            f"{random.choice(greetings)} **{name}**, I'm Toru-chan!"
        )

    # format the joke using discord markdown syntax
    def format_joke(self, joke):
        message = ""
        if self.is_twopart(joke):
            message = f"{joke['setup']}\n\n||{joke['delivery']}||"
        else:
            message = joke["joke"]

        return message

    # returns a random dict containing a joke
    def joke(self, type=None):
        endpoint = JOKE_API_DOMAIN
        if type is None:
            endpoint += "/Any"
        else:
            endpoint += f"/{type}"

        response = requests.get(endpoint)

        if response.status_code != 200:
            return {"joke": "I've failed to ~~copy ~~come up any good joke!"}

        return json.loads(response.text)

    def is_twopart(self, joke):
        # a twopart joke contains a setup and a delivery,
        # otherwise it just contains a joke
        return {"setup", "delivery"} <= set(joke.keys())


def setup(client):
    client.add_cog(Joke(client))
