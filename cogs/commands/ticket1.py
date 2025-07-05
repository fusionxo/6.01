import discord
from discord.ext import commands
import json

class ticket1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Ticket commands"""  

    def help2_custom(self):
		      emoji = '<:tiicket:1089113691082993674>'
		      label = "Ticket"
		      description = "Show the help menu of ticket command."
		      return emoji, label, description

    
    @commands.group()
    async def __Tickets__(self, ctx: commands.Context):
        """`ticket setup`, `ticket create`, `ticket addmember`, `ticket close`, `ticket reopen`, `ticket delete`, `ticket save`"""

def setup(bot):
    bot.add_cog(ticket1(bot))