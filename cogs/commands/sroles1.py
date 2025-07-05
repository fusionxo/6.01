import discord
from discord.ext import commands
import json

class sroles1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Giveaway commands"""
  
    def help2_custom(self):
		      emoji = '<:dice:1295685592092381235>'
		      label = "Custom Roles"
		      description = "Shows the custom roles commands."
		      return emoji, label, description
    @commands.group()
    async def __sroles__(self, ctx: commands.Context):
        """`choose`, `rrole`, `remove`"""

def setup(bot):
    bot.add_cog(sroles1(bot))