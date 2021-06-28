import os

from discord.ext.commands.context import Context
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()

client = commands.Bot(command_prefix="!")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@client.event
async def on_message(message: discord.Message):
    print(f"message from {message.author}: {message.content}")

    if message.author == client.user:
        return
    if message.content.startswith("hello"):
        await message.channel.send("hello")

    await client.process_commands(message)


@client.command()
async def ping(ctx: Context):
    await ctx.send("pong!")


# Just load every file in cogs directory for the time being
for file in os.scandir("./cogs"):
    if file.name.endswith(".py") and file.name != "__init__.py":
        print(f"cogs.{file.name[:-3]}")
        client.load_extension(f"cogs.{file.name[:-3]}")


# move to util class
# Checks if bot is connected to a voice channel in the given guild
def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


client.run(os.getenv("DISCORD_TOKEN"))
