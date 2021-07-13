import os
import logging

from discord.ext.commands.context import Context
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# for futrue refactors, this function should have some parameter
def init_bot():
    listening = discord.Activity(
        type=discord.ActivityType.listening,
        name="soft loli breathing",
    )
    return commands.Bot(command_prefix="!", activity=listening)


client = init_bot()


@client.event
async def on_ready():
    logging.info(f"Successfully logged in as '{client.user}'")


@client.event
async def on_message(message: discord.Message):
    logging.info(
        f"'{message.author}' sent a message in #{message.channel.name}: '{message.content}'"
    )

    if message.author == client.user:
        return

    await client.process_commands(message)


@client.command()
async def ping(ctx: Context):
    await ctx.send("pong!")


# Just load every file in cogs directory for the time being
for file in os.scandir("./cogs"):
    if file.name.endswith(".py") and file.name != "__init__.py":
        logging.info(f"Loading cog module: cogs.{file.name[:-3]}")
        client.load_extension(f"cogs.{file.name[:-3]}")


client.run(os.getenv("DISCORD_TOKEN"))
