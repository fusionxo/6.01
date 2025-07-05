import discord
from discord.ext import commands


class autopfp1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """AutoPFP commands"""
  
    def help2_custom(self):
		      emoji = '<:media:1089136852100980806>'
		      label = "AutoPFP"
		      description = "Shows AutoPFP commands."
		      return emoji, label, description

    @commands.group()
    async def __autopfp1__(self, ctx: commands.Context):
        """`apfp channel add <channel>`, `apfp channel remove <channel>`, `afp enable`, `afp disable`"""