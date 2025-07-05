import discord
from discord.ext import commands


class tts1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Text-To-Speech commands"""
  
    def help2_custom(self):
		      emoji = '<:sound:1087776618723950593>'
		      label = "TTS"
		      description = "Shows the Text-To-Speech page."
		      return emoji, label, description

    @commands.group()
    async def __tts__(self, ctx: commands.Context):
        """`tts <text>`"""