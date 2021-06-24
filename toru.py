import os

from discord.ext.commands.context import Context
from dotenv import load_dotenv

import discord
from discord.ext import commands

from toru.giphy import get_gif, cat_gif

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


@client.command()
async def gif(ctx: Context, *, arg: str = ""):
    await ctx.send(get_gif(arg))


@client.command()
async def cat(ctx: Context):
    await ctx.send(cat_gif())


# move to util class
# Checks if bot is connected to a voice channel in the given guild
def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


client.run(os.getenv("DISCORD_TOKEN"))
