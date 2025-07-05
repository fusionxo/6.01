import discord
from discord.ext import commands


class soundboard1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Soundboard commands"""
  
    def help2_custom(self):
		      emoji = '<:audio:1089139281441861764>'
		      label = "Soundboard"
		      description = "Shows the soundboard commands."
		      return emoji, label, description

    @commands.group()
    async def __Soundboard__(self, ctx: commands.Context):
        """`b virus`, `b cutekimochi`,`b kimochi`, `b gigachad`, `b sigma`, `b bosrike`, `b hmoan`, `b uaregey`, `b whyugey`, `b stepbro`, `b pstepbro`, `b omgunoob`, `b modibkl`, `b biharkid`, `b haatomc`, `b ninjahatori`, `b bengali`, `b marathi`, `b narutosad`, `b abdi`, `b ahshit`, `b airhorn`, `b araara`, `b bhau`, `b bruh`, `b cuteuwu`, `b disconnected`, `b game-over`, `b giggle`, `b ha-gay`, `b hellomf`, `b honk`, `b illuminati`, `b john-cena`, `b laugh`, `b magic`, `b margayamc`, `b moin-meister`, `b nani`, `b oioi`, `b oioioi`, `b onichan`, `b pew-pew`, `b ph-intro`, `b quack-quack`, `b rickroll`, `b samsung-notification`, `b sheesh`, `b sike`, `b skype`, `b siuuu`, `b superidol`, `b surprisemf`, `b sus`, `b uwu`, `b verpissdich`, `b wow`, `b iphone-notification`, `b gimme-ohyeah`, `b amogus`, `b nogodno`, `b dattebayo`, `b afewmomentslater`, `b ilikecutg`, `b oppai-dragon`"""