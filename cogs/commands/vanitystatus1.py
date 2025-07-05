import discord
from discord.ext import commands


class vanitystatus1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """VanityStatus commands"""
  
    def help2_custom(self):
		      emoji = '<:love:1089116684046041158>'
		      label = "VanityStatus"
		      description = "Shows the VanityStatus commands."
		      return emoji, label, description

    @commands.group()
    async def __VanityStatus__(self, ctx: commands.Context):
        """`vrsetup`, `vrshow`, `vrremove`"""