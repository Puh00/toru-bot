import asyncio
import discord
from discord.ext import commands
from discord.ext import tasks

import re


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    ##### !mute/!unmute #####

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
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

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, time: str = None, *, reason=None):
        # reason for now is shown only in the audit log
        if reason is None:
            reason = "No reason given"

        # look for the role named "Muted"
        muted = discord.utils.get(ctx.guild.roles, name="Muted")
        # create it if the "Muted" role does not exist
        if not muted:
            # create a new Permissions that can only read messages
            perms = discord.Permissions(read_messages=True)
            muted = await ctx.guild.create_role(name="Muted", permissions=perms)

        # we don't mute the same poor guy twice
        if muted in member.roles:
            await ctx.send(f"{member.display_name} is already muted!")
            return

        mute_time_sec = 0
        is_perm_mute = True

        # parse the time is it's specified
        if time is not None:
            # parses time into time in seconds
            try:
                time = Admin.parse_time(time)

                mute_time_sec = (
                    time["seconds"]
                    + time["minutes"] * 60
                    + time["hours"] * 3600
                    + time["days"] * 86400
                )

                if is_perm_mute := (mute_time_sec == 0):
                    raise ValueError
            except:
                raise commands.ArgumentParsingError

        # mute the member
        await member.add_roles(muted, reason=reason)

        if is_perm_mute:
            # the user is permanently fucked
            await ctx.send(
                f"{member.mention} has been permanently muted by {ctx.author.mention}!"
            )
        else:
            await ctx.send(
                f"{member.mention} has been temporarily muted by {ctx.author.mention} for {Admin.time_to_string(time)}!"
            )

            # this works suprisingly well
            await asyncio.sleep(mute_time_sec)

            # retrive the member again to update the cache
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

    def parse_time(time):
        """
        Returns a dict of given time string, in the following form
          {
              "seconds": 11,
              "minutes": 0,
              "hours": 0,
              "days": 1
          }

        Parameters:
        -----------
        time: str [Required]
            Defined as a combination of [number + unit] where the units are
            limited to s|m|h|d for second, minute, hour and day, the order
            of the units is irrelevant, but no units should appear more
            than once, if so, then only the last instance will be parsed
        """

        # make sure that the whole string is matched
        mo = re.fullmatch(
            r"""
            (?:
                (?P<seconds>(?:\d)*)s |
                (?P<minutes>(?:\d)*)m |
                (?P<hours>(?:\d)*)h   |
                (?P<days>(?:\d)*)d
            )+
            """,
            time,
            re.VERBOSE,
        )

        if not mo:
            raise ValueError("The given time is invalid!")
        else:
            # make sure all values are integers
            time_dict = {k: int(v) for (k, v) in mo.groupdict(default=0).items()}
            return time_dict

    def time_to_string(time):
        """
        Given a time dict, return a human readable version of the time

        Parameters:
        -----------
        time: dict [Required]
            The dict object obtained by parse a time string using parse_time
        """

        # adjust the time
        time["minutes"] += int(time["seconds"] / 60)
        time["seconds"] = time["seconds"] % 60

        time["hours"] += int(time["minutes"] / 60)
        time["minutes"] = time["minutes"] % 60

        time["days"] += int(time["hours"] / 24)
        time["hours"] = time["hours"] % 24

        readable_time = ""
        # could've used time.keys() but since a dict is unorded,
        # it must be hard-coded like this to enforce an ordering
        time_units = ["days", "hours", "minutes", "seconds"]
        for unit in time_units:
            if (count := time[unit]) > 0:
                readable_time += f"{count} {unit} "

        if len(readable_time) == 0:
            readable_time += "0 seconds"

        # a simple substitution that inserts an "and" if possible
        return re.sub(
            r"((?:\d)+ (?:[a-z]){4,}) ((?:\d)+ (?:[a-z]){4,})$",
            r"\1 and \2",
            readable_time.strip(),
        )

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
