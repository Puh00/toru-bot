import os

from discord.ext.commands.context import Context
from dotenv import load_dotenv

import discord
from discord.ext import commands

import toru.magic8ball as m8b

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


client.load_extension("cogs.giphy")


@client.command(name="8ball")
async def ask8ball(ctx: Context, question):
    await ctx.send(m8b.ask(question))


client.run(os.getenv("DISCORD_TOKEN"))
