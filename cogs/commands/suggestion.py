import discord
from discord.ext import commands

DEV_SUGGESTION_CHANNEL_ID = 1085536508129312788

class Suggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='suggest', description='Send a suggestion to the bot developer.')
    @commands.cooldown(1, 300, commands.BucketType.user) # 5-minute cooldown per user
    async def suggest(self, ctx: commands.Context, *, suggestion: str):
        
        suggestion_channel = self.bot.get_channel(DEV_SUGGESTION_CHANNEL_ID)

        if not suggestion_channel:
            print(f"Error: Suggestion channel with ID {DEV_SUGGESTION_CHANNEL_ID} not found.")
            return await ctx.send("Sorry, I couldn't submit your suggestion right now. Please try again later.", ephemeral=True)

        embed = discord.Embed(
            title="New Bot Suggestion",
            description=suggestion,
            color=0x977FD7,
            timestamp=discord.utils.utcnow()
        )
        
        embed.set_author(name=f"From: {ctx.author} ({ctx.author.id})", icon_url=ctx.author.display_avatar.url)
        
        if ctx.guild:
            embed.add_field(name="Source Server", value=f"{ctx.guild.name} (`{ctx.guild.id}`)", inline=False)
        else:
            embed.add_field(name="Source", value="Direct Message", inline=False)

        try:
            message = await suggestion_channel.send(embed=embed)
            await message.add_reaction("👍")
            await message.add_reaction("👎")
        except discord.Forbidden:
            print(f"Error: I don't have permission to send messages or add reactions in the suggestion channel ({DEV_SUGGESTION_CHANNEL_ID}).")
            return await ctx.send("Sorry, I couldn't submit your suggestion right now. Please try again later.", ephemeral=True)
        except Exception as e:
            print(f"An unexpected error occurred while sending a suggestion: {e}")
            return await ctx.send(f"An unexpected error occurred. Please try again later.", ephemeral=True)

        await ctx.send("Your suggestion has been sent to the developers. Thank you for your feedback!", ephemeral=True)

    @suggest.error
    async def on_suggest_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You're on cooldown! Please wait `{error.retry_after:.2f}` seconds before sending another suggestion.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You need to provide a suggestion! Usage: `!suggest <your idea>`", ephemeral=True)
        else:
            await ctx.send("An unknown error occurred.", ephemeral=True)
            raise error

async def setup(bot):
    await bot.add_cog(Suggestion(bot))
