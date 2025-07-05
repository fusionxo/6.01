import discord
from discord.ext import commands


class starboard1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Starboard commands"""
  
    def help2_custom(self):
		      emoji = '<:sstar:1089111407712276580>'
		      label = "Starboard"
		      description = "Shows the Starboard commands."
		      return emoji, label, description

    @commands.group()
    async def __Starboard__(self, ctx: commands.Context):
        """`starboard channel`, `starboard starlimit`, `starboard remove`"""