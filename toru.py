import os

from discord.ext.commands.context import Context
from dotenv import load_dotenv

import discord
from discord.ext import commands
import youtube_dl

from toru.giphy import get_gif, cat_gif

load_dotenv()

client = commands.Bot(command_prefix="!")

player = {}


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
async def gif(ctx: Context, arg: str = ""):
    await ctx.send(get_gif(arg))


@client.command()
async def cat(ctx: Context):
    await ctx.send(cat_gif())


@client.command()
async def join(ctx: Context):
    channel = ctx.author.voice.channel
    if not is_connected(ctx):
        await channel.connect()
    else:
        ctx.send("Already joined a channel la")


@client.command()
async def leave(ctx: Context):
    if is_connected(ctx):
        await ctx.voice_client.disconnect()
    else:
        ctx.send("Can't leave leave from null bruh")


@client.command()
async def play(ctx: Context, url):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not is_connected(ctx):
        await ctx.send("BAKA MITAI NEE~!")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("NOT PLAYING")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("ALREADY PLAYING")


# move to util class
# Checks if bot is connected to a voice channel in the given guild
def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()


client.run(os.getenv("DISCORD_TOKEN"))
