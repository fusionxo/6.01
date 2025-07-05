import discord
from discord.ext import commands


class media1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Media commands"""
  
    def help2_custom(self):
		      emoji = '<:media:1089136852100980806>'
		      label = "Media"
		      description = "Shows some useful media commands."
		      return emoji, label, description

    @commands.group()
    async def __Media__(self, ctx: commands.Context):
        """`media setup`, `media reset`, `media config`"""