import discord
from discord.ext import commands


class general1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """General commands"""
  
    def help_custom(self):
		      emoji = '<:search:1088438737727406142>'
		      label = "General"
		      description = "Shows the general useful commands."
		      return emoji, label, description

    @commands.group()
    async def __General__(self, ctx: commands.Context):
        """`afk` , `avatar` , `banner` , `servericon` , `membercount` , `poll` , `hack` , `token` , `users` , `italicize` , `strike` , `quote` , `code` , `bold` , `censor` , `underline` , `gender` , `wizz` , `pikachu` , `shorten` , `urban` , `rickroll` , `hash` , `snipe` , `roleall`"""