import discord
from discord.ext.commands import BucketType, cooldown, CommandOnCooldown, CommandInvokeError
from discord.ext import commands
from utils.Tools import *
from utils.checks import global_check

class TextToEmoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_mapping = {
            'A': '<:Luka_A:1088203106958983200>',
            'B': '<:Luka_B:1088203111610450040>',
            'C': '<:Luka_C:1088203115901231276>',
            'D': '<:Luka_D:1088203122515656804>',
            'E': '<:Luka_E:1088203124801544263>',
            'F': '<:Luka_F:1088203129285267616>',
            'G': '<:Luka_G:1088203135773851659>',
            'H': '<:Luka_H:1088203138206535802>',
            'I': '<:Luka_I:1088203143214542888>',
            'J': '<:Luka_J:1088203149694738523>',
            'K': '<:Luka_K:1088203104496930816>',
            'L': '<:Luka_L:1088203332327313470>',
            'M': '<:Luka_M:1088203336941043763>',
            'N': '<:Luka_N:1088203340980158526>',
            'O': '<:Luka_O:1088203347594588251>',
            'P': '<:Luka_P:1088203350052446258>',
            'Q': '<:Luka_Q:1088203355114979388>',
            'R': '<:Luka_R:1088203359732903966>',
            'S': '<:Luka_S:1088203365965643939>',
            'T': '<:Luka_T:1088203370310934528>',
            'U': '<:Luka_U:1088203372848484362>',
            'V': '<:Luka_V:1088203376661119037>',
            'W': '<:Luka_W:1088203379282554903>',
            'X': '<:Luka_X:1088203384034689116>',
            'Y': '<:Luka_Y:1088203388388384911>',
            'Z': '<:Luka_Z:1088203329412280412>',
            '0': '<:Luka_0:1088203534790557726>',
            '1': '<:Luka_1:1088203539374936144>',
            '2': '<:Luka_2:1088203496488190092>',
            '3': '<:Luka_3:1088203501601042523>',
            '4': '<:Luka_4:1088203505950539817>',
            '5': '<:Luka_5:1088203508727160882>',
            '6': '<:Luka_6:1088203513361870892>',
            '7': '<:Luka_7:1088203520416677998>',
            '8': '<:Luka_8:1088203524631953551>',
            '9': '<:Luka_9:1088203529505747004>',
        }
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help2_custom(self):
		      emoji = '<:puzzle:1087776730137239572>'
		      label = "TextToEmoji"
		      description = "Shows the TextToEmoji commands."
		      return emoji, label, description

    @commands.group()
    async def __TextToEmoji__(self, ctx: commands.Context):
        """`texttoemoji`"""


    @commands.hybrid_command(name='texttoemoji', with_app_command=True, aliases=['tte'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    
    
    async def texttoemoji(self, ctx: commands.Context, *, text: str):
        try:
            emoji_text = ''
            for i, char in enumerate(text.upper()):
                if char in self.emoji_mapping:
                    emoji = self.emoji_mapping[char]
                    emoji_text += emoji
                elif char == ' ' and i > 0 and i < len(text) - 1 and text[i-1] != ' ' and text[i+1] != ' ':
                    emoji_text += '     '
                else:
                    emoji_text += char

            if len(emoji_text) > 4000:
                for chunk in [emoji_text[i:i+4000] for i in range(0, len(emoji_text), 4000)]:
                    await ctx.send(chunk)
            else:
                await ctx.send(emoji_text)
                
        except discord.HTTPException as e:
            if e.code == 50035:
                await ctx.send("Error: The message is too long. Please shorten the input.")
            else:
                await ctx.send("An error occurred while processing your request.")
        except Exception as e:
            await ctx.send(f"Unexpected error: {str(e)}")

def setup(bot):
    bot.add_cog(TextToEmoji(bot))
