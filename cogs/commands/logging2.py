import discord
from discord.ext import commands


class logging1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Logging commands"""
  
    def help_custom(self):
		      emoji = '<:logging:1088442287115219087>'
		      label = "Logging"
		      description = "Shows the log setup commands."
		      return emoji, label, description

    @commands.group()
    async def __Logging__(self, ctx: commands.Context):
        """`logging` , `logging channel` , `logging config` , `logging delete`"""