#!/usr/bin/env python3
import requests
import json
import urllib.parse

from discord.ext.commands.context import Context
from discord.ext import commands

_8BALL_API_DOMAIN_ = "https://8ball.delegator.com"


class Magic8Ball(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="8ball")
    async def ask8ball(self, ctx: Context, question):
        await ctx.send(self.ask(question))

    # Given an str of a question, return an random answer
    def ask(self, question):
        question = urllib.parse.quote(question)
        response = requests.get(f"{_8BALL_API_DOMAIN_}/magic/JSON/{question}")

        if response.status_code != 200:
            return "Yeah, I don't know man"

        answer = json.loads(response.text)["magic"]["answer"]
        return answer


def setup(client):
    client.add_cog(Magic8Ball(client))
