import discord
from discord.ext import commands


class anti1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Security commands"""
  
    def help_custom(self):
		      emoji = '<:securityconfig:1087776720368709752>'
		      label = "Security"
		      description = "Shows the security page."
		      return emoji, label, description

    @commands.group()
    async def __Security__(self, ctx: commands.Context):
        """`antinuke` , `antinuke enable` , `antinuke disable` , `antinuke show` , `antinuke punishment set` , `antinuke whitelist add` , `antinuke whitelist remove` , `antinuke whitelist show` , `antinuke whitelist reset` , `antinuke channelclean` , `antinuke roleclean` , `antinuke setvanity`"""