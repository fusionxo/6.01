import discord
from discord.ext import commands


class voicecmds1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Voice Commands"""
  
    def help_custom(self):
		      emoji = '<:voice:1090677401874337833>'
		      label = "VoiceCmds"
		      description = "Shows the Voice commands."
		      return emoji, label, description

    @commands.group()
    async def __Voice__(self, ctx: commands.Context):
        """`voice`, `voice kick` , `voice kickall` , `voice mute` , `voice muteall` , `voice unmute` , `voice unmuteall` , `voice deafen` , `voice deafenall` , `voice undeafen` , `voice undeafenall` , `voice moveall`"""