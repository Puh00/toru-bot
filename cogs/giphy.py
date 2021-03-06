import os
from dotenv import load_dotenv
import requests
import json

from discord.ext.commands.context import Context
from discord.ext import commands

load_dotenv()
_GIPHY_KEY = os.getenv("GIPHY_KEY")
_rating = "g"


class Giphy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def gif(self, ctx: Context, *, arg: str = ""):
        await ctx.send(self.get_gif(arg))

    @commands.command()
    async def cat(self, ctx: Context):
        await ctx.send(self.get_gif("cat"))

    def get_gif(self, tag: str = "") -> str:
        tag.replace(" ", "+")

        r = requests.get(
            "https://api.giphy.com/v1/gifs/random?api_key=%s&tag=%s&rating=%s"
            % (_GIPHY_KEY, tag, _rating)
        )

        if r.status_code == 200:
            cat_gif = json.loads(r.content)
            res = cat_gif["data"]["embed_url"]
            return res
        else:
            return "no gif for u"


def setup(client):
    client.add_cog(Giphy(client))
