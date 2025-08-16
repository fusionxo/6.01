import contextlib
from traceback import format_exception
import discord
from discord.ext import commands
import io
import textwrap
import datetime
import sys
from discord.ui import Button, View
import psutil
import time
import datetime
import platform
from utils.Tools import *
import os
import logging
from discord.ext import commands
from pymongo import MongoClient
from discord.ext.commands import BucketType, cooldown
import requests
from typing import Optional
import pymongo
import aiohttp
import urllib.parse
import re
import json
import discord, psutil, pathlib, shutil, os, sys
from typing import Optional, Union
# Pillow is required for image generation.
from PIL import Image, ImageDraw, ImageFont, ImageOps

def get_ram_usage():
    return int(psutil.virtual_memory().total - psutil.virtual_memory().available)


def get_ram_total():
    return int(psutil.virtual_memory().total)


start_time = time.time()
#########3
def datetime_to_seconds(thing: datetime.datetime):
    current_time = datetime.datetime.fromtimestamp(time.time())
    return round(round(time.time()) + (current_time - thing.replace(tzinfo=None)).total_seconds())
cluster = MongoClient("mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net/note?retryWrites=true&w=majority")
db = cluster["note"]
collection = db["notedata"]

class Extra(commands.Cog):
    VERSION = "7.0.0"
    LATEST_RELEASE = "2025-07-30"
    def __init__(self, bot):
        self.bot = bot
        self.connection = pymongo.MongoClient(
            "mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net/ready?retryWrites=true&w=majority"
        )
        self.db = self.connection["ready"]["readydata"]
        self.start_time = datetime.datetime.utcnow()
        self.message_count = 0

    async def _create_badge_profile(self, user: discord.User, badges: list) -> discord.File:
        # --- Asset & Font Loading ---
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(str(user.display_avatar.with_size(256))) as resp:
                    avatar_bytes = await resp.read() if resp.status == 200 else None
            except Exception:
                avatar_bytes = None

            badge_data_list = []
            for badge_text in badges:
                match = re.search(r"<a?:(\w+):(\d+)>", badge_text)
                clean_text = badge_text.replace("*", "").split("ㆍ")[-1]
                if match:
                    emoji_id = match.group(2)
                    emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
                    try:
                        async with session.get(emoji_url) as resp:
                            if resp.status == 200:
                                badge_data_list.append({"text": clean_text, "image": await resp.read()})
                    except Exception:
                        continue
        
        try:
            title_font = ImageFont.truetype("assets/fonts/Poppins-Bold.ttf", 45)
            base_font = ImageFont.truetype("assets/fonts/Poppins-Regular.ttf", 24)
        except IOError:
            title_font = ImageFont.truetype("arialbd.ttf", 45)
            base_font = ImageFont.truetype("arial.ttf", 24)

        # --- Dynamic Height & Layout Calculation ---
        items_per_row = 4 # Changed from 5 to 4
        badge_rows = 0
        if badge_data_list:
            badge_rows = (len(badge_data_list) - 1) // items_per_row + 1
        
        base_height = 360
        badge_area_height = badge_rows * 110
        padding = 40
        card_height = base_height + badge_area_height

        # --- Image Generation ---
        card = Image.new('RGB', (900, card_height), color='#2C2F33')
        draw = ImageDraw.Draw(card)

        # Draw background gradient
        for i in range(card.height):
            ratio = i / card.height
            r = int(44 + (35 - 44) * ratio)
            g = int(47 + (39 - 47) * ratio)
            b = int(51 + (42 - 51) * ratio)
            draw.line([(0, i), (card.width, i)], fill=(r, g, b))

        # Draw user avatar
        if avatar_bytes:
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
            size = (200, 200)
            mask = Image.new('L', size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0) + size, fill=255)
            
            border_size = (size[0] + 10, size[1] + 10)
            border_bg = Image.new('RGBA', border_size, (0, 0, 0, 0))
            border_draw = ImageDraw.Draw(border_bg)
            border_draw.ellipse((0, 0) + border_size, fill='#99AAB5')
            card.paste(border_bg, (45, 45), border_bg)

            output = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            card.paste(output, (50, 50), output)

        # Draw user name with shadow
        user_text = str(user)
        shadow_color = "#23272A"
        draw.text((302, 72), user_text, font=title_font, fill=shadow_color)
        draw.text((300, 70), user_text, font=title_font, fill='#FFFFFF')

        # Draw badges title and divider
        draw.text((70, 280), "Badges", font=title_font, fill='#FFFFFF')
        draw.line([(70, 340), (830, 340)], fill='#99AAB5', width=2)
        
        # Draw badge icons and text
        if not badge_data_list:
            draw.text((70, 360), "No badges to display.", font=base_font, fill='#72767D')
        else:
            x, y = 70, 360
            item_width = 210 # Increased from 160
            for i, badge in enumerate(badge_data_list):
                # Draw badge image, preserving aspect ratio
                badge_img = Image.open(io.BytesIO(badge['image'])).convert("RGBA")
                badge_img.thumbnail((64, 64), Image.Resampling.LANCZOS)
                
                img_canvas = Image.new('RGBA', (64, 64), (0,0,0,0))
                paste_x = (64 - badge_img.width) // 2
                paste_y = (64 - badge_img.height) // 2
                img_canvas.paste(badge_img, (paste_x, paste_y))
                
                card.paste(img_canvas, (x, y), img_canvas)
                
                # Draw badge text below the image
                bbox = draw.textbbox((0, 0), badge['text'], font=base_font)
                text_width = bbox[2] - bbox[0]
                text_x = x + (64 - text_width) // 2
                text_y = y + 70
                draw.text((text_x, text_y), badge['text'], font=base_font, fill='#FFFFFF')

                if (i + 1) % items_per_row == 0:
                    x = 70
                    y += 110
                else:
                    x += item_width

        final_buffer = io.BytesIO()
        card.save(final_buffer, "PNG")
        final_buffer.seek(0)
        
        return discord.File(fp=final_buffer, filename=f"profile_{user.id}.png")

  
    @commands.hybrid_command(description="Shows the bot's statistics.", aliases=["statistics", "st"], usage="stats")
    async def stats(self, ctx):
      
        system = platform.system()
        python_version = f"Python {platform.python_version()}"
        discord_version = f"discord.py {discord.__version__}"
        total_memory = f"{psutil.virtual_memory().total / (1024 ** 2):.2f} MB"
        used_memory = f"{psutil.virtual_memory().used / (1024 ** 2):.2f} MB"
        cpu_percent = f"{psutil.cpu_percent(interval=1):.2f}%"
        cpu_count = f"{psutil.cpu_count()}"

        process = psutil.Process()
        process_memory = f"{process.memory_info().rss / (1024 ** 2):.2f} MB"
        process_cpu_percent = f"{process.cpu_percent(interval=1):.2f}%"

        server_count = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        cached_members = len(self.bot.users)

        latency = f"{self.bot.latency * 1000:.2f} ms"
        shard_id = ctx.guild.shard_id if ctx.guild else 0

        current_time = datetime.datetime.utcnow()
        uptime = current_time - self.start_time
        uptime_str = str(uptime).split('.')[0]


        embed = discord.Embed(title="Luka's Statistics", color=0x977FD7)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
        embed.add_field(name="🖥 System", value=f"""```yaml\n{system}\n{python_version}\n{discord_version}\n{total_memory} total\n{used_memory} used\n{cpu_percent} CPU\n{cpu_count} cores```""", inline=False)
        embed.add_field(name="📡 Process", value=f"""```yaml\n{process_memory} memory\n{process_cpu_percent} CPU```""", inline=False)
        embed.add_field(name="🌐 Discord", value=f"""```yaml\n{server_count} servers\n{total_members} members\n{cached_members} cached\n{latency} latency\nShard ID {shard_id}```""", inline=False)
      
        embed.add_field(name="⏰ Uptime", value=f"""```\n{uptime_str}```""", inline=True)
        embed.add_field(name="💻 Commands", value=f"""```\n{len(set(ctx.bot.walk_commands()))} commands```""", inline=True)
        embed.add_field(name="💬 Messages", value=f"""```\n{self.message_count} messages received```""", inline=True)


        embed.set_footer(text=f"Version {self.VERSION} | Developer : kamiplayzofficial")

        invite_button = discord.ui.Button(style=discord.ButtonStyle.link, label="Invite Link", url="https://fusionxo.com/luka/invite")
        support_button = discord.ui.Button(style=discord.ButtonStyle.link, label="Support Server", url="https://fusionxo.com/luka/support")
        view = discord.ui.View()
        view.add_item(invite_button)
        view.add_item(support_button)

        await ctx.send(embed=embed, view=view)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "<@1040194948496109569>":
            prefix = "$"

            button = Button(label="Invite Luka", url="https://fusionxo.com/luka/invite")
            button1 = Button(label="Support Server", url="https://fusionxo.com/luka/support")
            button2 = Button(label="Vote Us", url="https://fusionxo.com/luka/vote")

            embed = discord.Embed(
                description=f"""Hello there! <a:cutieeheart:1017407063598575646> I'm **Luka**!

                To get help, just type in `{prefix}help`. <:LUKA5:1093892855950491750>

                And if you need additional assistance, feel free to join us on KAMI's Discord server by clicking on this link:  https://bit.ly/luka-support. We're always happy to help you out with anything you need! <a:dil:1045290487654907944>""",
                color=0x977FD7)
            view = View()
            view.add_item(button)
            view.add_item(button1)
            view.add_item(button2)
            await message.reply(f"Hey..!! {message.author.mention}", embed=embed, mention_author=True, view=view)        
        
        
  
    @commands.hybrid_group(description='Get Luka invite link', aliases=[("inv")])
    
    
    async def invite(self, ctx):
        guild = ctx.guild
    
        icon_url = guild.icon.url if guild.icon else None
    
        embed = discord.Embed(description="Use Buttons To Invite Luka or Join Our Support Server", color=0x977FD7)
        embed.set_thumbnail(url=icon_url)
    
        button2 = discord.ui.Button(label='Invite', emoji="<:Invitelink:1040661606809473046>",  style=discord.ButtonStyle.blurple)
        button1 = discord.ui.Button(label='Server', emoji="<:users:1044192823215394856>",  style=discord.ButtonStyle.success)
        button = discord.ui.Button(label='Back', emoji="↩️",  style=discord.ButtonStyle.danger)
        view = discord.ui.View()
        view.add_item(button2)
        view.add_item(button1)
        view.add_item(button)
    
        async def button2_callback(interaction: discord.Interaction):
            embed1 = discord.Embed(description=f'[Click To Invite Me](https://fusionxo.com/luka/invite)', color=0x977FD7)
            await interaction.response.send_message(embed=embed1, ephemeral=True)
    
        async def button_callback(interaction: discord.Interaction):
            embed5 = discord.Embed(description="Use Buttons To Invite Luka or Join Our Support Server", color=0x977FD7)
            embed5.set_thumbnail(url=icon_url)
            await interaction.response.send_message(embed=embed5, ephemeral=True)
    
        async def button1_callback(interaction: discord.Interaction):
            embed3 = discord.Embed(description="**Click **[here](https://fusionxo.com/luka/support) **To Join Support Server**", color=0x977FD7)
            await interaction.response.send_message(embed=embed3, ephemeral=True)
    
        button2.callback = button2_callback
        button1.callback = button1_callback
        button.callback = button_callback
  
        await ctx.send(embed=embed, view=view)



      

    @commands.cooldown(1, 60, commands.BucketType.user)
    
    
    @commands.hybrid_command(description='Shows the bot information.', with_app_command=True, name="info", aliases=['botinfo', 'bi'])
    @commands.guild_only()
    async def _info(self, ctx):
        # Calculate uptime
        uptime_seconds = int(time.time() - self.start_time.timestamp())
        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
        weeks, days, hours, minutes, seconds = uptime_seconds // 604800, (uptime_seconds // 86400) % 7, (uptime_seconds // 3600) % 24, (uptime_seconds // 60) % 60, uptime_seconds % 60

        # Get process information
        process = psutil.Process()
        pid = process.pid
        mem_info = process.memory_info()
        mem_rss = mem_info.rss / 1024 / 1024
        mem_vms = mem_info.vms / 1024 / 1024

        # Count active voice channels and guilds playing music
        voice_connections = sum(1 for vc in self.bot.voice_clients if vc.is_connected())
        music_guilds = sum(1 for vc in self.bot.voice_clients if vc.is_playing())

        # Count users and messages
        user_count = len(self.bot.users)
        message_count = self.db.count_documents({})

        # Count files, functions, classes, and lines of code
        file_count = 0
        function_count = 0
        class_count = 0
        line_count = 0
        for path in pathlib.Path().rglob('*.py'):
            if str(path).startswith("venv"):
                continue
            try:
                # Try to read the file using utf-8 encoding
                with path.open(encoding='utf-8') as f:
                    source = f.read()
            except UnicodeDecodeError:
                # If utf-8 fails, try ignoring problematic characters
                with path.open(encoding='utf-8', errors='ignore') as f: 
                    source = f.read()
                file_count += 1
                function_count += len(re.findall(r'^\s*async\s+def\s+\w+\(', source, re.MULTILINE))
                function_count += len(re.findall(r'^\s*def\s+\w+\(', source, re.MULTILINE))
                class_count += len(re.findall(r'^\s*class\s+\w+\(', source, re.MULTILINE))
                line_count += len(source.splitlines())

        # Get disk usage information
        try:
            disk_usage = shutil.disk_usage('/')
            disk_usage_str = f"{disk_usage.used // (2 ** 30)} GB / {disk_usage.total // (2 ** 30)} GB ({disk_usage.percent:.1f}%)"
        except AttributeError:
            disk_usage_str = "N/A"

        embed = discord.Embed(color=discord.Colour(0x977FD7), description=f"""**Developers:** [K4MI ⸸#8166](https://discord.com/users/980763915749322773) \n [LUKA#8702](https://discord.com/users/975012142640169020)
```adoc
Created At ::  {ctx.me.created_at}
Guilds :: {len(ctx.bot.guilds):,}
Users :: {user_count:,}
Commands :: {len(set(ctx.bot.walk_commands()))}
Shards :: {len(self.bot.shards)}
Status :: {self.bot.status}```""")
        if self.bot.activity is not None:
            embed.add_field(name="Activity", value=f"""```yaml\n
Type :: {self.bot.activity.type.name.title()}
Name :: {self.bot.activity.name}```""")
        embed.add_field(name="System Information", value=f"""```yaml\n
CPU Usage :: {psutil.cpu_percent()}%
Memory Usage :: {mem_rss:.2f} MB (RSS) / {mem_vms:.2f} MB (VMS)
Disk Usage :: {disk_usage_str}
Process ID :: {pid}```""")
        embed.add_field(name="Uptime", value=f"```yaml\n{weeks} weeks, {days} days, {hours} hours, {minutes} minutes, {seconds} seconds```")
        embed.add_field(name="Counts", value=f"""```yaml\n
Messages :: {message_count:,}
Files :: {file_count:,}
Functions :: {function_count:,}
Classes :: {class_count:,}
Lines :: {line_count:,}```""")
        embed.add_field(name="Music", value=f"""```yaml\n
Voice Connections :: {voice_connections}
Guilds Playing Music :: {music_guilds}```""")
        embed.set_footer(text=f"Version {self.VERSION} | Latest release {self.LATEST_RELEASE}")
        await ctx.send(embed=embed)


    @commands.command(name="serverinfo", aliases=["sinfo", "si"], with_app_command=True)
    async def serverinfo(self, ctx: commands.Context):
            c_at = int(ctx.guild.created_at.timestamp())
            nsfw_level = ''
            if ctx.guild.nsfw_level.name == 'default':
                nsfw_level = 'Default'
            if ctx.guild.nsfw_level.name == 'explicit':
                nsfw_level = 'Explicit'
            if ctx.guild.nsfw_level.name == 'safe':
                nsfw_level = 'Safe'
            if ctx.guild.nsfw_level.name == 'age_restricted':
                nsfw_level = 'Age Restricted'

            guild: discord.Guild = ctx.guild
            t_emojis = len(guild.emojis)
            t_stickers = len(guild.stickers)
            total_emojis = t_emojis + t_stickers

            embed = discord.Embed(color=0x2f3136).set_author(
                name=f"{guild.name}'s Information",
                icon_url=guild.me.display_avatar.url
                if guild.icon is None else guild.icon.url).set_footer(
                    text=f"Requested By {ctx.author}",
                    icon_url=ctx.author.avatar.url
                    if ctx.author.avatar else ctx.author.default_avatar.url)
            if guild.icon is not None:
                embed.set_thumbnail(url=guild.icon.url)
                embed.timestamp = discord.utils.utcnow()

            # Updated role handling to prevent exceeding character limits
            roles = [role.mention for role in guild.roles[1:]]
            roles.reverse()
            
            roless = ""
            if not roles:
                roless = "None"
            else:
                role_mentions = []
                current_length = 0
                limit = 900  # Safe limit to leave space for "and X more..."

                for r in roles:
                    # Add length of mention and separator " • "
                    if current_length + len(r) + 3 > limit:
                        break
                    role_mentions.append(r)
                    current_length += len(r) + 3
                
                roless = " • ".join(role_mentions)
                
                remaining_count = len(roles) - len(role_mentions)
                if remaining_count > 0:
                    roless += f" **• and {remaining_count} more...**"

            # A final fallback, just in case
            if len(roless) > 1024:
                roless = "Too many roles to show here."


            embed.add_field(
                name="**__About__**",
                value=
                f"**Name : ** {guild.name}\n**ID :** {guild.id}\n**Owner <:OwnerIcon:1040661621174976563> :** {guild.owner} (<@{guild.owner_id}>)\n**Created At : ** <t:{c_at}:F>\n**Members :** {len(guild.members)}",
                inline=False)

            embed.add_field(
                name="**__Extras__**",
                value=
                f"""**Verification Level :** {str(guild.verification_level).title()}\n**AFK Channel :** {ctx.guild.afk_channel}\n**AFK Timeout :** {str(ctx.guild.afk_timeout / 60)}\n**System Channel :** {"None" if guild.system_channel is None else guild.system_channel.mention}\n**NSFW level :** {nsfw_level}\n**Explicit Content Filter :** {guild.explicit_content_filter.name}\n**Max Talk Bitrate :** {int(guild.bitrate_limit)} kbps""",
                inline=False)

            embed.add_field(name="**__Description__**",
                            value=f"""{guild.description}""",
                            inline=False)
            if guild.features:
                embed.add_field(
                    name="**__Features__**",
                    value="\n".join([
                        f"<:check:1087776909246607360> : {feature.replace('_',' ').title()}"
                        for feature in guild.features
                    ]))

            embed.add_field(name="**__Members__**",
                            value=f"""
    Members : {len(guild.members)}
    Humans : {len(list(filter(lambda m: not m.bot, guild.members)))}
    Bots : {len(list(filter(lambda m: m.bot, guild.members)))}
                """,
                            inline=False)

            embed.add_field(name="**__Channels__**",
                            value=f"""
    Categories : {len(guild.categories)}
    Text Channels : {len(guild.text_channels)}
    Voice Channels : {len(guild.voice_channels)}
    Threads : {len(guild.threads)}
                """,
                            inline=False)

            embed.add_field(name="**__Emoji Info__**",
                            value=f"""
    **Regular Emojis :** {t_emojis}
    **Stickers :** {t_stickers}
    **Total Emoji/Stickers :** {total_emojis}
                """,
                            inline=False)

            booster_role = guild.premium_subscriber_role
            booster_role_mention = f"<@&{booster_role.id}>" if booster_role is not None else "Not set"

            embed.add_field(
                name="**__Boost Status__**",
                value=f"Level: {guild.premium_tier} [<a:NITRO:1040662466998325309> {guild.premium_subscription_count} Boosts]\nBooster Role: {booster_role_mention}",
                inline=False)

            embed.add_field(name=f"**__Server Roles [ {len(guild.roles)} ]__**",
                            value=f"{roless}",
                            inline=False)

            if guild.banner is not None:
                embed.set_image(url=guild.banner.url)
            return await ctx.reply(embed=embed)

  

    
    
    @commands.hybrid_command(name="userinfo",
                             aliases=["whois", "ui"],
                             usage="Userinfo [user]",with_app_command = True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _userinfo(self,
                        ctx,
                        member: Optional[Union[discord.Member, discord.User]] = None):
        if member == None or member == "":
            member = ctx.author
        elif member not in ctx.guild.members:
            member = await self.bot.fetch_user(member.id)

        badges = ""
        if member.public_flags.hypesquad:
            badges += "<:hypesquad:1108273258874282014> "
        if member.public_flags.hypesquad_balance:
            badges += "<:Balance:1108271102754553898> "
        if member.public_flags.hypesquad_bravery:
            badges += "<:Bravery:1108271251195179068> "
        if member.public_flags.hypesquad_brilliance:
            badges += "<:Brilliance:1108271424138924042> "
        if member.public_flags.early_supporter:
            badges += "<:EarlySupporter:1108271665768583238> "
        if member.public_flags.active_developer:
            badges += "<a:ativedev:1108272212311552051> "
        if member.public_flags.discord_certified_moderator:
            badges += "<:Moderator:1108272882372583475> "
        if member.public_flags.staff:
            badges += "<:Staffteam:1108272888110391326> "
        if member.public_flags.partner:
            badges += "<:partner:1108272879625322567> "
        if badges == None or badges == "":
            badges += "None"

        if member in ctx.guild.members:
            nickk = f"{member.nick if member.nick else 'None'}"
            joinedat = f"<t:{round(member.joined_at.timestamp())}:R>"
        else:
            nickk = "None"
            joinedat = "None"

        kp = ""
        if member in ctx.guild.members:
            if member.guild_permissions.kick_members:
                kp += "Kick Members"
            if member.guild_permissions.ban_members:
                kp += " , Ban Members"
            if member.guild_permissions.administrator:
                kp += " , Administrator"
            if member.guild_permissions.manage_channels:
                kp += " , Manage Channels"


#    if  member.guild_permissions.manage_server:
#        kp = "Manage Server"
            if member.guild_permissions.manage_messages:
                kp += " , Manage Messages"
            if member.guild_permissions.mention_everyone:
                kp += " , Mention Everyone"
            if member.guild_permissions.manage_nicknames:
                kp += " , Manage Nicknames"
            if member.guild_permissions.manage_roles:
                kp += " , Manage Roles"
            if member.guild_permissions.manage_webhooks:
                kp += " , Manage Webhooks"
            if member.guild_permissions.manage_emojis:
                kp += " , Manage Emojis"

            if kp is None or kp == "":
                kp = "None"

        if member in ctx.guild.members:
            if member == ctx.guild.owner:
                aklm = "Server Owner"
            elif member.guild_permissions.administrator:
                aklm = "Server Admin"
            elif member.guild_permissions.ban_members or member.guild_permissions.kick_members:
                aklm = "Server Moderator"
            else:
                aklm = "Server Member"

        bannerUser = await self.bot.fetch_user(member.id)
        embed = discord.Embed(color=0x977FD7)
        embed.timestamp = discord.utils.utcnow()
        if not bannerUser.banner:
            pass
        else:
            embed.set_image(url=bannerUser.banner)
        embed.set_author(name=f"{member.name}'s Information",
                         icon_url=member.avatar.url
                         if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.
                            default_avatar.url)
        embed.add_field(name="__General Information__",
                        value=f"""
**Name:** {member}
**ID:** {member.id}
**Nickname:** {nickk}
**Bot?:** {'Yes' if member.bot else 'No'}
**Badges:** {badges}
**Account Created:** <t:{round(member.created_at.timestamp())}:R>
**Server Joined:** {joinedat}
            """,
                        inline=False)
        if member in ctx.guild.members:
            r = (', '.join(role.mention for role in member.roles[1:][::-1])
                 if len(member.roles) > 1 else 'None.')
            embed.add_field(name="__Role Info__",
                            value=f"""
**Highest Role:** {member.top_role.mention if len(member.roles) > 1 else 'None'}
**Roles [{f'{len(member.roles) - 1}' if member.roles else '0'}]:** {r if len(r) <= 1024 else r[0:1006] + ' and more...'}
**Color:** {member.color if member.color else '000000'}
                """,
                            inline=False)
        if member in ctx.guild.members:
            embed.add_field(
                name="__Extra__",
                value=
                f"**Boosting:** {f'<t:{round(member.premium_since.timestamp())}:R>' if member in ctx.guild.premium_subscribers else 'None'}\n**Voice <:soundfull:1087776969627811891>:** {'None' if not member.voice else member.voice.channel.mention}",
                inline=False)
        if member in ctx.guild.members:
            embed.add_field(name="__Key Permissions__",
                            value=", ".join([kp]),
                            inline=False)
        if member in ctx.guild.members:
            embed.add_field(name="__Acknowledgement__",
                            value=f"{aklm}",
                            inline=False)
        if member in ctx.guild.members:
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
        else:
            if member not in ctx.guild.members:
                embed.set_footer(
                    text=f"{member.name} not in this this server.",
                    icon_url=ctx.author.avatar.url
                    if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)




  
    @commands.hybrid_command(description='Shows information of a role.', help="Shows you all information about a role.",usage="Roleinfo <role>")
    
    
    async def roleinfo(self, ctx: commands.Context, *, role: discord.Role):
        """Get information about a role"""
        content = discord.Embed(title=f"@{role.name} | #{role.id}")

        content.colour = role.color

        if isinstance(role.icon, discord.Asset):
            content.set_thumbnail(url=role.icon.url)
        elif isinstance(role.icon, str):
            content.title = f"{role.icon} @{role.name} | #{role.id}"

        content.add_field(name="Color", value=str(role.color).upper())
        content.add_field(name="Member count", value=len(role.members))
        content.add_field(name="Created at", value=role.created_at.strftime("%d/%m/%Y %H:%M"))
        content.add_field(name="Hoisted", value=str(role.hoist))
        content.add_field(name="Mentionable", value=role.mentionable)
        content.add_field(name="Mention", value=role.mention)
        if role.managed:
            if role.tags.is_bot_managed():
                manager = ctx.guild.get_member(role.tags.bot_id)
            elif role.tags.is_integration():
                manager = ctx.guild.get_member(role.tags.integration_id)
            elif role.tags.is_premium_subscriber():
                manager = "Server boosting"
            else:
                manager = "UNKNOWN"
            content.add_field(name="Managed by", value=manager)

        perms = []
        for perm, allow in iter(role.permissions):
            if allow:
                perms.append(f"`{perm.upper()}`")

        if perms:
            content.add_field(name="Allowed permissions", value=" ".join(perms), inline=False)

        await ctx.send(embed=content)



    
    
    @commands.group(
                      description="Shows users status",
                      usage="status <member>")
    async def status(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        status = member.status
        if status == discord.Status.offline:
            status_location = "Not Applicable"
        elif member.mobile_status != discord.Status.offline:
            status_location = "Mobile"
        elif member.web_status != discord.Status.offline:
            status_location = "Browser"
        elif member.desktop_status != discord.Status.offline:
            status_location = "Desktop"
        else:
            status_location = "Not Applicable"
        await ctx.send(embed=discord.Embed(title="**<a:green_fire:1016313318031491092> | status**",
                                           description="`%s`: `%s`" %
                                           (status_location, status),
                                           color=0x977FD7))

    @commands.group(
                      help="Shows emoji syntax",
                      usage="emoji <emoji>")
    
    
    async def emoji(self, ctx, emoji: discord.Emoji):
        return await ctx.send(
            embed=discord.Embed(title="**<a:green_fire:1016313318031491092> | emoji**",
                                description="emoji: %s\nid: **`%s`**" %
                                (emoji, emoji.id),
                                color=0x977FD7))

    @commands.group(
                      help="Shows user syntax",
                      usage="user [user]")
    
    
    async def user(self, ctx, user: discord.Member = None):
        return await ctx.send(
            embed=discord.Embed(title="user",
                                description="user: %s\nid: **`%s`**" %
                                (user.mention, user.id),
                                color=0x977FD7))

    @commands.group(
                      help="Shows role syntax",
                      usage="roleid <role>")
    
    
    async def roleid(self, ctx, role: discord.Role):
        return await ctx.send(
            embed=discord.Embed(title="role",
                                description="role: %s\nid: **`%s`**" %
                                (role.mention, role.id),
                                color=0x977FD7))

    @commands.group(
                      help="Shows channel syntax",
                      usage="channel <channel>")
    
    
    async def channel(self, ctx, channel: discord.TextChannel):
        return await ctx.send(
            embed=discord.Embed(title="channel",
                                description="channel: %s\nid: **`%s`**" %
                                (channel.mention, channel.id),
                                color=0x977FD7))

    @commands.group(
                      help="Shows boosts count",
                      usage="boosts",
                      aliases=["bc"])
    
    
    async def boosts(self, ctx):
        await ctx.send(
            embed=discord.Embed(title=f"Boosts Count Of {ctx.guild.name}",
                                description="**`%s`**" %
                                (ctx.guild.premium_subscription_count),
                                color=0x977FD7))

      
    @commands.command(
        help="Adds one or more emojis, or steals stickers if none provided.",
        usage="steal <emoji1> [emoji2 ...]",
        aliases=["eadd", "ssticker"]
    )
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, *emotes: str):
        new_name = None

        if not emotes:
            if not ctx.message.stickers:
                return await ctx.send(
                    embed=discord.Embed(
                        title="Steal",
                        description="Please provide an emoji or send a sticker to steal.",
                        color=0x977FD7
                    )
                )

            try:
                for sticker in ctx.message.stickers:
                    fetched_sticker = await sticker.fetch()

                    if not isinstance(fetched_sticker, discord.GuildSticker):
                        raise commands.CommandError("I cannot steal default Discord stickers!")

                    name = new_name if new_name else fetched_sticker.name
                    sticker_file = await fetched_sticker.to_file()

                    my_new_sticker = await ctx.guild.create_sticker(
                        name=name,
                        description=fetched_sticker.description or "",
                        emoji=fetched_sticker.emoji,
                        file=sticker_file,
                    )

                    embed = discord.Embed(
                        description=(
                            f"Successfully stole sticker `{my_new_sticker.name}` "
                            f"and added it to this server with the name \"{name}\""
                        ),
                        color=0x977FD7,
                    )
                    embed.set_thumbnail(url=my_new_sticker.url)
                    await ctx.send(embed=embed)
            except Exception as e:
                await ctx.send(
                    embed=discord.Embed(
                        title="Sticker Add",
                        description=f"Failed to steal sticker. Error: {str(e)}",
                        color=0x977FD7
                    )
                )
            return

        added = []
        for emote in emotes:
            if not emote.startswith('<') or ':' not in emote:
                continue
            try:
                parts = emote.strip('<>').split(':')  
                anim_flag = parts[0]
                name = parts[1]
                emoji_id = parts[2]
                ext = 'gif' if anim_flag == 'a' else 'png'
                url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"

                resp = requests.get(url)
                resp.raise_for_status()
                img_data = resp.content

                new_emoji = await ctx.guild.create_custom_emoji(name=name, image=img_data)
                added.append(f"{new_emoji} (`:{name}:`)")
            except Exception as e:
                await ctx.send(
                    embed=discord.Embed(
                        title="Emoji Add",
                        description=f"Failed to add {emote}. Error: {e}",
                        color=0x977FD7
                    )
                )

        if added:
            await ctx.send(
                embed=discord.Embed(
                    title="Emoji Add",
                    description="Added emojis: " + ", ".join(added),
                    color=0x977FD7
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="Emoji Add",
                    description="No valid custom emojis found to steal.",
                    color=0x977FD7
                )
            )
       
            

    @commands.hybrid_command(description='Deletes a emoji from the server.', help="Deletes the emoji from the server",usage="removeemoji <emoji>")
    
    
    @commands.has_permissions(manage_emojis=True)
    async def removeemoji(self, ctx, emoji: discord.Emoji):
        await emoji.delete()
        await ctx.send(f"**<:check:1087776909246607360> emoji has been deleted.**")

    @commands.hybrid_command(description='Unbans Everyone Banned Person From The Guild.', help="Unbans Everyone In The Guild!", aliases=['massunban'],usage="Unbanall")
    
    
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only() 
    @commands.has_permissions(ban_members=True)
    async def unbanall(self, ctx):
        button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:check:1087776909246607360>")
        button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:wrong:1087776947720953949>")
        async def button_callback(interaction: discord.Interaction):
          a = 0
          if interaction.user == ctx.author:
            if interaction.guild.me.guild_permissions.ban_members:
              await interaction.response.edit_message(content=f"Unbanning All Banned Member(s)", embed=None, view=None)
              async for idk in interaction.guild.bans(limit=None):
                await interaction.guild.unban(user=idk.user, reason="Unbanall Command Executed By: {}".format(ctx.author))
                a += 1
              await interaction.channel.send(content=f"Successfully Unbanned {a} Member(s)")
            else:
              await interaction.response.edit_message(content="I am missing ban members permission.\ntry giving me permissions and retry", embed=None, view=None)
          else: 
            await interaction.response.send_message("This Is Not For You Dummy!", embed=None, view=None, ephemeral=True) 

        async def button1_callback(interaction: discord.Interaction): 
          if interaction.user == ctx.author: 
            await interaction.response.edit_message(content="Ok I will not unban anyone in this guild", embed=None, view=None)
          else:
            await interaction.response.send_message("This Is Not For You Dummy!", embed=None, view=None, ephemeral=True)
        embed = discord.Embed(title='Confirmation',
                          color=0x977FD7,
                          description=f'**Are you sure you want to unban everyone in this guild?**')
        embed.set_footer(text="Made With 💖 By K4MI ⸸#8166")
        
        view = View()
        button.callback = button_callback
        button1.callback = button1_callback
        view.add_item(button)
        view.add_item(button1)
        await ctx.reply(embed=embed, view=view, mention_author=False)



    @commands.hybrid_command(description='Shows when a user joined', 
                      help="Shows when a user joined",
                      usage="joined-at [user]",
                      aliases=["joined-at"])
    
    
    async def joined_at(self, ctx):
        joined = ctx.author.joined_at.strftime("%a, %d %b %Y %I:%M %p")
        await ctx.send(embed=discord.Embed(title="joined-at",
                                           description="**`%s`**" % (joined),
                                            color=0x977FD7))


    @commands.command(help="Shows the latency", usage="ping", aliases=["latency"])
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f":ping_pong: Pong! Websocket **{latency}** ms\n Yes, I'm still alive!")


    @commands.hybrid_command(description='Shows the first messsage sent in the mentioned channel or current channel', 
            help=
            "First message sent in the mentioned channel or current channel",
            usage="firstmsg",
            aliases=["fmsg", "first"])
    
    
    async def firstmsg(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        async for message in channel.history(limit=1, oldest_first=True):
            first_message = message
            break
        embed = discord.Embed(color=0x977FD7)
        if first_message.content:
            embed.set_author(name=first_message.content,
                             url=first_message.jump_url)
        else:
            embed.description = f"This message has no content. Jump URL: {first_message.jump_url}"
        await ctx.send(embed=embed)


    @commands.hybrid_command(description='Search github.', usage="github [search]")
    
    
    async def github(self, ctx, *, search_query):
        json = requests.get(
            f"https://api.github.com/search/repositories?q={search_query}"
        ).json()

        if json["total_count"] == 0:
            await ctx.send("No matching repositories found")
        else:
            await ctx.send(
                f"First result for '{search_query}':\n{json['items'][0]['html_url']}")


    @commands.hybrid_command(description='get info about voice channel.', help="get info about voice channel",usage="Vcinfo <VoiceChannel>")
    
    
    async def vcinfo(self, ctx: Context, vc: discord.VoiceChannel):
      e = discord.Embed(title='VC Information', color=0x977FD7)
      e.add_field(name='VC name', value=vc.name, inline=False)
      e.add_field(name='VC ID', value=vc.id, inline=False)
      e.add_field(name='VC bitrate', value=vc.bitrate, inline=False)
      e.add_field(name='Mention', value=vc.mention, inline=False)
      e.add_field(name='Category name', value=vc.category.name, inline=False)
      #e.add_field(name='VC Created', value=format_date(vc.created_at), inline=False)
      await ctx.send(embed=e)




    @commands.hybrid_command(description='shows information a about channel.', help="shows info about channel",aliases=['channeli', 'cinfo', 'ci'], pass_context=True, no_pm=True,usage="Channelinfo [channel]")
    
    
    async def channelinfo(self, ctx, *, channel: int = None):
        """Shows channel information"""
        if not channel:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(channel)
        data = discord.Embed()
        if hasattr(channel, 'mention'):
            data.description = "**Information about Channel:** " + channel.mention
        if hasattr(channel, 'changed_roles'):
            if len(channel.changed_roles) > 0:
                data.color = 0x977FD7 if channel.changed_roles[0].permissions.read_messages else 0x977FD7
        if isinstance(channel, discord.TextChannel): 
            _type = "Text"
        elif isinstance(channel, discord.VoiceChannel): 
            _type = "Voice"
        else: 
            _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id, inline=False)
        if hasattr(channel, 'position'):
            data.add_field(name="Position", value=channel.position)
        if isinstance(channel, discord.VoiceChannel):
            if channel.user_limit != 0:
                data.add_field(name="User Number", value="{}/{}".format(len(channel.voice_members), channel.user_limit))
            else:
                data.add_field(name="User Number", value="{}".format(len(channel.voice_members)))
            userlist = [r.display_name for r in channel.members]
            if not userlist:
                userlist = "None"
            else:
                userlist = "\n".join(userlist)
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif isinstance(channel, discord.TextChannel):
            try:
                pins = await channel.pins()
                data.add_field(name="Pins", value=len(pins), inline=True)
            except discord.Forbidden:
                pass
            data.add_field(name="Members", value="%s"%len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            hidden = []
            allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages is True:
                    if role.name != "@everyone":
                        allowed.append(role.mention)
                elif role.permissions.read_messages is False:
                    if role.name != "@everyone":
                        hidden.append(role.mention)
            if len(allowed) > 0: 
                data.add_field(name='Allowed Roles ({})'.format(len(allowed)), value=', '.join(allowed), inline=False)
            if len(hidden) > 0:
                data.add_field(name='Restricted Roles ({})'.format(len(hidden)), value=', '.join(hidden), inline=False)
        if channel.created_at:
            data.set_footer(text=("Created on {} ({} days ago)".format(channel.created_at.strftime("%d %b %Y %H:%M"), (ctx.message.created_at - channel.created_at).days)))
        await ctx.send(embed=data)



    @commands.hybrid_command(description='Creates a note for you', cooldown_after_parsing=True, help="Creates a note for you",usage="Note <message>")
    @cooldown(1, 10, BucketType.user)
    
    
    async def note(self, ctx, *, message: str):
      author_id = ctx.author.id
      if len(message) > 50:
          await ctx.send("Message cannot be greater than 50 characters.")
      else:
          notes = collection.find({"_id": author_id})
          if notes.count() >= 3:
              await ctx.send("You can only save up to 3 notes.")
          else:
              note = {"_id": author_id, "note": message}
              collection.insert_one(note)
              await ctx.send(f"Note created: {message}")

    @commands.hybrid_command(description='Shows your note', help="Shows your note",usage="Notes")
    
    
    async def notes(self, ctx):
      author_id = ctx.author.id
      notes = collection.find({"_id": author_id})
      embed = discord.Embed(title=f"{ctx.author.name}'s Notes", color=0x977FD7)
      for note in notes:
          embed.add_field(name="Note", value=note["note"], inline=False)
      await ctx.send(embed=embed)

    @commands.hybrid_command(description='Delete the notes', help="Delete the notes , it's a good practice",usage="Trashnotes")
    
    
    async def trashnotes(self, ctx):
      author_id = ctx.author.id
      notes = collection.find({"_id": author_id})
      if notes.count() == 0:
          await ctx.send("You have no recorded notes.")
      else:
          collection.delete_many({"_id": author_id})
          await ctx.send("All your notes have been deleted.")


    @commands.hybrid_command(description='Shows your or a user\'s profile card with badges.', name="badges", help="Check what premium badges a user have.", aliases=["badge", "pr", "profile"],usage="badges [user]")
    
    
    async def _badges(self, ctx, user: Optional[discord.User] = None):
      mem = user or ctx.author
      badges = getbadges(mem.id)
      
      await ctx.defer()
      profile_image_file = await self._create_badge_profile(mem, badges)
      await ctx.send(file=profile_image_file)


    def parse_google_card(self, node):
        if node is None or type(node) is int:
            return None

        e = discord.Embed(colour=0x0057e7)

        # check if it's a calculator card:
        calculator = node.find(".//table/tr/td/span[@class='nobr']/h2[@class='r']")
        if calculator is not None:
            e.title = 'Calculator'
            e.description = ''.join(calculator.itertext())
            return e

        parent = node.getparent()

        # check for unit conversion card
        unit = parent.find(".//ol//div[@class='_Tsb']")
        if unit is not None:
            e.title = 'Unit Conversion'
            e.description = ''.join(''.join(n.itertext()) for n in unit)
            return e

        # check for currency conversion card
        currency = parent.find(".//ol/table[@class='std _tLi']/tr/td/h2")
        if currency is not None:
            e.title = 'Currency Conversion'
            e.description = ''.join(currency.itertext())
            return e

        # check for release date card
        release = parent.find(".//div[@id='_vBb']")
        if release is not None:
            try:
                e.description = ''.join(release[0].itertext()).strip()
                e.title = ''.join(release[1].itertext()).strip()
                return e
            except:
                return None

        # check for definition card
        words = parent.find(".//ol/div[@class='g']/div/h3[@class='r']/div")
        if words is not None:
            try:
                definition_info = words.getparent().getparent()[1]
            except:
                pass
            else:
                try:
                    e.title = words[0].text
                    e.description = words[1].text
                except:
                    return None
                for row in definition_info:
                    if len(row.attrib) != 0:
                        break
                    try:
                        data = row[0]
                        lexical_category = data[0].text
                        body = []
                        for index, definition in enumerate(data[1], 1):
                            body.append('%s. %s' % (index, definition.text))
                        e.add_field(name=lexical_category, value='\n'.join(body), inline=False)
                    except:
                        continue
                return e

        # check for translate card
        words = parent.find(".//ol/div[@class='g']/div/table/tr/td/h3[@class='r']")
        if words is not None:
            e.title = 'Google Translate'
            e.add_field(name='Input', value=words[0].text,  inline=True)
            e.add_field(name='Out', value=words[1].text,  inline=True)
            return e

        # check for "time in" card
        time_in = parent.find(".//ol//div[@class='_Tsb _HOb _Qeb']")
        if time_in is not None:
            try:
                time_place = ''.join(time_in.find("span[@class='_HOb _Qeb']").itertext()).strip()
                the_time = ''.join(time_in.find("div[@class='_rkc _Peb']").itertext()).strip()
                the_date = ''.join(time_in.find("div[@class='_HOb _Qeb']").itertext()).strip()
            except:
                return None
            else:
                e.title = time_place
                e.description = '%s\n%s' % (the_time, the_date)
                return e

        weather = parent.find(".//ol//div[@class='e']")
        if weather is None:
            return None

        location = weather.find('h3')
        if location is None:
            return None

        e.title = ''.join(location.itertext())

        table = weather.find('table')
        if table is None:
            return None

        try:
            tr = table[0]
            img = tr[0].find('img')
            category = img.get('alt')
            image = 'https:' + img.get('src')
            temperature = tr[1].xpath("./span[@class='wob_t']//text()")[0]
        except:
            return None
        else:
            e.set_thumbnail(url=image)
            e.description = '*%s*' % category
            e.add_field(name='Temperature', value=temperature)

        try:
            wind = ''.join(table[3].itertext()).replace('Wind: ', '')
        except:
            return None
        else:
            e.add_field(name='Wind', value=wind)

        try:
            humidity = ''.join(table[4][0].itertext()).replace('Humidity: ', '')
        except:
            return None
        else:
            e.add_field(name='Humidity', value=humidity)

        return e





    @commands.hybrid_command(pass_context=True)
    async def g(self, ctx, *, query):
        """Google web search. Ex: [p]g what is discordapp?"""
        if not embed_perms(ctx.message):
            config = load_optional_config()
            async with self.bot.session.get("https://www.googleapis.com/customsearch/v1?q=" + urllib.parse.quote_plus(query) + "&start=1" + "&key=" + config['google_api_key'] + "&cx=" + config['custom_search_engine']) as resp:
                result = json.loads(await resp.text())
            return await ctx.send(result['items'][0]['link'])

        try:
            entries, root = await get_google_entries(query, session=self.bot.session)
            card_node = root.find(".//div[@id='topstuff']")
            card = self.parse_google_card(card_node)
        except RuntimeError as e:
            await ctx.send(str(e))
        else:
            if card:
                value = '\n'.join(entries[:2])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await ctx.send(embed=card)
            if not entries:
                return await ctx.send('No results.')
            next_two = entries[1:3]
            if next_two:
                formatted = '\n'.join(map(lambda x: '<%s>' % x, next_two))
                msg = '{}\n\n**See also:**\n{}'.format(entries[0], formatted)
            else:
                msg = entries[0]
            await ctx.send(msg)
            
def setup(bot):
    bot.add_cog(Extra(bot))