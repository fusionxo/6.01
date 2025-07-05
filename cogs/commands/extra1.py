import discord
from discord.ext import commands


class extra1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Extra commands"""
  
    def help_custom(self):
		      emoji = '<:support:1087776643868790975>'
		      label = "Extra"
		      description = "Shows some useful exatra commands."
		      return emoji, label, description

    @commands.group()
    async def __Extra__(self, ctx: commands.Context):
        """`stats` , `invite` , `serverinfo` , `userinfo` , `roleinfo` , `botinfo` , `status` , `emoji` , `user` , `role` , `channel` , `boosts`, `emoji-add` , `removeemoji` , `unbanall` ,  `joined-at` , `ping` , `github` , `vcinfo` , `channelinfo` , `note` , `notes` , `trashnotes` , `badges` , `list boosters`"""