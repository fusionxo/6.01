import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta
import re
from utils import *
from utils.checks import global_check

class TimerM(commands.Cog):
    MIN_INTERVAL = timedelta(minutes=10)  # Minimum interval of 10 minutes
    MAX_INTERVAL = timedelta(days=28)  # Maximum interval of 28 days
    COLOR = 0x977FD7  # Embed color
    THUMBNAIL_URL = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'

    def __init__(self, bot):
        self.bot = bot
        self.auto_messages = {}
        self.load_data()
        self.auto_message_task.start()
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help2_custom(self):
		      emoji = '<:puzzle:1087776730137239572>'
		      label = "AutoMessages"
		      description = "Shows the AutoMessages commands."
		      return emoji, label, description

    @commands.group()
    async def __AutoMessages__(self, ctx: commands.Context):
        """`am add <channel> <interval> <true/false> <message>`, `am remove <channel>`, `am view <channel>`, `am list`"""

    def load_data(self):
        """Load auto messages from JSON file."""
        if not os.path.exists("jsons/automessages.json"):
            with open("jsons/automessages.json", "w") as f:
                json.dump({}, f)
        with open("jsons/automessages.json", "r") as f:
            self.auto_messages = json.load(f)

    def save_data(self):
        """Save auto messages to JSON file."""
        with open("jsons/automessages.json", "w") as f:
            json.dump(self.auto_messages, f, indent=4)

    def parse_time(self, time_str):
        """Parse a time string into a timedelta object."""
        time_regex = re.match(r"(\d+)([smhd])$", time_str)
        if not time_regex:
            return None

        value, unit = int(time_regex.group(1)), time_regex.group(2)
        if unit == "s":
            return timedelta(seconds=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "d":
            return timedelta(days=value)

    @tasks.loop(seconds=10)  # Check every 10 seconds
    async def auto_message_task(self):
        """Send scheduled messages if the interval has passed."""
        for channel_id, data in self.auto_messages.items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                last_sent = datetime.fromisoformat(data["last_sent"])
                interval = timedelta(seconds=data["interval"])
                if datetime.utcnow() - last_sent >= interval:
                    if data["embed"]:
                        embed = discord.Embed(description=data["message"], color=self.COLOR)
                        embed.set_thumbnail(url=self.bot.user.avatar.url)
                        embed.set_footer(text="Luka | Auto Messages")
                        await channel.send(embed=embed)
                    else:
                        await channel.send(data["message"])

                    self.auto_messages[channel_id]["last_sent"] = datetime.utcnow().isoformat()
                    self.save_data()

    @auto_message_task.before_loop
    async def before_auto_message_task(self):
        await self.bot.wait_until_ready()

    def create_embed(self, title, description):
        """Helper function to create an embed with a title and description."""
        amembed = discord.Embed(title=title, color=self.COLOR)
        amembed.set_thumbnail(url=self.THUMBNAIL_URL)
        amembed.add_field(
            name='**Add an Auto Message**', 
            value='`$am add <channel> <interval> <true/false> <message>`\n'
                  'Create an auto message for the selected channel.\n'
                  'Examples:\n'
                  '`$am add #general 10m true This is an auto message sent as an embed!`\n'
                  '`$am add #announcements 1h false This is a normal auto message.`', 
            inline=False
        )
        amembed.add_field(
            name='**Remove an Auto Message**', 
            value='`$am remove <channel>`\n'
                  'Remove the auto message from the specified channel.\n'
                  'Example:\n'
                  '`$am remove #general`', 
            inline=False
        )
        amembed.add_field(
            name='**View Auto Message Configuration**', 
            value='`$am view <channel>`\n'
                  'View the current auto message configuration for the specified channel.\n'
                  'Example:\n'
                  '`$am view #general`', 
            inline=False
        )
        amembed.add_field(
            name='**List All Auto Messages**', 
            value='`$am list`\n'
                  'Lists all auto messages set in the current server.', 
            inline=False
        )
        amembed.set_footer(text='Luka • Page 1/1')
        return amembed

    @commands.group(name="automessage", aliases=["am", "auto messages"], invoke_without_command=True)
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def automessage(self, ctx):
        """Group command for automessage management."""
        embed = self.create_embed(
            "Automessage Commands", 
            "Here are the available commands for managing auto messages:"
        )
        await ctx.send(embed=embed)

    @automessage.command(name="add")
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def add(self, ctx, channel: discord.TextChannel, interval: str, embed_format: bool, *, message: str):
        """Add an auto message to a channel with a specified interval (e.g., 10m, 1h)."""
        time_delta = self.parse_time(interval)
        if not time_delta:
            embed = discord.Embed(title="Invalid Time Format", description="<:info:1087776877898383400> | Invalid time format. Please use a valid time like 10m, 1h, 1d.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        if time_delta < self.MIN_INTERVAL:
            embed = discord.Embed(title="Interval Too Short", description="<:info:1087776877898383400> | The minimum interval is 10 minutes.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        if time_delta > self.MAX_INTERVAL:
            embed = discord.Embed(title="Interval Too Long", description="<:info:1087776877898383400> | You can't set an interval longer than 28 days.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        interval_seconds = int(time_delta.total_seconds())

        if str(channel.id) in self.auto_messages:
            embed = discord.Embed(title="Auto Message Exists", description=f"<:info:1087776877898383400> | An auto message already exists for {channel.mention}. Remove it first before adding a new one.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        self.auto_messages[str(channel.id)] = {
            "interval": interval_seconds,
            "message": message,
            "last_sent": datetime.utcnow().isoformat(),
            "embed": embed_format
        }
        self.save_data()
        embed = discord.Embed(title="Auto Message Added", description=f"<:discotoolsxyzicon:1128990368659144745> | Auto message added to {channel.mention} with an interval of {interval}.", color=self.COLOR)
        await ctx.send(embed=embed)

    @automessage.command(name="remove")
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def remove(self, ctx, channel: discord.TextChannel):
        """Remove an auto message from a channel."""
        if str(channel.id) not in self.auto_messages:
            embed = discord.Embed(title="No Auto Message Found", description=f"<:discotoolsxyzicon1:1128990364678766612> | No auto message is set for {channel.mention}.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        del self.auto_messages[str(channel.id)]
        self.save_data()
        embed = discord.Embed(title="Auto Message Removed", description=f"<:discotoolsxyzicon:1128990368659144745> | Auto message removed from {channel.mention}.", color=self.COLOR)
        await ctx.send(embed=embed)

    @automessage.command(name="view")
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def view(self, ctx, channel: discord.TextChannel):
        """View the auto message for a specific channel."""
        if str(channel.id) not in self.auto_messages:
            embed = discord.Embed(title="No Auto Message Found", description=f"<:discotoolsxyzicon1:1128990364678766612> | No auto message is set for {channel.mention}.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        data = self.auto_messages[str(channel.id)]
        interval = str(timedelta(seconds=data['interval']))
        embed = discord.Embed(title="Auto Message Details", description=f"<:dot:1088106350904610827> | Auto message: `{data['message']}`\n<:dot:1088106350904610827> | Interval: {interval}\n<:dot:1088106350904610827> | Format: {'Embed' if data['embed'] else 'Normal'}", color=self.COLOR)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Luka | Auto Messages")
        await ctx.send(embed=embed)

    @automessage.command(name="list")
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def list(self, ctx):
        """List all auto messages."""
        if not self.auto_messages:
            embed = discord.Embed(title="No Auto Messages", description="<:discotoolsxyzicon1:1128990364678766612> | No auto messages are set.", color=self.COLOR)
            await ctx.send(embed=embed)
            return

        message_list = []
        for channel_id, data in self.auto_messages.items():
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                interval = str(timedelta(seconds=data['interval']))
                format_type = "Embed" if data['embed'] else "Normal"
                message_list.append(f"{channel.mention}: `{data['message']}` (Interval: {interval}, Format: {format_type})")

        if message_list:
            embed = discord.Embed(title="List of Auto Messages", description="\n".join(message_list), color=self.COLOR)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text="Luka | Auto Messages")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="No Valid Channels", description="<:discotoolsxyzicon1:1128990364678766612> | No valid channels found for auto messages.", color=self.COLOR)
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TimerM(bot))
