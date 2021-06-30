from discord.ext import commands
from discord.ext import tasks

import re


class Channel(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 12)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, *, amount=None):
        if amount != None:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send(f"{amount!r} is not a valid value!")
                return

        confirmation = await ctx.send("React with anything to confirm the purge.")

        await self.purge_countdown.start(confirmation)

        new_msg = await ctx.fetch_message(confirmation.id)
        for reaction in new_msg.reactions:
            users = await reaction.users().flatten()
            # purges if the command caller confirmed it
            if ctx.message.author in users:
                await ctx.channel.purge(limit=amount)
                return

        # else just deletes the bot's message
        await new_msg.delete()

    @purge.error
    async def purge_error(self, ctx, error):
        message = ":x: "
        if isinstance(error, commands.MissingPermissions):
            message += "You don't have the permissions to purge!"
        elif isinstance(error, commands.CommandOnCooldown):
            message += "This command is on cooldown!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)

    @tasks.loop(seconds=1, count=10)
    async def purge_countdown(self, msg):
        if self.purge_countdown.current_loop == 0:
            original = msg.content
            # append the deletion notice
            await msg.edit(
                content=original + " `(This action will be executed in 10s)`",
            )

        else:
            seconds_left = int(10 - self.purge_countdown.current_loop)
            # always need some regex in a python project
            new_msg = re.sub(r"(\d|10)s\)`$", f"{seconds_left}s)`", msg.content)
            await msg.edit(content=new_msg)


def setup(client):
    client.add_cog(Channel(client))
