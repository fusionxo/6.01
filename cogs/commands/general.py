import discord
from discord.ext import commands
from afks import afks
from discord.utils import get
import psutil
from psutil import Process, virtual_memory
from typing import Union, Optional
import time
import datetime
import asyncio
import random
import requests
from utils.checks import global_check
import aiohttp
from faker import Faker
import re
from discord.ext.commands.errors import BadArgument
from discord.colour import Color
import hashlib
from core import *
from utils.Tools import *
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
from datetime import datetime, timedelta
import string


password = ['1838812`', '382131847', '231838924', '218318371', '3145413', '43791', '471747183813474', '123747019', '312312318']

fake = Faker()

def generate_strong_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def generate_access_key():
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for _ in range(3)) + random.choice(string.digits)

def progress_bar(progress):
    total_blocks = 10
    filled_blocks = int(progress / 10)
    empty_blocks = total_blocks - filled_blocks
    return '███ ' * filled_blocks + '▯ ' * empty_blocks

def remove(afk):
    if "[AFK]" in afk.split():
        return " ".join(afk.split()[1:])
    else:
        return afk

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aiohttp = aiohttp.ClientSession()
        self._URL_REGEX = r'(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s])'
        self.tasks = []
        self.dump_tasks = []
        self.sniped = {}
        self.afk = {}
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        

    def help_custom(self):
		      emoji = '<:search:1088438737727406142>'
		      label = "General"
		      description = "Shows the general useful commands."
		      return emoji, label, description

    @commands.group()
    async def __General__(self, ctx: commands.Context):
        """`afk` , `avatar` , `banner` , `servericon` , `membercount` , `poll` , `hack` , `token` , `users` , `italicize` , `strike` , `quote` , `code` , `bold` , `censor` , `underline` , `gender` , `wizz` , `pikachu` , `shorten` , `urban` , `rickroll` , `hash` , `snipe` , `roleall`"""

 
######################


    @commands.hybrid_command(description="Shows your/someone's avatar", usage="Avatar [member]",
        name='avatar',
        aliases=['av', 'ab', 'ac', 'ah', 'pfp', 'avi', 'ico'],
        help="""Wanna steal someone's avatar here you go
Aliases"""
    )
    
    
    async def avatar(self, ctx, user: discord.Member = None):
        try:
          if user == None:
             user = ctx.author
          else:  
             user = await self.bot.fetch_user(user.id)
        except AttributeError:
            user = ctx.author
        webp = user.avatar.replace(format='webp')
        jpg = user.avatar.replace(format='jpg')
        png = user.avatar.replace(format='png')
        avemb = discord.Embed(
            color=0x977FD7,
            title=f"{user}'s Avatar",description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
            if not user.avatar.is_animated()
            else f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({user.avatar.replace(format='gif')})"
        )
        avemb.set_image(url=user.avatar.url)
        avemb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=avemb)


    @commands.group(name="banner")
    async def banner(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @banner.command(name="server")
    async def server(self, ctx):
        if not ctx.guild.banner:
            await ctx.reply("This server does not have a banner.")
        else:
            webp = ctx.guild.banner.replace(format='webp')
            jpg = ctx.guild.banner.replace(format='jpg')
            png = ctx.guild.banner.replace(format='png')
            embed = discord.Embed(
                color=0x2f3136,
                description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
                if not ctx.guild.banner.is_animated() else
                f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({ctx.guild.banner.replace(format='gif')})"
            )
            embed.set_image(url=ctx.guild.banner)
            embed.set_author(name=ctx.guild.name,
                             icon_url=ctx.guild.icon.url
                             if ctx.guild.icon else ctx.guild.default_icon.url)
            embed.set_footer(
                text=f"Requested By {ctx.author}",
                icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=embed)

    
    
    @banner.command(name="user")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def _user(self,
                    ctx,
                    member: Optional[Union[discord.Member,
                                           discord.User]] = None):
        if member == None or member == "":
            member = ctx.author
        bannerUser = await self.bot.fetch_user(member.id)
        if not bannerUser.banner:
            await ctx.reply("{} does not have a banner.".format(member))
        else:
            webp = bannerUser.banner.replace(format='webp')
            jpg = bannerUser.banner.replace(format='jpg')
            png = bannerUser.banner.replace(format='png')
            embed = discord.Embed(
                color=0x2f3136,
                description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
                if not bannerUser.banner.is_animated() else
                f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({bannerUser.banner.replace(format='gif')})"
            )
            embed.set_author(name=f"{member}",
                             icon_url=member.avatar.url
                             if member.avatar else member.default_avatar.url)
            embed.set_image(url=bannerUser.banner)
            embed.set_footer(
                text=f"Requested By {ctx.author}",
                icon_url=ctx.author.avatar.url
                if ctx.author.avatar else ctx.author.default_avatar.url)

            await ctx.send(embed=embed)
            
            
            
    @commands.hybrid_command(description="Shows the server icon.", help="Shows the server icon",usage="Servericon")
    
    
    async def servericon(self, ctx):
        server = ctx.guild
        webp = server.icon.replace(format='webp')
        jpg = server.icon.replace(format='jpg')
        png = server.icon.replace(format='png')
        avemb = discord.Embed(
            color=0x977FD7,
            title=f"{server}'s Icon",description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
            if not server.icon.is_animated()
            else f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({server.icon.replace(format='gif')})"
        )
        avemb.set_image(url=server.icon.url)
        avemb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=avemb)


    @commands.hybrid_command()
    
    async def vote(self, ctx):
        embed = discord.Embed(title="Vote for Us", color=0x977FD7)
        embed.add_field(name="Vote Us", value="Click the buttons below to support us! 🎈🏆", inline=False)

        button1 = Button(label="Vote Us", emoji="<:Invitelink:1040661606809473046>", url="https://fusionxo.com/luka/vote")
        button2 = Button(label="Support Server", emoji="<:Invitelink:1040661606809473046>", url="https://fusionxo.com/luka/support")
        button3 = Button(label="Invite Luka", emoji="<:invite:1095942167593234484>", url="https://fusionxo.com/luka/invite")

        view = View()
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)

        await ctx.send(embed=embed, view=view)        
        
        

    @commands.hybrid_command(description="Shows the member count of the server.", help="Get total member count and status distribution of the server", usage="membercount", aliases=["mc"])
    
    
    async def membercount(self, ctx):
        online = 0
        offline = 0
        dnd = 0
        idle = 0
        streaming = 0
        bots = 0
        
        for member in ctx.guild.members:
            if member.bot:
                bots += 1
            else:
                if member.status == discord.Status.online:
                    online += 1
                elif member.status == discord.Status.offline:
                    offline += 1
                elif member.status == discord.Status.dnd:
                    dnd += 1
                elif member.status == discord.Status.idle:
                    idle += 1
                if member.activity and member.activity.type == discord.ActivityType.streaming:
                    streaming += 1

        total = len(ctx.guild.members)
        total_online = online + dnd + idle + streaming
        bot_percentage = round((bots / total) * 100)
        human_percentage = round((1 - (bots / total)) * 100)

        embed = discord.Embed(
            title=f"{ctx.guild.name} Member Information",
            description=f"```👥 Total Members: {total} ({bot_percentage}% bots, {human_percentage}% humans)```\n\n<:dot:1088106350904610827> **Status Distribution**",
            color=0x977FD7
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        else:
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
            embed.set_footer(text=ctx.guild.name)

        embed.add_field(name="<:online:1044193241639166012> Online", value=f"```{online}```", inline=True)
        embed.add_field(name="<:2179offlinestatus:1044193150664708206> Offline", value=f"```{offline}```", inline=True)
        embed.add_field(name="<:5505idlestatus:1044193198798544986> Idle", value=f"```{idle}```", inline=True)
        embed.add_field(name="<:5163dndstatus:1044193104154083368> Do Not Disturb", value=f"```{dnd}```", inline=True)
        embed.add_field(name="<:69814streaming:1273527545987465258> Streaming", value=f"```{streaming}```", inline=True)
        embed.add_field(name="<:Bot:1042445512479092776> Bots", value=f"```{bots}```", inline=True)
        embed.add_field(name="<:user:1087776942679412856> Total Members", value=f"```{total}```", inline=True)
        embed.add_field(name="<:user:1087776942679412856> Total Online Members", value=f"```{total_online}```", inline=True)

        await ctx.send(embed=embed)



    @commands.hybrid_command(description="Create a poll message.", usage="Poll [message]")
    
    
    async def poll(self, ctx,*,message):
      emp = discord.Embed(title=f"**Poll!**", description=f"{message}", color =  0x977FD7)
      msg = await ctx.send(embed=emp)
      await msg.add_reaction("👍")
      await msg.add_reaction("👎")


    @commands.hybrid_command(help="hack someone's discord account", usage="Hack <member>")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def hack(self, ctx, member: discord.Member):
        steps = [
            f"Injecting trojan into ID: {member.id}",
            f"Getting access key from discriminator: {generate_access_key()}",
            f"Tracing IP address: {fake.ipv4()}",
            "Exploiting vulnerabilities...",
            f"Latest incognito search: {fake.sentence(nb_words=4)}",
            "Passwords acquired. Accessing accounts...",
            "Bypassing security: 2FA, security questions, reCAPTCHA...",
            "Extracting data...",
            "Selling data on Dark Web...",
            "Hack traces erased."
        ]

        red_steps = {0, 1, 2, 4, 6, 8}
        green_steps = {3, 5, 7, 9}

        progress_message = await ctx.send("Loading....")
        await asyncio.sleep(1)

        for i, step in enumerate(steps):
            status = (i + 1) * 10
            progress = progress_bar(status)
            if i in red_steps:
                message_content = f"```diff\n- Status: {status}%\n{progress}\n-{step}\n```"
            else:
                message_content = f"```diff\n+ Status: {status}%\n{progress}\n-{step}\n```"
            await progress_message.edit(content=message_content)
            await asyncio.sleep(1)
        
        # Generate fake data
        random_pass = generate_strong_password(random.randint(12, 18))
        email_local = member.display_name.replace(" ", "").lower()
        email = fake.free_email()
        ip_address = fake.ipv4()
        location = fake.city()
        bank_account = fake.bban()  # Basic Bank Account Number
        bank_name = fake.company()
        cc_number = fake.credit_card_number()
        salary = f"${random.randint(30000, 120000)}"
        address = fake.address().replace("\n", ", ")
        gender = fake.random_element(elements=('Male', 'Female', 'Non-Binary'))
        age = fake.random_int(min=18, max=90)
        religion = fake.random_element(elements=('Christianity', 'Islam', 'Hinduism', 'Buddhism', 'Atheism', 'Other'))

        embed = discord.Embed(
            title=f"**Hacking Complete**",
            description=f"Successfully hacked @{member.display_name}!",
            color=0x977FD7
        )
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="E-Mail", value=email, inline=True)
        embed.add_field(name="Password", value=random_pass, inline=True)
        embed.add_field(name="IP Address", value=ip_address, inline=True)
        embed.add_field(name="Location", value=location, inline=True)
        embed.add_field(name="Bank Account", value=bank_account, inline=True)
        embed.add_field(name="Bank Name", value=bank_name, inline=True)
        embed.add_field(name="Credit Card Number", value=cc_number, inline=True)
        embed.add_field(name="Salary", value=salary, inline=True)
        embed.add_field(name="Address", value=address, inline=True)
        embed.add_field(name="Gender", value=gender, inline=True)
        embed.add_field(name="Age", value=age, inline=True)
        embed.add_field(name="Religion", value=religion, inline=True)

        # Send final embed after the progress simulation
        final_message_content = f"```diff\n+ Status: 100%\n{progress_bar(100)}\n-Hacking complete\n```"
        await progress_message.edit(content=final_message_content)
        await asyncio.sleep(3)
        await progress_message.delete()
        await ctx.send(embed=embed)


    @commands.hybrid_command(description="Create a random token (fake fun only)", usage="Token <member>")
    
    
    async def token(self, ctx, user: discord.Member = None):
        list = [
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
            "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "_"
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
            'ñ', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0',
            '1', '2', '3', '4', '5', '6', '7', '8', '9'
        ]
        token = random.choices(list, k=59)
        if user is None:
            user = ctx.author
            await ctx.send(user.mention + "'s token is " + ''.join(token))
        else:
            await ctx.send(user.mention + "'s token is " + "".join(token))




    @commands.hybrid_command(description="Check users of Luka.", help="check users of Luka .")
    
    
    async def users(self, ctx):
      embed = discord.Embed(
        title=f"**Users:**", 
        description=f"**{len(set(self.bot.get_all_members()))} Users Of Luka**",
        color = 0x977FD7
      )
      await ctx.send(embed=embed)

    @commands.hybrid_command(help="italicize the given text",usage="Italicize <message>")
    @commands.cooldown(1, 15, commands.BucketType.user)    
    
    
    async def italicize(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.message.delete()
        await ctx.send('*' + message + '*')

    @commands.hybrid_command(help="strike the given text",usage="Strike <message>")
    @commands.cooldown(1, 15, commands.BucketType.user) 
    
    
    async def strike(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.message.delete()
        await ctx.send('~~' + message + '~~')

    @commands.hybrid_command(help="quote the given text",usage="Quote <message>")
    @commands.cooldown(1, 15, commands.BucketType.user)    
    
    
    async def quote(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.message.delete()
        await ctx.send('> ' + message)

    @commands.hybrid_command(help="code the given text",usage="Code <message>")
    @commands.cooldown(1, 15, commands.BucketType.user)
    
    
    async def code(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.send('`' + message + '`')

    @commands.hybrid_command(help="bold the given text",usage="Bold <message>")
    @commands.cooldown(1, 15, commands.BucketType.user)
    
    
    async def bold(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.send('**' + message + '**')

    @commands.hybrid_command(help="censor the given text",usage="Censor <message>")
    @commands.cooldown(1, 15, commands.BucketType.user)
    
    
    async def censor(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.send('||' + message + '||')

    @commands.hybrid_command(help="underline the given text",usage="Underline <message>")
    @commands.cooldown(1, 15, commands.BucketType.user)
    
    
    async def underline(self, ctx, *, message):
        message = message.replace('@', '@\u200b')  # Prevent user mentions
        await ctx.send('__' + message + '__')



    @commands.hybrid_command(usage="Gender <member>")
    
    
    async def gender(self, ctx, member: discord.Member):
      embed = discord.Embed(
        description=f"{member.mention}'s gender is None",
        color = discord.Colour.default()
      )
      await ctx.send(embed=embed)



    @commands.hybrid_command(usage="Wizz")
    
    
    async def wizz(self, ctx):
      message6 = await ctx.send(f"`Wizzing {ctx.guild.name}, will take 22 seconds to complete`")
      message5 = await ctx.send(f"`Deleting {len(ctx.guild.roles)} Roles...`")
      message4 = await ctx.send(f"`Deleting {len(ctx.guild.channels)} Channels...`")
      message3 = await ctx.send(f"`Deleting Webhooks...`")
      message2 = await ctx.send(f"`Deleting emojis`")
      message1 = await ctx.send(f"`Installing Ban Wave..`")
      await message6.delete()
      await message5.delete()
      await message4.delete()
      await message3.delete()
      await message2.delete()
      await message1.delete()
      embed=discord.Embed(title="Luka", description=f"**Successfully Wizzed {ctx.guild.name}**", color=0x977FD7,timestamp=ctx.message.created_at)
      await ctx.reply(embed=embed)
    @commands.hybrid_command(help="Gives a gif of pikachu",usage="Pikachu")
    
    
    async def pikachu(self, ctx):
      response = requests.get('https://some-random-api.ml/img/pikachu')
      data = response.json()
      embed = discord.Embed(
        title = 'Pikachu',
        description = 'Here is a gif of Pikachu.',
        color = 0x977FD7
      )
      embed.set_image(url=data['link'])
      embed.set_footer(name="Made with 💖 by LUKA#5191", icon_url="")
      await ctx.channel.trigger_typing()
      await ctx.send(embed=embed)
    @commands.hybrid_command(description="Shortens specified url with 3 different url shorteners.", help="Shortens specified url with 3 different url shorteners",usage="Shorten <url>")
    
    
    async def shorten(self, ctx: commands.Context, *, url: str):
        async with ctx.typing():
            embed = discord.Embed(
                title="URL Shortener ({})".format(url))
            async with self.aiohttp.get("https://api.shrtco.de/v2/shorten?url={}".format(url)) as shrtco:
                async with self.aiohttp.get("https://clck.ru/--?url={}".format(url)) as clck:
                    async with self.aiohttp.get("http://tinyurl.com/api-create.php?url={}".format(url)) as tiny:
                        parse = await shrtco.json()
                        embed.add_field(name="Shortened URL (9qr.de)", value=parse["result"]["full_short_link2"], inline=False)
                        embed.add_field(name="Shortened URL (clck.ru)", value=await clck.text(), inline=False)
                        embed.add_field(name="Shortened URL (tinyurl.com)", value=await tiny.text(), inline=False)
        await ctx.reply(embed=embed, mention_author=True)
        
        
    @commands.hybrid_command(description="Searches for specified phrase on urbandictionary.com", help="Don't know meaning of some words don't worry this will help",usage="Urban <phrase>")
    
    
    async def urban(self, ctx, *, phrase):
        async with self.aiohttp.get("http://api.urbandictionary.com/v0/define?term={}".format(phrase)) as urb:
            urban = await urb.json()
            try:
                embed = discord.Embed(
                    title=f"Term - \"{phrase}\"", color=0x977FD7)
                embed.add_field(name="Definition",
                                value=urban['list'][0]['definition'].replace('[', '').replace(']', ''))
                embed.add_field(name="Example", value=urban['list'][0]['example'].replace(
                    '[', '').replace(']', ''))
                temp = await ctx.reply(embed=embed, mention_author=True)
                await asyncio.sleep(15)
                await temp.delete()
                await ctx.message.delete()
            except:
                pass
    @commands.hybrid_command(name="rickroll",help="Detects if provided url is a rick-roll",usage="Rickroll <url>")
    
    
    async def _rr(self, ctx: commands.Context, *, url: str):
        if not re.match(self._URL_REGEX, url):
            raise BadArgument("Invalid URL")

        phrases = ["rickroll", "rick roll", "rick astley", "never gonna give you up"]
        source = str(await (await self.aiohttp.get(url, allow_redirects=True)).content.read()).lower()
        rickRoll = bool(
            (re.findall('|'.join(phrases), source, re.MULTILINE | re.IGNORECASE)))
        await ctx.reply(embed=discord.Embed(
            title="Rick Roll {} in webpage".format(
                "was found" if rickRoll is True else "was not found"),
            color=Color.red() if rickRoll is True else Color.green(),
        ), mention_author=True)

    @commands.hybrid_command(name="hash",help="Hashes provided text with provided algorithm")
    
    
    async def _hash(self, ctx, algorithm: str, *, message):
        algos: dict[str, str] = {
            "md5": hashlib.md5(bytes(message.encode("utf-8"))).hexdigest(),
            "sha1": hashlib.sha1(bytes(message.encode("utf-8"))).hexdigest(),
            "sha224": hashlib.sha224(bytes(message.encode("utf-8"))).hexdigest(),
            "sha3_224": hashlib.sha3_224(bytes(message.encode("utf-8"))).hexdigest(),
            "sha256": hashlib.sha256(bytes(message.encode("utf-8"))).hexdigest(),
            "sha3_256": hashlib.sha3_256(bytes(message.encode("utf-8"))).hexdigest(),
            "sha384": hashlib.sha384(bytes(message.encode("utf-8"))).hexdigest(),
            "sha3_384": hashlib.sha3_384(bytes(message.encode("utf-8"))).hexdigest(),
            "sha512": hashlib.sha512(bytes(message.encode("utf-8"))).hexdigest(),
            "sha3_512": hashlib.sha3_512(bytes(message.encode("utf-8"))).hexdigest(),
            "blake2b": hashlib.blake2b(bytes(message.encode("utf-8"))).hexdigest(),
            "blake2s": hashlib.blake2s(bytes(message.encode("utf-8"))).hexdigest()
        }
        embed = discord.Embed(color=Color.green(),
                              title="Hashed \"{}\"".format(message))
        if algorithm.lower() not in list(algos.keys()):
            for algo in list(algos.keys()):
                hashValue = algos[algo]
                embed.add_field(name=algo, value="```{}```".format(hashValue))
        else:
            embed.add_field(name=algorithm, value="```{}```".format(
                algos[algorithm.lower()]), inline=False)
        await ctx.reply(embed=embed, mention_author=True)



    @commands.Cog.listener()
    async def on_message_delete(self, message): 
        if message.guild == None: 
            return
        if message.author.bot: 
            return
        if not message.content: 
            return 
        self.sniped[message.channel.id] = message
         #@commands.hybrid_command(aliases=['sb'])
    @commands.guild_only()
    @commands.has_permissions(view_audit_log=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    
    
    @commands.group(name="snipe", help="Snipes the most recent deleted message", usage="snipe")
    async def snipe(self, ctx):
        message = self.sniped.get(ctx.channel.id)
        if message == None:
            return await ctx.send(embed=discord.Embed(title="Snipe", description="There are no recently deleted messages", color=0x977FD7))
        embed = discord.Embed(title="Sniped Message sent by %s" % (message.author), description=message.content, color=0x977FD7, timestamp=message.created_at)
        await ctx.send(embed=embed)

 

    @commands.hybrid_command( help="Gives a role to all members", usage="roleall <role>", aliases=["role-all", "rall"])
    
    
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def roleall(self, ctx, *, role: discord.Role):
        if ctx.guild.id in self.tasks:
            return await ctx.send(embed=discord.Embed(title="roleall", description="There is a roleall task already running, please wait for it to finish", color=0x977FD7))
        await ctx.message.add_reaction("<:check:1087776909246607360>")
        num = 0
        failed = 0
        for user in list(ctx.guild.members):
            try:
                await user.add_roles(role)
                num += 1
            except Exception:
                failed += 1
        await ctx.send(embed=discord.Embed(title="roleall", description="<:check:1087776909246607360> | Successfully added **`%s`** to **`%s`** users, failed to add it to **`%s`** users" % (role.name, num, failed), color=0x977FD7))



    @commands.group(name="jail", help="Jails a user", usage="jail <user>")
    
    
    @commands.has_permissions(administrator=True)
    async def jail(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="jailed")
        if not role:
            await ctx.guild.create_role(name="jailed")

        jail = discord.utils.get(ctx.guild.text_channels, name="jail")
        if not jail:
            try:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                }            
                jail = await ctx.guild.create_text_channel("jail", overwrites=overwrites)
                await ctx.send(embed=discord.Embed(title="jail", description="Your server has no jail channel, I created one for you %s" % (jail.mention), color=0x977FD7))
            except discord.Forbidden:
                return await ctx.send(embed=discord.Embed(title="jail", help="Please give me permissions, I am unable to create the jailed channel", color=0x977FD7))

        for channel in ctx.guild.channels:
            if channel.name == "jail":
                perms = channel.overwrites_for(member)
                perms.send_messages = True
                perms.read_messages = True
                await channel.set_permissions(member, overwrite=perms)
            else:
                perms = channel.overwrites_for(member)
                perms.send_messages = False
                perms.read_messages = False
                perms.view_channel = False
                await channel.set_permissions(member, overwrite=perms)

        role = discord.utils.get(ctx.guild.roles, name="jailed")
        await member.add_roles(role)

        await jail.send(content=member.mention, embed=discord.Embed(title="jail", description="You have been put in jail please live out your jail sentence until the court lets you free. <:jail:1063560071201693838>", color=0x977FD7))
        await ctx.send(embed=discord.Embed(title="jail", description="Successfully jailed **`%s`**" % (member.name), color=0x977FD7))
        await member.send(embed=discord.Embed(title="jail", description="You have been jailed in **`%s`** by **`%s`**" % (ctx.guild.name, ctx.author.name), color=0x977FD7))

    @commands.group(name="unjail", help="Unjails a user", usage="unjail <user>",  aliases=["free"])
    
    
    @commands.has_permissions(administrator=True)
    async def unjail(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="jailed")
        for channel in ctx.guild.channels:
            if channel.name == "jail":
                perms = channel.overwrites_for(member)
                perms.send_messages = None
                perms.read_messages = None
                await channel.set_permissions(member, overwrite=perms)
            else:
                perms = channel.overwrites_for(member)
                perms.send_messages = None
                perms.read_messages = None
                perms.view_channel = None
                await channel.set_permissions(member, overwrite=perms)

        await member.remove_roles(role)
        await ctx.send(embed=discord.Embed(title="unjail", description="Successfully unjailed **`%s`**" % (member.name), color=self.color))
        await member.send(embed=discord.Embed(title="unjail", description="you have been unjailed in **`%s`** by **`%s`**" % (ctx.guild.name, ctx.author.name), color=0x977FD7))

    @commands.group(name="cleanup", help="deletes the bots messages", aliases=["purgebots"], usage="cleanup <amount>")
    
    
    @commands.has_permissions(administrator=True)
    async def cleanup(self, ctx, amount: int):
        msg = await ctx.send("cleaning...")
        async for message in ctx.message.channel.history(limit=amount).filter(lambda m: m.author == self.bot.user).map(lambda m: m):
            try:
                if message.id == msg.id:
                    pass
                else:
                    await message.delete()
            except:
                pass
        await msg.edit(content="cleaned up 👍")
        
    @commands.command(name='specs')
    async def send_specs(self, ctx):
        ram = psutil.virtual_memory().total
        storage = psutil.disk_usage('/').total
        cpu = f"{psutil.cpu_percent(interval=1)}%"

        embed = discord.Embed(title='Device Specifications', color=0x00ff00)
        embed.add_field(name='RAM', value=f"{ram / (1024 ** 3):.2f} GB", inline=False)
        embed.add_field(name='Storage', value=f"{storage / (1024 ** 3):.2f} GB", inline=False)
        embed.add_field(name='CPU Usage', value=cpu, inline=False)

        await ctx.send(embed=embed)
        
        

    @commands.command(name="easteregg", aliases=["easter", "egg", "update"])
    
    
    async def eeg(self, ctx):
        message = "**Who Knows ;)**"
        await ctx.send(message)
        
def setup(bot):
    bot.add_cog(General(bot))