import discord
from discord.ext import commands


class vcroles1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """VcRoles commands"""
  
    def help2_custom(self):
		      emoji = '<:soundfull:1087776969627811891>'
		      label = "VcRoles"
		      description = "Shows the VcRoles commands."
		      return emoji, label, description

    @commands.group()
    async def __VcRoles__(self, ctx: commands.Context):
        """`vcrole bots add`, `vcrole bots remove`, `vcrole bots`, `vcrole humans add`, `vcrole humans remove`, `vcrole humans`, `vcrole reset`, `vcrole config`, `vcrole`"""