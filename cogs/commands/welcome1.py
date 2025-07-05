import discord
from discord.ext import commands


class welcome1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Welcome commands"""
  
    def help_custom(self):
		      emoji = '<:welcome:1088445113417605150>'
		      label = "Welcome"
		      description = "Shows the welcome commands."
		      return emoji, label, description

    @commands.group()
    async def __Welcome__(self, ctx: commands.Context):
        """`welcome` , `welcome enable` , `welcome  disable` , `welcome message` , `welcome emessage` , `welcome channel` , `welcome test `"""