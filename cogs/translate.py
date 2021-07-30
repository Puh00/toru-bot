import logging
import aiohttp
import requests

from discord import Embed
from discord.ext.commands.context import Context
from discord.ext import commands

from util.ascii_table import generateTable


class Translate(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
      help="Display list of languages supported for translation"
    )
    async def languages(self, ctx: Context):
        r = requests.get(f"https://libretranslate.de/languages")
        languages = [["Name", "code"]]
        for lang in r.json():
            languages.append([lang["name"], lang["code"]])
        logging.info(generateTable(languages))
        await ctx.send(
            embed=Embed(title="Languages", description=f"```{generateTable(languages)}```")
        )

    @commands.command(
      help="Literal translation"
    )
    async def translate(self, ctx: Context, source: str, target: str, *text: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://libretranslate.de/translate",
                    json={"q": text, "source": source, "target": target},
                    headers={"Content-Type": "application/json"},
                ) as response:
                    json = await response.json()
                    logging.info(f"Received translation: {json}")
                    translatedText = " ".join(json['translatedText'])
                    await ctx.send(f"\"{translatedText}\"")
        except Exception as e:
            logging.error(f"Failed")
            return


def setup(client):
    client.add_cog(Translate(client))
