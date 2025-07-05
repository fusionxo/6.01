import discord
from discord.ext import commands
import json

class jtc1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """J2C commands"""

    def help_custom(self):
		      emoji = '<:automation:1089140152674308126>'
		      label = "Join To Create"
		      description = "Shows the log Join To Create commands."
		      return emoji, label, description

    @commands.group()
    async def __JoinToCreate__(self, ctx: commands.Context):
        """• `jtc setupj2c`, `jtc deletej2c`"""


def setup(bot):
    bot.add_cog(jtc1(bot))