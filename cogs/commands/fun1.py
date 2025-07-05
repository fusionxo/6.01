import discord
from discord.ext import commands


class fun1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Fun commands"""
  
    def help_custom(self):
		      emoji = '<:fun:1088451095795351672>'
		      label = "Fun"
		      description = "Shows the fun commands."
		      return emoji, label, description

    @commands.group()
    async def __Fun__(self, ctx: commands.Context):
        """` tickle` , `kiss` , `hug` , `slap` , `pat` , `feed` , `pet` , `howgay` , `slots` , ` pp` , `meme` , `cat` , `iplookup`, `ship`, `roast`"""