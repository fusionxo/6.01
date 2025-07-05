import discord
from discord.ext import commands


class games1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Games commands"""
  
    def help_custom(self):
		      emoji = '<:games:1088451606049198091>'
		      label = "Games"
		      description = "Shows the fun commands."
		      return emoji, label, description

    @commands.group()
    async def __Games__(self, ctx: commands.Context):
        """`sayhello`, `roll`, `chooseit <text>`, `flipcoin`, `compliment`, `vhug`, `truth`, `dare`, `gpt`"""