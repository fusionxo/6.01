import discord
import asyncio
from discord.ext import commands
import datetime
import aiohttp
from io import BytesIO
import discord
import time
from discord import User, errors
import re
import typing
import typing as t
from discord.ext.commands import has_permissions, MissingPermissions, has_role, has_any_role
import asyncio
from datetime import datetime
from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands
from utils.Tools import *
from core import Cog, Luka, Context
import json
from typing import Optional
from datetime import timedelta
from utils.checks import global_check

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = []
        with open("jsons/moderation.json", "r") as f:
            self.moderation_data = json.load(f)
            
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
            
    def help_custom(self):
		      emoji = '<:usershield:1087776624486920294>'
		      label = "Moderation"
		      description = "Shows the moderation commands."
		      return emoji, label, description

    @commands.group()
    async def __Moderation__(self, ctx: commands.Context):
        """`menable`, `mdisable`, `softban` , `purge` , `purge contains` , `purge startswith` , `purge invites` , `purge user` , `mute` , `unmute` , `kick` , `roleallhumans` , `roleallbots` , `removeallhumans` , `removeallbots` , `warn` , `ban` , `unban` , `clone` , `nick` , `slowmode` ,  `unslowmode` , `clear` , `clear all` , `clear bots` , `clear embeds` , `clear files` , `clear mentions` , `clear images` , `clear contains` , `clear reactions` , `nuke` , `lock` , `unlock`, `hide`, `unhide`, `lockall`, `unlockall`, `hideall`, `unhideall`"""
        
    def convert(self, time):
        pos = ["s","m","h","d"]
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}
        unit = time[-1]
        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2
        return val * time_dict[unit]        
        

    @staticmethod
    def is_moderation_enabled(ctx):
        moderation_data = ctx.bot.get_cog("Moderation").moderation_data
        guild_id = str(ctx.guild.id)
        return guild_id in moderation_data and moderation_data[guild_id]

    @commands.command(help="Enable moderation for this server", aliases=["moderation enable","menable"])
    @commands.guild_only()
    async def moderation_enable(self, ctx):
        if ctx.guild.owner_id == ctx.author.id:
            self.moderation_data[str(ctx.guild.id)] = True
            with open("jsons/moderation.json", "w") as f:
                json.dump(self.moderation_data, f)
            await ctx.send("Moderation has been enabled for this server.")
        else:
            await ctx.send("<:info:1087776877898383400> | Only the Server Owner can use this command.")

    @commands.command(help="Disable moderation for this server", aliases=["moderation disable","mdisable"])
    @commands.guild_only()
    async def moderation_disable(self, ctx):
        if ctx.guild.owner_id == ctx.author.id:
            self.moderation_data[str(ctx.guild.id)] = False
            with open("jsons/moderation.json", "w") as f:
                json.dump(self.moderation_data, f)
            await ctx.send("Moderation has been disabled for this server.")
        else:
            await ctx.send("<:info:1087776877898383400> | Only the Server Owner can use this command.")

    async def cog_check(cls, ctx: commands.Context) -> bool:
        if not isinstance(ctx.guild, discord.Guild):
            return False
        
        # Ignore moderation status for moderation_enable and moderation_disable commands
        if ctx.command.name in ["moderation_enable", "moderation_disable"]:
            return True

        if not cls.is_moderation_enabled(ctx):
            embed = discord.Embed(
                title="Moderation is currently disabled for this server.",
                color=0x977FD7
            )
            embed.add_field(name="Enable Moderation", value="To enable it kindly type `$menable`")
            await ctx.send(embed=embed)
            return False


        return True


    # ...

    @commands.hybrid_command(name="prefix", aliases=["setprefix","prefixset"], help="Allows you to change prefix of the bot for this server")
    
    
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _prefix(self, ctx: commands.Context, prefix):
        data = getConfig(ctx.guild.id)
        data["prefix"] = str(prefix)  
        updateConfig(ctx.guild.id, data)
        await ctx.reply(embed=discord.Embed(description=f"<:check:1087776909246607360> | Successfully Changed Prefix For **{ctx.guild.name}**\nNew Prefix for **{ctx.guild.name}** is : `{prefix}`\nUse `{prefix}help` For More info .", color=0x977FD7))



    @commands.command(aliases=['sb'], help="Literally trolling command or you can use to clear all messages by the user.", usage="softban <member>")
    
    
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def softban(self, ctx, member: discord.Member, *, reason=None):
        """Soft bans a member from the server."""
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        
        if reason is None:
            reason = f"No reason given.\nBanned by {ctx.author}"

        if member.id == self.bot.user.id:
            await ctx.send('Oh, you think you can softban me? Nice try! But I’m already here, and I’m not going anywhere.')
            return

        if member.id == ctx.author.id:
            await ctx.send('Softbanning yourself? That’s some serious commitment to self-discipline!')
            return

        if member.id == ctx.guild.owner_id:
            await ctx.send("Softbanning the server owner? That’s bold! And probably ineffective.")
            return

        await member.ban(reason=reason)
        await member.unban(reason=reason)
        hacker = discord.Embed(color=0x977FD7, description=f"<:check:1087776909246607360> | Successfully soft-banned {member}.", timestamp=ctx.message.created_at)
        hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker)


    @commands.group(invoke_without_command=True, help="Clears the messages", usage="purge <amount>")
    
    
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        if amount > 1000:
            return await ctx.send("Purge limit exceeded. Please provide an integer which is less than or equal to 1000.")
        deleted = await ctx.channel.purge(limit=amount + 1)
        return await ctx.send(f"**<:check:1087776909246607360> Deleted {len(deleted)-1} message(s)**")

    @purge.command(help="Clears the messages starts with the given letters", usage="purge startswith <text>")
    
    
    @commands.has_guild_permissions(manage_messages=True)
    async def startswith(self, ctx, key, amount: int = 10):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        if amount > 1000:
            return await ctx.send("Purge limit exceeded. Please provide an integer which is less than or equal to 1000.")
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.content.startswith(key):
                counter += 1
                return True
            else:
                return False

        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"**<:check:1087776909246607360> Deleted {len(deleted)}/{amount} message(s) which started with the given keyword**")

    @purge.command(help="Clears the messages ends with the given letter",usage="purge endswith <text>")
    
    
    @commands.has_guild_permissions(manage_messages=True)
    async def endswith(self, ctx, key, amount: int = 10):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")        
        if amount >1000:
            return await ctx.send("Purge limit exceeded. Please provide an integer which is less than or equal to 1000.")
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.content.endswith(key):
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"**<:check:1087776909246607360> Deleted {len(deleted)}/{amount} message(s) which ended with the given keyword**")

    @purge.command(help="Clears the messages contains with the given argument",usage="purge contains <message>")
    
    
    @commands.has_guild_permissions(manage_messages=True)
    async def contains(self, ctx, key, amount: int = 10):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        if amount >1000:
            return await ctx.send("Purge limit exceeded. Please provide an integer which is less than or equal to 1000.")
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if key in m.content:
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"**<:check:1087776909246607360> Deleted {len(deleted)}/{amount} message(s) which contained the given keyword**")

    @purge.command(help="Clears the messages of the given user",usage="purge <user>")
    
    
    @commands.has_guild_permissions(manage_messages=True)
    async def user(self, ctx, user: discord.Member, amount: int = 10):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        if amount >1000:
            return await ctx.send("Purge limit exceeded. Please provide an integer which is less than or equal to 1000.")
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if m.author.id == user.id:
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"**<:check:1087776909246607360> Deleted {len(deleted)}/{amount} message(s) which were sent by the mentioned user**")

    @purge.command(help="Clears the messages containing invite links",usage="purge invites")
    
    
    @commands.has_guild_permissions(manage_messages=True)
    async def invites(self, ctx, amount: int = 10):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        if amount >1000:
            return await ctx.send("Purge limit exceeded. Please provide an integer which is less than or equal to 1000.")
        global counter
        counter = 0

        def check(m):
            global counter
            if counter >= amount:
                return False

            if "discord.gg/" in m.content.lower():
                counter += 1
                return True
            else:
                return False
        deleted = await ctx.channel.purge(limit=100, check=check)
        return await ctx.send(f"**<:check:1087776909246607360> Deleted {len(deleted)}/{amount} message(s) which contained invites**")


      
    @commands.command(name="timeout", help="Mutes a specific member", aliases=["mute", "stfu"])
    @commands.cooldown(1, 20, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _mute(self, ctx, member: discord.Member, duration):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        ok = duration[:-1]
        tame = self.convert(duration)
        till = duration[-1]
        if tame == -1:
            await ctx.reply(f"You didnt give time with the correct unit\nExamples:\n{ctx.prefix}mute {ctx.author} 10m\n{ctx.prefix}mute {ctx.author} 5h", mention_author=False)
        elif tame == -2:
            await ctx.reply(f"Time must be an integer!", mention_author=False)
        else:
            if till.lower() == "d":
                t = timedelta(seconds=tame)
                msg = "<:check:1087776909246607360> | Successfully Muted {0.mention} For {1} Day(s)".format(member, ok)
            elif till.lower() == "m":
                t = timedelta(seconds=tame)
                msg = "<:check:1087776909246607360> | Successfully Muted {0.mention} For {1} Minute(s)".format(member, ok)
            elif till.lower() == "s":
                t = timedelta(seconds=tame)
                msg = "<:check:1087776909246607360> | Successfully Muted {0.mention} For {1} Second(s)".format(member, ok)
            elif till.lower() == "h":
                t = timedelta(seconds=tame)
                msg = "<:check:1087776909246607360> | Successfully Muted {0.mention} For {1} Hour(s)".format(member, ok)

            try:
                if member.guild_permissions.administrator:
                    await ctx.reply("<:error:1088542929158688788> | I can't mute administrators")
                else:
                    await member.timeout(discord.utils.utcnow() + t, reason="Command By: {0}".format(ctx.author))
                    await ctx.send(msg)
            except:
                await ctx.send("<:info:1087776877898383400> | An error occurred")

    @commands.command(name="untimeout", aliases=["unmute", "unshut"], help="Unmutes a member")
    @commands.cooldown(1, 20, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _unmute(self, ctx, member: discord.Member):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        if member.is_timed_out():
            try:
                await member.edit(timed_out_until=None)
            except Exception as e:
                await ctx.send("Unable to Remove Timeout:\n```py\n{}```".format(e))
            else:
                await ctx.send("<:check:1087776909246607360> | Successfully Unmuted {}".format(member.mention))



    @commands.command(aliases=['k'], help="Someone is disregarding the rules - take swift action and kick them from the server as a consequence.", usage="kick <member>")
    
    
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        if member.id == self.bot.user.id:
            await ctx.send(f"Seriously? Trying to kick me? Nice try, but I’m unkickable!")
            return

        if member.id == ctx.author.id:
            await ctx.send('Kicking yourself? That’s a bold move! And also a bit confusing.')
            return

        if member.id == ctx.guild.owner_id:
            await ctx.send("Kicking the server owner? That’s a tall order. Good luck with that!")
            return

        if ctx.author.top_role.position > member.top_role.position or ctx.author.id == ctx.guild.owner.id:
            await member.kick(reason=reason)
            hacker = discord.Embed(color=0x977FD7, description=f"<:check:1087776909246607360> | {member.display_name} has been kicked from this guild, for: {reason}", timestamp=ctx.message.created_at)
            hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=hacker)
            hacker1 = discord.Embed(color=0x977FD7, description=f":exclamation: | You’ve been kicked from {ctx.guild.name} for: {reason}!", timestamp=ctx.message.created_at)
            await member.send(embed=hacker1)
        else:
            await ctx.send("*<a:error:1002226340516331571> | You can’t kick someone with a higher role than you.*")


  
    @commands.command(aliases=['w'],help="To warn a specific user.",usage="warn <member>")
    
    
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, * , reason="No Reason Provided!"):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        hacker = discord.Embed(color=0x977FD7,description=f"<:check:1087776909246607360> | {member.display_name} has been warned for: {reason}", timestamp=ctx.message.created_at)
        hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker)
        hacker1 = discord.Embed(color=0x886ad1,description=f":exclamation: | You have been warned in {ctx.guild.name} for: {reason}", timestamp=ctx.message.created_at)
        await member.send(embed=hacker1)


    @commands.command(name='ban', help="Ban a user from the server, either by mentioning them or by providing their user ID.", usage="ban [member or user_id] [reason]")
    
    
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member_or_id: str, *, reason=None):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        member = None
        user_id = None

        mention_match = re.match(r'<@!?(\d+)>', member_or_id)
        if mention_match:
            user_id = int(mention_match.group(1))
        elif member_or_id.isdigit():
            user_id = int(member_or_id)
        
        if user_id is not None:
            member = ctx.guild.get_member(user_id)
            if member is None:
                try:
                    user = await self.bot.fetch_user(user_id)
                    await ctx.guild.ban(user, reason=reason, delete_message_days=7)
                    
                    embed = discord.Embed(
                        color=0x977FD7,
                        description=f"<:check:1087776909246607360> | User with ID {user_id} has been successfully banned",
                        timestamp=ctx.message.created_at
                    )
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")
                    await ctx.send(embed=embed)
                    return
                except discord.NotFound:
                    return await ctx.reply("User not found.")
                except discord.Forbidden:
                    return await ctx.reply("I don't have permission to ban this user.")
                except discord.HTTPException:
                    return await ctx.reply("An error occurred while trying to ban the user.")
        else:
            member = ctx.guild.get_member_named(member_or_id)

        if member is None:
            return await ctx.reply("Member not found in this guild.")
        
        if member.id == self.bot.user.id:
            await ctx.send('Nice try, but you can’t ban the bot. I’m unbannable!')
            return

        if member.id == ctx.author.id:
            await ctx.send('Banning yourself? That’s a bold move!')
            return

        if member.id == ctx.guild.owner_id:
            await ctx.send("Banning the server owner? Nice try, but that's not happening!")
            return

        if ctx.author.top_role.position > member.top_role.position or ctx.author.id == ctx.guild.owner.id:
            try:
                await member.ban(reason=reason, delete_message_days=7)
                embed = discord.Embed(
                    color=0x977FD7,
                    description=f"<:check:1087776909246607360> | {member.display_name} has been successfully banned",
                    timestamp=ctx.message.created_at
                )
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar.url}")
                await ctx.send(embed=embed)

                ban_dm = discord.Embed(
                    color=0x977FD7,
                    description=f":exclamation: | You have been banned from {ctx.guild.name} for reason: {reason}",
                    timestamp=ctx.message.created_at
                )
                try:
                    await member.send(embed=ban_dm)
                except discord.Forbidden:
                    pass

            except discord.Forbidden:
                await ctx.send("I don't have permission to ban this member.")
            except discord.HTTPException:
                await ctx.send("An error occurred while trying to ban the member.")
        else:
            embed = discord.Embed(
                color=0x977FD7,
                description="*<a:error:1002226340516331571> | You cannot ban someone with a higher role than you.*",
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)


    
    @commands.command(help="If someone realizes his mistake you should unban him",usage="unban [user]")
    
    
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, id: int):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)
        hacker = discord.Embed(color=0x977FD7,description=f"<:check:1087776909246607360> | {user.name} has been successfully unbanned", timestamp=ctx.message.created_at)
        hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker)

    @commands.command(help="Clones a channel .")
    
    
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx, channel: discord.TextChannel):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        await channel.clone()
        hacker = discord.Embed(color=0x977FD7,description=f"<:check:1087776909246607360> | {channel.name} has been successfully cloned", timestamp=ctx.message.created_at)
        hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker)



        
                          
    @commands.command(aliases=['nick'],help="To change someone's nickname.",usage="nick [member]")
    
    
    @commands.has_permissions(manage_nicknames=True)
    async def changenickname(self, ctx, member: discord.Member, * , nick):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        await member.edit(nick=nick)
        hacker = discord.Embed(color=0x977FD7,description=f"<:check:1087776909246607360> | Successfully changed nickname of {member.name}", timestamp=ctx.message.created_at)
        hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=hacker)


  
    @commands.group(aliases=["c"],invoke_without_command=True,help="Clears the messages")
    
    
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    
    async def clear(self, ctx):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        embed = discord.Embed(color=0x977FD7)
        embed.add_field(name="**Clear <cmd>**", value="**\n<:arrow:1060839014724280320> Clear all\n<:arrow:1060839014724280320> Clear bots\n<:arrow:1060839014724280320> Clear embeds\n<:arrow:1060839014724280320> Clear files\n<:arrow:1060839014724280320> Clear mentions\n<:arrow:1060839014724280320> Clear images \n<:arrow:1060839014724280320> Clear contains\n<:arrow:1060839014724280320> Clear reactions**")
        await ctx.reply(embed=embed, mention_author=False)
    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 1000:
            em = discord.Embed(description=f" Too many messages to search given ({limit}/2000)", color=0x977FD7)
            return await ctx.send(embed=em)

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.HTTPException as e:
            em = discord.Embed(description=f" Try a smaller search?", color=0x977FD7)
            return await ctx.send(embed=em)

        deleted = len(deleted)
        if message is True:
            await ctx.message.delete()
            await ctx.send(embed= discord.Embed(description=f" Successfully removed {deleted} message{'' if deleted == 1 else 's'}.", color=0x977FD7, delete_after=3))

    @clear.command(aliases=["e"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    async def embeds(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @clear.command(aliases=["f"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    async def files(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @clear.command(aliases=["m"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    async def mentions(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes messages that have mentions in them."""
        await self.do_removal(ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @clear.command(aliases=["i"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    
    async def images(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @clear.command(name="all")
    
        
    
    async def _remove_all(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @clear.command(aliases=["co"])
    
    
    @commands.has_permissions(manage_messages=True)  
    
    async def contains(self, ctx, *, substr: str):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 1000, lambda e: substr in e.content)

    @clear.command(name="bots", aliases=["b"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    
    async def _bots(self, ctx, search=100, prefix=None):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = [";", "$", "!", "-", "?", ">", "^", "$", "w!", ".", ",", "a?", "g!", "m!", "s?"]

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @clear.command(name="emojis", aliases=["em"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    
    async def _emojis(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)
        
    @clear.command(name="reactions", aliases=["r"])
    
    
    @commands.has_permissions(manage_messages=True)
    
    
    async def _reactions(self, ctx, search=1000):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()
        await ctx.message.delete()
        await ctx.send(embed=discord.Embed(description=f"<:check:1087776909246607360> | Successfully Removed {total_reactions}.", color=0x977FD7))


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    
    
    async def nuke(self, ctx, channels: discord.TextChannel = None):
        channels = channels or ctx.channel

        await ctx.send('<:info:1087776877898383400> | Are you sure you want to nuke {}!\nType in `yes`. To proceed'.format(channels.mention))

        def check(m):
            user = ctx.author
            return m.author.id == user.id and m.content.lower() == 'yes'

        position = channels.position

        await self.bot.wait_for('message', check=check)
        await ctx.channel.send('Theres no going back!\n**Are you sure.**')
        await self.bot.wait_for('message', check=check)
        try:
            new = await channels.clone()
            await channels.delete()
            await new.edit(positon=position)
        except discord.errors.Forbidden:
            return await ctx.send('**<:info:1087776877898383400> | Nuke Failed. I am missing permissions!**')

     #   await new.send('https://media1.tenor.com/images/6c485efad8b910e5289fc7968ea1d22f/tenor.gif?itemid=5791468')
        await asyncio.sleep(2)
        await new.send(f" ``nuked by`` {ctx.author.mention}")



    @commands.command(help="Locks down a channel", usage="lock <channel> <reason>", aliases=["lockdown"])
    
    
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        if channel is None: channel = ctx.channel
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=False),
                reason=reason)
            await ctx.send(embed=discord.Embed(
                title="Luka | Lockdown",
                description="<:check:1087776909246607360> | Successfully locked **%s**" % (channel.mention),
                color=0x977FD7))
        except:
            await ctx.send(
                embed=discord.Embed(title="Luka | Lockdown",
                                    description="Failed to lockdown **%s**" %
                                    (channel.mention),
                                    color=0x977FD7))
        else:
            pass

    @commands.command(help="Unlocks a channel", usage="unlock <channel> <reason>", aliases=["unlockdown"])
    
    
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        if channel is None: channel = ctx.channel
        try:
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=discord.PermissionOverwrite(send_messages=True),
                reason=reason)
            await ctx.send(embed=discord.Embed(
                title="Luka | Unlockdown",
                description="<:check:1087776909246607360> | Successfully unlocked **%s**" %
                (channel.mention),
                color=0x977FD7))
        except:
            await ctx.send(
                embed=discord.Embed(title="Luka | Unlockdown",
                                    description="Failed to lock **`%s`**" %
                                    (channel.mention),
                                    color=0x977FD7))
        else:
            pass


    @commands.command(name='lockall')
    @commands.has_permissions(manage_channels=True)
    async def lock_all(self, ctx):
        """Locks all channels in the server."""
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            embed = discord.Embed(title='Lock All Channels', description='All channels have been locked.', color=0x977FD7)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Error', description='<:error:1088542929158688788> | Failed to lock all channels.', color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name='hideall')
    @commands.has_permissions(manage_channels=True)
    async def hide_all(self, ctx):
        """Hides all channels in the server."""
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, read_messages=False)
            embed = discord.Embed(title='Hide All Channels', description='<:check:1087776909246607360> | All channels have been hidden.', color=0x977FD7)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Error', description='<:error:1088542929158688788> | Failed to hide all channels.', color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name='unlockall')
    @commands.has_permissions(manage_channels=True)
    async def unlock_all(self, ctx):
        """Unlocks all channels in the server."""
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
    
        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, send_messages=None)
            embed = discord.Embed(title='Unlock All Channels', description='<:check:1087776909246607360> | All channels have been unlocked.', color=0x977FD7)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Error', description='<:error:1088542929158688788> | Failed to unlock all channels.', color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name='unhideall')
    @commands.has_permissions(manage_channels=True)
    async def unhide_all(self, ctx):
        """Unhides all channels in the server."""
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(ctx.guild.default_role, read_messages=None)
            embed = discord.Embed(title='Unhide All Channels', description='<:check:1087776909246607360> | All channels have been unhidden.', color=0x977FD7)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title='Error', description='<:error:1088542929158688788> | Failed to unhide all channels.', color=discord.Color.red())
            await ctx.send(embed=embed)

    @commands.command(name='hide')
    @commands.has_permissions(manage_channels=True)
    async def hide_channel(self, ctx, channel: commands.TextChannelConverter = None):
        """Hides a specific channel in the server."""
        if not self.moderation_data.get(str(ctx.guild.id), False):
            return await ctx.reply("Moderation is not enabled for this server.")

        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.read_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            title='Hide Channel',
            description=f'<:check:1087776909246607360> | {channel.mention} has been hidden.',
            color=0x977FD7
        )
        await ctx.send(embed=embed)

    @commands.command(name='unhide')
    @commands.has_permissions(manage_channels=True)
    async def unhide_channel(self, ctx, channel: commands.TextChannelConverter = None):
        """Unhides a specific channel in the server."""
        if not self.moderation_data.get(str(ctx.guild.id), False):
            return await ctx.reply("Moderation is not enabled for this server.")

        channel = channel or ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.read_messages = None
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        embed = discord.Embed(
            title='Unhide Channel',
            description=f'<:check:1087776909246607360> | {channel.mention} has been unhidden.',
            color=0x977FD7
        )
        await ctx.send(embed=embed)



    @commands.command(
                      help="Changes the slowmode",
                      usage="slowmode [seconds]",
                      aliases=["slow"])
    
    
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self, ctx, seconds: int = 0):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")
        
        if seconds > 120:
            return await ctx.send(embed=discord.Embed(
                title="slowmode",
                description="Slowmode can not be over 2 minutes",
                color=0x977FD7))
        if seconds == 0:
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(
                embed=discord.Embed(title="slowmode",
                                    description="Slowmode is disabled",
                                    color=0x977FD7))
        else:
            await ctx.channel.edit(slowmode_delay=seconds)
            await ctx.send(
                embed=discord.Embed(title="slowmode",
                                    description="Set slowmode to **`%s`**" %
                                    (seconds),
                                    color=0x977FD7))

    @commands.command(
                      help="Disables slowmode",
                      usage="unslowmode",
                      aliases=["unslow"])
    
    
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def unslowmode(self, ctx):
        moderation_enabled = self.moderation_data.get(str(ctx.guild.id), False)
        if not moderation_enabled:
            return await ctx.reply("Moderation is not enabled for this server.")

        await ctx.channel.edit(slowmode_delay=0)
        await ctx.send(embed=discord.Embed(title="unslowmode",
                                           description="Disabled slowmode",
                                           color=0x977FD7))


 



def setup(bot):
    bot.add_cog(Moderation(bot))
