import discord
from discord.ext import commands


class blword1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """BlacklistWord commands"""
  
    def help_custom(self):
		      emoji = '<:knight:1087776872928120915>'
		      label = "BlacklistWord"
		      description = "Shows BlacklistWord commands."
		      return emoji, label, description

    @commands.group()
    async def __BlacklistWord__(self, ctx: commands.Context):
        """`blwordlist enable`, `blwordlist disable`, `blwhitelist add`, `blwhitelist remove`"""