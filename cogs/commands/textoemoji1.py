import discord
from discord.ext import commands


class tte1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """TextToEmoji commands"""
  
    def help2_custom(self):
		      emoji = '<:puzzle:1087776730137239572>'
		      label = "TextToEmoji"
		      description = "Shows the TextToEmoji commands."
		      return emoji, label, description

    @commands.group()
    async def __TextToEmoji__(self, ctx: commands.Context):
        """`texttoemoji`"""