import re
import asyncio
import discord
from discord import Member, Guild
from discord.ext import commands, tasks
from discord.ext.commands import Context

from util.time_parser import TimeParser


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    ##### !ban/!kick #####

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason):
        if ctx.author == member:
            await ctx.send("You can't kick yourself!")
            return

        await member.kick(reason=reason)
        await ctx.send(
            f"{ctx.author.mention} has kicked {member.mention} out of the cool kids clan!"
        )

    @kick.error
    async def kick_error(self, ctx, error):
        message = ":x: "
        if isinstance(error, commands.MissingPermissions):
            message += "Your leg is not strong enough to kick!"
        elif isinstance(error, commands.MemberNotFound):
            message += "Can't kick someone not in the server!"
        elif isinstance(error, commands.CommandInvokeError):
            cause = error.__cause__
            if isinstance(cause, discord.Forbidden):
                message += "You cannot kick an admin!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason):
        if ctx.author == member:
            await ctx.send("You can't ban yourself!")
            return

        await member.ban(reason=reason)
        await ctx.send(f"{ctx.author.mention} just banned {member.mention}'s ass!")

    @ban.error
    async def ban_error(self, ctx, error):
        message = ":x: "
        if isinstance(error, commands.MissingPermissions):
            message += "You don't have the ban hammer!"
        elif isinstance(error, commands.MemberNotFound):
            message += "Can't ban someone not in the server!"
        elif isinstance(error, commands.CommandInvokeError):
            cause = error.__cause__
            if isinstance(cause, discord.Forbidden):
                message += "You cannot ban an admin!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user, *, reason):
        # bans() returns a list of BanEntry
        _bans = await ctx.guild.bans()
        # extract the users from all BanEntry
        banned_users = map(lambda be: be.user, _bans)

        # assuming user is the discord user tag, since you
        # have no way to mention a banned member
        name, discriminator = user.split("#")
        for _user in banned_users:
            if (name, discriminator) == (_user.name, _user.discriminator):
                await ctx.guild.unban(_user, reason=reason)
                await ctx.send(
                    f"{_user.mention} has now been released from the ban hammer jail by {ctx.author.mention}!"
                )
                return

        await ctx.send(f"{user.mention} is not found in the secret ban list!")

    @unban.error
    async def unban_error(self, ctx, error):
        message = ":x: "
        if isinstance(error, commands.MissingPermissions):
            message += "You don't have the power to lift the ban hammer!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)

    ##### !mute/!unmute #####

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: Member):
        muted = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted not in member.roles:
            await ctx.send(f"{member.display_name} is not muted!")
            return

        await member.remove_roles(muted)
        await ctx.send(f"{ctx.author.mention} has unmuted {member.mention}!")

    @unmute.error
    async def unmute_error(self, ctx, error):
        message = ":x: "
        if isinstance(error, commands.MemberNotFound):
            message += "That user is not a member!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        # whenever a channel has been created, override Muted roles
        # permissions to speak in the newly created channel
        muted = discord.utils.get(channel.guild.roles, name="Muted")
        if not muted:
            Admin.create_muted_role(channel.guild)
        else:
            await channel.set_permissions(
                muted, speak=False, send_messages=False, read_messages=True
            )

    async def create_muted_role(guild: Guild):
        muted = await guild.create_role(name="Muted")
        # for each channel in the server, mute the member in that channel
        for ch in guild.channels:
            await ch.set_permissions(
                muted, speak=False, send_messages=False, read_messages=True
            )

    @commands.command(
        name="mute",
        help="Mutes the given member given a time parameter, defaults to 5 minute if not given any",
    )
    @commands.has_permissions(manage_messages=True)
    async def mute(
        self,
        ctx: Context,
        member: Member,
        time: str = "5m",
        *,
        reason: str = None,
    ):
        try:
            # try to parse to see if the time is correctly formatted
            tp = TimeParser(time)
        except ValueError:
            # if not then we assume it's part of the reason, this is scuffed...
            tp = TimeParser("5m")

            if reason is None:
                reason = time
            else:
                reason = f"{time} {reason}"

        # look for the role named "Muted"
        muted = discord.utils.get(ctx.guild.roles, name="Muted")
        # create it if the "Muted" role does not exist
        if not muted:
            await Admin.create_muted_role(ctx.guild)

        # we don't mute the same poor guy twice
        if muted in member.roles:
            await ctx.send(f"{member.display_name} is already muted!")
            return

        mute_time = int(tp)

        # mute the member
        await member.add_roles(muted, reason=reason)

        await ctx.send(
            f"{member.mention} has been muted by {ctx.author.mention} for {str(tp)}!"
        )

        # simply sleeps this thread until the time is up
        await asyncio.sleep(mute_time)

        # retrieve the member again to update the cache
        member = await ctx.guild.fetch_member(member.id)

        # only send a notification if the user is in the server and
        # has the mute role
        if member and muted in member.roles:
            await member.remove_roles(muted)
            await ctx.send(
                f"{member.mention} has been successfully released from the mute jail! :tada:"
            )

    @mute.error
    async def mute_error(self, ctx, error):
        message = ":x: "
        if isinstance(error, commands.MemberNotFound):
            message += "That user is not a member!"
        elif isinstance(error, commands.ArgumentParsingError):
            message += "The given time is invalid!"

        else:
            message += f"Command failed to execute due to: ```\n{error}\n```"

        await ctx.send(message)

    ##### !purge #####

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
    client.add_cog(Admin(client))
