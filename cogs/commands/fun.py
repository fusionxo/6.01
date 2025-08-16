############MODULES#############
import discord
import requests
import aiohttp
import datetime
import random
import pymongo
from discord.ext import commands, tasks
from random import randint
from time import sleep
from utils.Tools import *
from core import Cog, Luka, Context
from PIL import Image, ImageDraw, ImageFont
from discord import Embed
import asyncio
from pymongo import MongoClient
import datetime
from datetime import datetime, timedelta
from utils.checks import global_check

#14
#snipe | editsnipe | tickle | kiss | hug | slap | pat | feed | pet | howgay | slots | penis | meme | cat





def RandomColor(): 
    randcolor = discord.Color(random.randint(0x000000, 0xFFFFFF))
    return randcolor

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roasts = [
                    "Your face is so asymmetrical, it looks like it was drawn by a toddler 🎨😬",
                    "Your jokes are so unfunny, even Siri wouldn't laugh at them 🤖🙄",
                    "Your cooking is so bad, it could be considered a weapon of mass digestion 💣🤢",
                    "Your dancing is so awkward, it looks like you're trying to escape from invisible shackles 💃🙈",
                    "Your singing is so off-key, it could shatter glass 🎤🚫🎶",
                    "Your fashion sense is so outdated, you could be a living time capsule ⌛🤦‍♂️",
                    "Your social skills are so lacking, you could make an introverted hermit cringe 🦀😳",
                    "Your logic is so flawed, even a toddler could outsmart you with a juice box 🧃🧠",
                    "Your sense of direction is so terrible, you could get lost in a one-way street 🚗🤷‍♀️",
                    "Your memory is so bad, you could forget your own birthday while blowing out the candles 🎂🤔",
                    "Your fashion style is so tasteless, it looks like a clearance rack threw up on you 🛍️🤮",
                    "Your dancing skills are so bad, you could make a scarecrow look like a professional ballerina 🌽🩰",
                    "Your wit is so dull, it could make a butter knife seem sharp 🗡️😐",
                    "Your jokes are so cringeworthy, they make dad jokes look like high art 🙈🤦‍♂️",
                    "Your singing voice is so grating, it could make a banshee cover its ears 👻🙉",
                    "Your decision-making skills are so poor, you could struggle to choose between a fork and a spoon 🍴🤷‍♀️",
                    "Your intelligence is so lacking, you make the Three Stooges look like geniuses 🤪🤓",
                    "Your insults are so weak, they couldn't even hurt a marshmallow 🍡😴",
                    "Your sense of humor is so dry, it makes the Sahara Desert look like a water park 🏜️🌊",
                    "Your selfies are so unflattering, they could break a camera lens 📷😱",
                    "Your hair is so greasy, you could fry an egg on it 🍳🤢",
                    "Your teeth are so yellow, you could use them as highlighters 🖍️🤮",
                    "Your breath is so bad, it could knock a skunk out 🦨🤮",
                    "Your clothes are so dirty, you could grow crops on them 🌱🤮",
                    "Your nails are so long, you could use them as a weapon 🔪🤮",
                    "Your ears are so big, you could use them as satellite dishes 📡🤮",
                    "Your nose is so big, you could use it as a sundial 🕰️🤮",
                    "Your feet are so smelly, you could clear a room 💨🤮",
                    "Your voice is so annoying, it could make a dog bark 🐶😡",
                    "Your personality is so bland, you could put a bag of flour to shame 🥙🤮",
                    "Your face is so punchable, I'm surprised you haven't been knocked out yet 👊😵",
                    "Your body is so out of shape, you could be used as a bowling pin 🎳💀",
                    "Your clothes are so ugly, you could be a fashion model 🤮👔",
                    "Your hair is so messy, you could be a bird's nest 🐦🤮",
                    "Your teeth are so crooked, you could be a shark 🦈🤮",
                    "Your IQ is so low, you could be a goldfish 🐟🥴"
        ]
        self.self_roast_message = "Hey, don't be so hard on yourself! Everyone has their flaws. Just remember that you're unique and special in your own way ✨"
        self.cluster = MongoClient("mongodb+srv://hitman25:luka.123@cluster0.xlxhrlj.mongodb.net/")
        self.db = self.cluster["bday"]
        self.collection = self.db["bdaydata"]
        self.check_birthdays.start()

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)


    def help_custom(self):
		      emoji = '<:fun:1088451095795351672>'
		      label = "Fun"
		      description = "Shows the fun commands."
		      return emoji, label, description

    @commands.group()
    async def __Fun__(self, ctx: commands.Context):
        """` tickle` , `kiss` , `hug` , `slap` , `pat` , `feed` , `pet` , `howgay` , `slots` , ` pp` , `meme` , `cat` , `iplookup`, `ship`, `roast`"""
        

    @commands.command()
    @commands.has_permissions(administrator=True)
    
    
    @premium_check()
    async def bday(self, ctx, action, user: discord.Member, *args):
        if action == "set":
            if len(args) != 3:
                await ctx.send("Invalid arguments. Usage: bday set <user> dd mm <chat>")
                return
            day, month, chat = args
            try:
                day = int(day)
                month = int(month)
                chat = await commands.TextChannelConverter().convert(ctx, chat)
            except ValueError:
                await ctx.send("Invalid date or chat. Usage: bday set <user> dd mm <chat>")
                return
            if not (1 <= day <= 31) or not (1 <= month <= 12):
                await ctx.send("Invalid date. Usage: bday set <user> dd mm <chat>")
                return
            self.collection.update_one({"_id": user.id}, {"$set": {"day": day, "month": month, "chat": chat.id}}, upsert=True)
            await ctx.send(f"Birthday set for {user.mention} on {day}/{month} in {chat.mention}")
        elif action == "edit":
            if len(args) != 3:
                await ctx.send("Invalid arguments. Usage: bday edit <user> dd mm <chat>")
                return
            day, month, chat = args
            try:
                day = int(day)
                month = int(month)
                chat = await commands.TextChannelConverter().convert(ctx, chat)
            except ValueError:
                await ctx.send("Invalid date or chat. Usage: bday edit <user> dd mm <chat>")
                return
            if not (1 <= day <= 31) or not (1 <= month <= 12):
                await ctx.send("Invalid date. Usage: bday edit <user> dd mm <chat>")
                return
            if not self.collection.find_one({"_id": user.id}):
                await ctx.send(f"No birthday set for {user.mention}")
                return
            self.collection.update_one({"_id": user.id}, {"$set": {"day": day, "month": month, "chat": chat.id}})
            await ctx.send(f"Birthday edited for {user.mention} on {day}/{month} in {chat.mention}")
        elif action == "delete":
            if len(args) != 0:
                await ctx.send("Invalid arguments. Usage: bday delete <user>")
                return
            if not self.collection.find_one({"_id": user.id}):
                await ctx.send(f"No birthday set for {user.mention}")
                return
            self.collection.delete_one({"_id": user.id})
            await ctx.send(f"Birthday deleted for {user.mention}")
        elif action == "test":
            if len(args) != 0:
                await ctx.send("Invalid arguments. Usage: bday test <user>")
                return
            data = self.collection.find_one({"_id": user.id})
            if not data:
                await ctx.send(f"No birthday set for {user.mention}")
                return
            chat = self.bot.get_channel(data["chat"])
            await chat.send(f"Happy birthday {user.mention}! 🎂🎉🎁")
        else:
            await ctx.send("Invalid action. Available actions: set, edit, delete, test")

    @tasks.loop(minutes=1)
    async def check_birthdays(self):
        now = datetime.utcnow()
        if now.hour == 0 and now.minute == 0:
            tomorrow = (now + timedelta(days=1)).strftime("%d/%m")
            data = self.collection.find({"$expr": {"$and": [{"$eq": [{"$dayOfMonth": "$date"}, tomorrow[:2]]}, {"$eq": [{"$month": "$date"}, tomorrow[3:]]}]}})
            for doc in data:
                user = self.bot.get_user(doc["_id"])
                chat = self.bot.get_channel(doc["chat"])
                if user and chat:
                    await chat.send(f"Happy birthday {user.mention}! 🎂🎉🎁")

    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()
        
       
        
    @commands.command()
    async def roast(self, ctx, user: discord.Member):
        if user == ctx.author:
            await ctx.send(self.self_roast_message)
        else:
            roast = random.choice(self.roasts)
            await ctx.send(f"{user.mention}, {roast}")


    



    @commands.command()
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        if user2 is None:
            user2 = ctx.author

        love_percentage = random.randint(1, 100)

        if love_percentage <= 10:
            love_messages = f":broken_heart: Oh no! {user1.mention} loves {love_percentage}% {user2.mention}. I don't think these two are meant to be."
        elif love_percentage <= 20:
            love_messages = f":thinking: Hmmm... {user1.mention} loves {love_percentage}% {user2.mention}. There might be potential, but they'll need to work on it."
        elif love_percentage <= 30:
            love_messages = f":joy: Hilarious! {user1.mention} loves {love_percentage}% {user2.mention}. These two are the ultimate comedy duo!"
        elif love_percentage <= 40:
            love_messages = f":sparkling_heart: Wow! {user1.mention} loves {love_percentage}% {user2.mention}. Love is definitely in the air!"
        elif love_percentage <= 50:
            love_messages = f":heartbeat: Oh, look at that! {user1.mention} is deeply in love with {user2.mention}. Their hearts beat as one."
        elif love_percentage <= 60:
            love_messages = f":heart_eyes: Aww! {user1.mention} loves {love_percentage}% {user2.mention}. They make a perfect match!"
        elif love_percentage <= 70:
            love_messages = f":tada: Congratulations! {user1.mention} loves {love_percentage}% {user2.mention}. It's a match made in celebration!"
        elif love_percentage <= 80:
            love_messages = f":cupid: Such a sweet connection! {user1.mention} adores {love_percentage}% {user2.mention} with all their heart."
        elif love_percentage <= 90:
            love_messages = f":zap: Electric! {user1.mention} loves {love_percentage}% {user2.mention}. Their chemistry is off the charts!"
        else:
            love_messages = f":star2: A celestial love! {user1.mention} loves {love_percentage}% {user2.mention}. Their love shines brighter than the stars!"

        embed = discord.Embed(title="Luka Ship", description=f"{user1.mention} loves {love_percentage}% {user2.mention}", color=discord.Color(0x977FD7))
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text=f"Ship requested by {ctx.author.display_name}")

        await ctx.send(love_messages, embed=embed)




    @commands.command(name='joke',
                      brief='Let me tell you a joke',
                      description='-> ".joke" - generates a random joke')
    async def joke(self, ctx):
        url = 'https://v2.jokeapi.dev/joke/Any'
        joke = requests.get(url).json()

        if joke['type'] == 'single':
            await ctx.send(joke["joke"])
        elif joke['type'] == 'twopart':
            await ctx.send(joke["setup"])
            await asyncio.sleep(2)
            await ctx.send(joke['delivery'])

    @commands.command(name='fact',
                      brief='Do you know that ...?',
                      description='-> ".fact" - generates a random fact')
    async def fact(self, ctx):
        url = 'https://uselessfacts.jsph.pl/random.json?language=en'
        fact = requests.get(url).json()

        embed = Embed(color=0x2ca5f1)
        embed.add_field(name="Random useless fact", value=fact['text'])

        await ctx.send(embed=embed)


    @commands.command(name='number',
                      brief='What this number means?',
                      description='-> ".number [number]" - generates a random fact about number')
    async def number(self, ctx, number):
        if str(number).isdigit():
            url = 'http://numbersapi.com/'
            result = requests.get(url + str(number)).text
            embed = Embed(color=0x2ca5f1)
        elif '.' in number:
            result = ':no_entry: Only an integer can be passed as argument of number function'
            embed = Embed(color=0x977FD7)
        else:
            result = ':no_entry: Type ".help number" to see how to use number function'
            embed = Embed(color=0x977FD7)

        embed.add_field(name=f"What do you know about {number}?", value=result)
        await ctx.send(embed=embed)

    @number.error
    async def number_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            embed = Embed(color=0x977FD7)
            embed.add_field(name='Warning', value=':warning: You need to pass an integer as argument to this function')
        else:
            embed = Embed(color=0x977FD7)
            embed.add_field(name='Error', value=':no_entry: I\'m unable to find information about this number')

        await ctx.send(embed=embed)

    @commands.command(name='randint',
                      brief='Get a random number',
                      description='-> ".randint" - generates randomly 0 or 1 \n'
                                  '-> ".randint [min] [max]" - generates a random integer from a given interval \n'
                                  '\n Only integers can be passed as arguments')
    async def randint(self, ctx, bottom=None, top=None):
        if str(bottom).replace('-', '').isdigit() and str(top).replace('-', '').isdigit():
            if int(top) < int(bottom):
                result = ':no_entry: The second number should be higher or equal than the first one.'
                embed = Embed(color=0x977FD7)
            else:
                bottom, top = int(bottom), int(top)
                result = str(random.randint(bottom, top))
                embed = Embed(color=0x2ca5f1)
        elif bottom is None and top is None:
            bottom, top = 0, 1
            result = str(random.randint(bottom, top))
            embed = Embed(color=0x2ca5f1)
        elif '.' in bottom or '.' in top:
            result = ':no_entry: Both numbers need to be integers!'
            embed = Embed(color=0x977FD7)
        else:
            result = ':no_entry: Type ".help randint" to see how to use randint function.'
            embed = Embed(color=0x977FD7)

        embed.add_field(name='%s, your random number: ' % ctx.message.author.name, value=result)
        await ctx.send(embed=embed)



    
    @commands.command(help="Tickle mentioned user .",usage="Tickle <member>")
    async def tickle(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/tickle")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),
              description=f"{ctx.author.mention} tickle {user.mention}",color=0x977FD7
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)
    
    @commands.command(help="Kiss mentioned user .",usage="Kiss <member>")
    async def kiss(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/kiss")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),
              description=f"{ctx.author.mention} kisses {user.mention}",color=0x977FD7
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)


                
    @commands.command(help="Hug mentioned user .",usage="Tickle <member>")
    async def hug(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/hug")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),color=0x977FD7,
              description=f"{ctx.author.mention} hugs {user.mention}",
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)

    @commands.command(help="Slap mentioned user .",usage="Slap <member>")
    
    async def slap(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/slap")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),color=0x977FD7,
              description=f"{ctx.author.mention} slapped {user.mention}",
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)

    @commands.command(help="Pat mentioned user .",usage="Pat <member>")
    
    async def pat(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/pat")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),
              description=f"{ctx.author.mention} pats {user.mention}",color=0x977FD7
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")   
            await ctx.send(embed=embed)

    @commands.command(help="Feed mentioned user .",usage="Feed <member>")
    
    async def feed(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/feed")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),
              description=f"{ctx.author.mention} feeds {user.mention}",color=0x977FD7
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)

    @commands.command(usage="Pet <member>")
    
    async def pet(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send(f"`{ctx.author}` you must mention a user to do that!")
        else:
            r = requests.get("https://nekos.life/api/v2/img/pat")
            res = r.json()
            embed = discord.Embed(
              timestamp=datetime.utcnow(),
              description=f"{ctx.author.mention} pets {user.mention}",color=0x977FD7
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)


      
    @commands.command(aliases=['gay'],help="check someone gay percentage",usage="Howgay <person>")
    
    async def howgay(self, ctx, *, person): 
        embed = discord.Embed(color=0x977FD7)
        responses = ['50',
                  '75',
                  '25',
                  '1',
                  '3',
                  '5',
                  '10',
                  '65',
                  '60',
                  '85',
                  '30',
                  '40',
                  '45',
                  '80',
                  '100',
                  '150',
                  '1000']
        embed.description = f'**{person} is {random.choice(responses)}% Gay** :rainbow:'
        embed.set_footer(text=f'How gay are you? - {ctx.author.name}')
        await ctx.send(embed = embed)
    @howgay.error 
    async def howgay_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="*You must mention someone to howgay!*")
            await ctx.send(embed=embed)

    @commands.command()
    
    async def slots(self, ctx):
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        slotmachine = f"[ {a} {b} {c} ]\n{ctx.author.mention}"
        if (a == b == c):
            await ctx.send(embed=discord.Embed(title="Slot machine", description=f"{slotmachine} All Matching! You Won!",color=0x977FD7))
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(embed=discord.Embed(title="Slot machine", description=f"{slotmachine} 2 Matching! You Won!",color=0x977FD7))
        else:
            await ctx.send(embed=discord.Embed(title="Slot machine", description=f"{slotmachine} No Matches! You Lost!",color=0x977FD7))

    @commands.command(aliases = ['dick'],help="Check someone`s dick`s size .",usage="Dick [member]")
    
    async def penis(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        size = random.randint(1, 15)
        dong = ""
        for _i in range(0, size):
            dong += "="
        em = discord.Embed(title=f"**{user}'s** Dick size", description=f"8{dong}D",color=0x977FD7)
        em.set_footer(text=f'whats {user} dick size?')
        await ctx.send(embed=em)

    @commands.command(help="give you a meme",usage="meme")
    
    async def meme(self, ctx):
        embed = discord.Embed(title="""Take some memes""",color=0x977FD7)
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r:
                res = await r.json()
                embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
                embed.set_footer(text=f'Random Meme:')
                #embed.set_footer(text=f'Random Meme:')
                await ctx.send(embed=embed)

    @commands.command(usage="cat")
    
    async def cat(self, ctx):
        embed = discord.Embed(title="""Here's a cat""",color=0x977FD7)
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://aws.random.cat/meow') as r:
                res = await r.json()
                embed.set_image(url=res['file'])
                embed.set_footer(text=f'Random Cats:')
                await ctx.send(embed=embed)

    @commands.command(name="iplookup", aliases=['ip', 'ipl'],help="shows info about an ip",usage="Iplookup [ip]")
    
    async def iplookup(self, ctx, *, ip):
     async with aiohttp.ClientSession() as a:
       async with a.get(f"http://ipwhois.app/json/{ip}") as b:
         c = await b.json()
         try:
           coordj = ''.join(f"{c['latitude']}" + ", " + f"{c['longitude']}")
           embed = discord.Embed(
           title="IP: {}".format(ip),
						description=f"```txt\n\nLocation Info:\nIP: {ip}\nIP Type: {c['type']}\nCountry, Country code: {c['country']} ({c['country_code']})\nPhone Number Prefix: {c['country_phone']}\nRegion: {c['region']}\nCity: {c['city']}\nCapital: {c['country_capital']}\nLatitude: {c['latitude']}\nLongitude: {c['longitude']}\nLat/Long: {coordj} \n\nTimezone Info:\nTimezone: {c['timezone']}\nTimezone Name: {c['timezone_name']}\nTimezone (GMT): {c['timezone_gmt']}\nTimezone (GMT) offset: {c['timezone_gmtOffset']}\n\nContractor/Hosting Info:\nASN: {c['asn']}\nISP: {c['isp']}\nORG: {c['org']}\n\nCurrency:\nCurrency type: {c['currency']}\nCurrency Code: {c['currency_code']}\nCurrency Symbol: {c['currency_symbol']}\nCurrency rates: {c['currency_rates']}\nCurrency type (plural): {c['currency_plural']}```",
						color=0x977FD7
					)
           embed.set_footer(text='Thanks For Using Luka',icon_url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
           await ctx.send(embed=embed)
         except KeyError:
          embed = discord.Embed(
						description="KeyError has occured, perhaps this is a bogon IP address, or invalid IP address?",
						color=0x977FD7
					)
          await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Fun(bot))