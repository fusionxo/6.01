import discord
from discord.ext import commands


class autorespond1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Soundboard commands"""
  
    def help2_custom(self):
		      emoji = '<:audio:1089139281441861764>'
		      label = "Autorespond"
		      description = "Shows the autorespond commands."
		      return emoji, label, description

    @commands.group()
    async def __autorespond1__(self, ctx: commands.Context):
        """`autoresponder create`, `autoresponder delete`, `autoresponder config`, `autoresponder edit`"""