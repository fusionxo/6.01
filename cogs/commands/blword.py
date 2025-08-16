import discord
from discord.ext import commands
import json
from utils.Tools import *
from utils.checks import global_check

class blword(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.blacklist_enabled = {}
        self.whitelist = {}
        self.banned_words = []
        self.exception_list = []
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help_custom(self):
		      emoji = '<:knight:1087776872928120915>'
		      label = "BlacklistWord"
		      description = "Shows BlacklistWord commands."
		      return emoji, label, description

    @commands.group()
    async def __BlacklistWord__(self, ctx: commands.Context):
        """`blwordlist enable`, `blwordlist disable`, `blwhitelist add`, `blwhitelist remove`"""

        try:
            with open('jsons/blwordlist.json', 'r') as f:
                self.blacklist_enabled = json.load(f)
        except FileNotFoundError:
            pass

        try:
            with open('jsons/blwordwhitelist.json', 'r') as f:
                self.whitelist = json.load(f)
        except FileNotFoundError:
            pass

        try:
            with open('jsons/word_list.json', 'r') as f:
                self.banned_words = json.load(f)
        except FileNotFoundError:
            self.banned_words = ['madarchod', 'behenchod', 'Bhosdike', 'Chutiya', 'rand', 'randi', 
                                 'bsdk', 'chut', 'madharchod', 'fuck', 'nigga', 'pussy', 'randwa', 
                                 'lund', 'hizra', 'prick', 'bastard', 'bellend', 'ass', 'cunt', 'balls', 
                                 'shit', 'crap', 'dumbass', 'fucker', 'witch', 'slut', 'dickhead', 
                                 'whore', 'bitch', 'tits', 'shithead', 'bhosda', 'fuddi', 'bakchod', 
                                 'chinal', 'chamar', 'jhat', 'chuche']

        try:
            with open('jsons/exception_list.json', 'r') as f:
                self.exception_list = json.load(f)
        except FileNotFoundError:
            self.exception_list = ['pass', 'world', 'python']

    @commands.command(description='Enable/Disable blacklist word checking.')
    
    
    async def blwordlist(self, ctx, arg):
        guild_id = str(ctx.guild.id)
        arg = arg.lower()

        if arg == "enable":
            self.blacklist_enabled[guild_id] = True
            with open('jsons/blwordlist.json', 'w') as f:
                json.dump(self.blacklist_enabled, f)
            embed = discord.Embed(title="<:check:1087776909246607360> Blacklist word checking has been enabled!", color=0x00FFFF)
            await ctx.send(embed=embed)
        elif arg == "disable":
            self.blacklist_enabled[guild_id] = False
            with open('jsons/blwordlist.json', 'w') as f:
                json.dump(self.blacklist_enabled, f)
            embed = discord.Embed(title="<:Error:1062714306652803132> Blacklist word checking has been disabled!", color=0x00FFFF)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Invalid Argument", description="Please use `enable` or `disable`.", color=0xFF0000)
            await ctx.send(embed=embed)

    @commands.command(description="Whitelist a user so that blacklisted words do not affect them. (Requires manage messages permission)")
    @commands.has_permissions(manage_messages=True)
    
    
    async def blwhitelist(self, ctx, action: str, member: discord.Member):

        guild_id = str(ctx.guild.id)
        action = action.lower()

        if guild_id not in self.whitelist:
            self.whitelist[guild_id] = []

        if action not in ["add", "remove"]:
            await ctx.send("Invalid action. Use `add` or `remove`.")
            return

        if action == "add":
            if member.id not in self.whitelist[guild_id]:
                self.whitelist[guild_id].append(member.id)
                await ctx.send(f"{member.mention} has been **whitelisted**.")
            else:
                await ctx.send(f"{member.mention} is already whitelisted.")
        elif action == "remove":
            if member.id in self.whitelist[guild_id]:
                self.whitelist[guild_id].remove(member.id)
                await ctx.send(f"{member.mention} has been removed from the whitelist.")
            else:
                await ctx.send(f"{member.mention} is not whitelisted.")

        with open('jsons/blwordwhitelist.json', 'w') as f:
            json.dump(self.whitelist, f)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore DMs
        if message.guild is None:
            return

        guild_id = str(message.guild.id)
        if guild_id not in self.blacklist_enabled or not self.blacklist_enabled[guild_id]:
            return

        if guild_id in self.whitelist and message.author.id in self.whitelist[guild_id]:
            return

        messageContent = message.content.lower()
        words = messageContent.split()

        for word in words:
            if word in self.banned_words and word not in self.exception_list:
                await message.delete()
                embed = discord.Embed(description="<:wrong:1087776947720953949> Don\'t say this kind of words in chat!", color=0xFF0000)
                await message.channel.send(embed=embed)
                break

        for attachment in message.attachments:
            if attachment.filename.endswith(('.dll', '.exe', '.zip', '.rar', '.flp')):
                await message.delete()
                ext = attachment.filename.split('.')[-1].upper()
                embed = discord.Embed(description=f"<:wrong:1087776947720953949> No {ext}'s allowed in chat!", color=0xFF0000)
                await message.channel.send(embed=embed)
                break

def setup(bot):
    bot.add_cog(blword(bot))
