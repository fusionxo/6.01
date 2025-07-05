import discord
from discord.ext import commands


class automessages1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """AutoMessages commands"""
  
    def help2_custom(self):
		      emoji = '<:puzzle:1087776730137239572>'
		      label = "AutoMessages"
		      description = "Shows the AutoMessages commands."
		      return emoji, label, description

    @commands.group()
    async def __AutoMessages__(self, ctx: commands.Context):
        """`am add <channel> <interval> <true/false> <message>`, `am remove <channel>`, `am view <channel>`, `am list`"""