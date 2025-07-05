import discord
from discord.ext import commands


class mod1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Moderation commands"""
  
    def help_custom(self):
		      emoji = '<:usershield:1087776624486920294>'
		      label = "Moderation"
		      description = "Shows the moderation commands."
		      return emoji, label, description

    @commands.group()
    async def __Moderation__(self, ctx: commands.Context):
        """`menable`, `mdisable`, `softban` , `purge` , `purge contains` , `purge startswith` , `purge invites` , `purge user` , `mute` , `unmute` , `kick` , `roleallhumans` , `roleallbots` , `removeallhumans` , `removeallbots` , `warn` , `ban` , `unban` , `clone` , `nick` , `slowmode` ,  `unslowmode` , `clear` , `clear all` , `clear bots` , `clear embeds` , `clear files` , `clear mentions` , `clear images` , `clear contains` , `clear reactions` , `nuke` , `lock` , `unlock`, `hide`, `unhide`, `lockall`, `unlockall`, `hideall`, `unhideall`"""