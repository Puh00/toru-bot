import logging
import datetime
import aiohttp
from random import randint

from discord import Message, Embed
from discord.ext.commands.context import Context
from discord.ext import commands

_REACTION_EMOJIS = [
    "👍",
    "👎",
    "🤷",
]

_MULTI_REACTION_EMOJIS = [
    "0️⃣",
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🔟",
]


class Poll(commands.Cog):
    def __init__(self, client):
        self.client = client

    def createEmbed(self, ctx: Context, title: str, content: str = "") -> Embed:
        # random color
        color = int("%06x" % randint(0, 0xFFFFFF), 16)
        embed = Embed(
            title=title,
            description=content,
            color=color,
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(
            text=self.client.user.name, icon_url=self.client.user.avatar_url
        )
        return embed

    @commands.command()
    async def poll(self, ctx: Context, question: str, *options: list[str]):
        if len(options) > 11:
            await ctx.send("Too many options!")
            return
        if len(options) < 3:
            embed = self.createEmbed(ctx, question)
            message: Message = await ctx.send(embed=embed)
            for i in range(len(_REACTION_EMOJIS)):
                await message.add_reaction(_REACTION_EMOJIS[i])
        else:
            content = ""
            for i in range(len(options)):
                content += f"\n{_MULTI_REACTION_EMOJIS[i]} {''.join(options[i])}"

            embed = self.createEmbed(ctx, question, content)
            message: Message = await ctx.send(embed=embed)
            for i in range(len(options)):
                await message.add_reaction(_MULTI_REACTION_EMOJIS[i])

    @commands.command()
    async def strawpoll(self, ctx: Context, question: str, *options: list[str]):
        # Convert to list of strings
        options = list(map(lambda x: "".join(x), options))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://www.strawpoll.me/api/v2/polls",
                    json={"title": question, "options": options, "multi": "false"},
                    headers={"Content-Type": "application/json"},
                ) as response:
                    json = await response.json()
                    logging.info(f"Received strawpoll response: {json}")
                    if "errorCode" in json:
                        await ctx.send(json["errorMessage"])
                        return

                    strawpoll_id = json["id"]
                await ctx.send(f"https://strawpoll.me/{strawpoll_id}")
        except Exception as e:
            logging.error(f"Failed to create a strawpoll: {e}")
            return


def setup(client):
    client.add_cog(Poll(client))
