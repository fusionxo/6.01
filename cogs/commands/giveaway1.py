import discord
from discord.ext import commands
import json

class giveaway1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Giveaway commands"""
  
    def help2_custom(self):
		      emoji = '<:giftbox:1087776608154304522>'
		      label = "Giveaway"
		      description = "Shows the giveaway commands."
		      return emoji, label, description
    @commands.group()
    async def __Giveaway__(self, ctx: commands.Context):
        """• `gstar`, `greroll <msgid>`, `gend <msgid>` """

def setup(bot):
    bot.add_cog(giveaway1(bot))