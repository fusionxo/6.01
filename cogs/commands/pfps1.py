import discord
from discord.ext import commands
import json

class pfps1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Pfps commands"""
  
    def help_custom(self):
		      emoji = '<:user:1087776942679412856>'
		      label = "Pfps"
		      description = "Shows the Pfps commands."
		      return emoji, label, description
    @commands.group()
    async def __Pfps__(self, ctx: commands.Context):
        """• `anime`, `couples`, `boys`, `girls`, `pic`, `` """

def setup(bot):
    bot.add_cog(pfps1(bot))