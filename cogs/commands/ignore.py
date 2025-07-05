from __future__ import annotations
import discord
from discord.ext import commands, tasks
from core import *
from utils.Tools import *
from typing import Optional
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator

class Ignore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.color = 0x2f3136

    @commands.group(name="ignore", invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def _ignore(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_ignore.group(name="channel",
                   aliases=["chnl"],
                   invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @blacklist_check()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _channel(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_channel.command(name="add")
    @commands.has_permissions(administrator=True)
    async def channel_add(self, ctx: Context, channel: discord.TextChannel):
        data = getIgnore(ctx.guild.id)
        ch= data["channel"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if str(channel.id) in ch:
                embed = discord.Embed(
                        description=
                        f"<:info:1087776877898383400> | {channel.mention} is already included in the ignore channel list.",
                        color=self.color)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                ch.append(str(channel.id))
                updateignore(ctx.guild.id, data)
                hacker4 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:check:1087776909246607360> | {channel.mention} has been successfully added to the ignore channel list.")
                hacker4.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=hacker4)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker5)

    @_channel.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def channel_remove(self, ctx, channel: discord.TextChannel):
        data = getIgnore(ctx.guild.id)
        ch= data["channel"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:   
            if len(ch) == 0:
                hacker = discord.Embed(
                    color=self.color,
                    description=
                    f"<:error:1088542929158688788> | There are no ignore channels set up in this server yet.")
                hacker.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=hacker)   
            else:
                if str(channel.id) not in ch:   
                    hacker1 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:error:1088542929158688788> | This channel is not in the list of ignored channels.")
                    hacker1.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.send(embed=hacker1) 
                else:
                    ch.remove(str(channel.id))
                    updateignore(ctx.guild.id, data)
                    hacker3 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:check:1087776909246607360> | {channel.mention} has been successfully removed from the ignore channel list.")
                    hacker3.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.send(embed=hacker3)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker5)                    
                    

######################



                    
################

    @_ignore.group(name="user",
                   aliases=["member", "u"],
                   invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @blacklist_check()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _user(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            
            
            
    @_user.command(name="add")
    @commands.has_permissions(administrator=True)
    async def user_add(self, ctx: Context, user: discord.User):
        data = getIgnore(ctx.guild.id)
        ch= data["user"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if str(user.id) in ch:
                embed = discord.Embed(
                        description=
                        f"<:info:1087776877898383400> | {user.mention} is already on the ignore users list.",
                        color=self.color)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                ch.append(str(user.id))
                updateignore(ctx.guild.id, data)
                hacker4 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:check:1087776909246607360> | {user.mention} has been successfully added to the ignore users list.")
                hacker4.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=hacker4)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker5)

    @_user.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def user_remove(self, ctx, user: discord.User):
        data = getIgnore(ctx.guild.id)
        ch= data["user"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:   
            if len(ch) == 0:
                hacker = discord.Embed(
                    color=self.color,
                    description=
                    f"<:error:1088542929158688788> | There are no ignore users set up in this server yet.")
                hacker.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=hacker)   
            else:
                if str(user.id) not in ch:   
                    hacker1 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:error:1088542929158688788> | {user.mention} is not on the ignore users list.")
                    hacker1.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.send(embed=hacker1) 
                else:
                    ch.remove(str(user.id))
                    updateignore(ctx.guild.id, data)
                    hacker3 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:check:1087776909246607360> | {user.mention} has been successfully removed from the ignore users list.")
                    hacker3.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.send(embed=hacker3)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker5)                   
                    
                    
###################






    @_ignore.group(name="exclude", invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @blacklist_check()
    async def _exclude(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

                    
                    




            
            
            
################

    @_exclude.group(name="user",
                   aliases=["member", "u"],
                   invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @blacklist_check()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _buser(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)
            
            
            
    @_buser.command(name="add")
    @commands.has_permissions(administrator=True)
    async def buser_add(self, ctx: Context, user: discord.User):
        data = getIgnore(ctx.guild.id)
        ch= data["excludeuser"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:
            if str(user.id) in ch:
                embed = discord.Embed(
                        description=
                        f"| {user.mention} is already included in the exclude users list.",
                        color=self.color)
                await ctx.reply(embed=embed, mention_author=False)
            else:
                ch.append(str(user.id))
                updateignore(ctx.guild.id, data)
                hacker4 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:check:1087776909246607360> | {user.mention} has been successfully added to the exclude users list.")
                hacker4.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=hacker4)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker5)

    @_buser.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def buser_remove(self, ctx, user: discord.User):
        data = getIgnore(ctx.guild.id)
        ch= data["excludeuser"]
        if ctx.author == ctx.guild.owner or ctx.author.top_role.position > ctx.guild.me.top_role.position:   
            if len(ch) == 0:
                hacker = discord.Embed(
                    color=self.color,
                    description=
                    f"<:error:1088542929158688788> | There are no exclude users set up in this server yet.")
                hacker.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=hacker)   
            else:
                if str(user.id) not in ch:   
                    hacker1 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:error:1088542929158688788> | {user.mention} is not on the exclude users list.")
                    hacker1.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.send(embed=hacker1) 
                else:
                    ch.remove(str(user.id))
                    updateignore(ctx.guild.id, data)
                    hacker3 = discord.Embed(
                        color=self.color,
                        description=
                        f"<:check:1087776909246607360> | {user.mention} has been successfully removed from the exclude users list.")
                    hacker3.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                    await ctx.send(embed=hacker3)
        else:
            hacker5 = discord.Embed(
                description=
                """```yaml\n - You must have Administrator permission.\n - Your top role should be above my top role.```""",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker5)
            
            
            
 
            
 
    @_user.command(name="show",
                        help="Shows list of ignored users in the server .",
                        usage="ignore user show")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def iuser_show(self, ctx):
        data = getIgnore(ctx.guild.id)
        ch= data["user"] 
        if len(ch) == 0:
            hacker = discord.Embed(
                color=self.color,
                title=f"{self.client.user.name}",
                description=
                f"<:error:1018174714750976030> | There are no ignored users for this server."
            )
            await ctx.reply(embed=hacker, mention_author=False)
        else:
            entries = [
                f"`{no}` | <@!{idk}> | ID: [{idk}](https://discord.com/users/{idk})"
                for no, idk in enumerate(ch, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"Ignored Users of {ctx.guild.name} - {len(ch)}",
                description="",
                color=self.color),
                                  ctx=ctx)
            await paginator.paginate()
            
            
            
    @_buser.command(name="show",
                        help="Shows list of ignore exclude users in the server .",
                        usage="ignore user show")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def buser_show(self, ctx):
        data = getIgnore(ctx.guild.id)
        ch= data["excludeuser"] 
        if len(ch) == 0:
            hacker = discord.Embed(
                color=self.color,
                title=f"{self.client.user.name}",
                description=
                f"<:error:1018174714750976030> | There are no exclude users for this server."
            )
            await ctx.reply(embed=hacker, mention_author=False)
        else:
            entries = [
                f"`{no}` | <@!{idk}> | ID: [{idk}](https://discord.com/users/{idk})"
                for no, idk in enumerate(ch, start=1)
            ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"Ignore Exclude Users of {ctx.guild.name} - {len(ch)}",
                description="",
                color=self.color),
                                  ctx=ctx)
            await paginator.paginate()
            
            
            
######