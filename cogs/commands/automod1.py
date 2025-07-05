import discord
from discord.ext import commands


class automod1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Automod commands"""
  
    def help_custom(self):
		      emoji = '<:autom:1088452318376239114>'
		      label = "Automod"
		      description = "Shows Automod commands."
		      return emoji, label, description

    @commands.group()
    async def __Automod__(self, ctx: commands.Context):
        """`automod antilink on`, `automod antispam on`, `automod whitelist add/remove`"""