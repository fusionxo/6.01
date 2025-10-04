import discord
from discord.ext import commands
from utils import *
from utils.checks import global_check

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help_custom(self):
		      emoji = '<:games:1088451606049198091>'
		      label = "Games"
		      description = "Shows the fun commands."
		      return emoji, label, description

    @commands.group()
    async def __Games__(self, ctx: commands.Context):
        """`sayhello`, `roll`, `chooseit <text>`, `flipcoin`, `compliment`, `vhug`, `truth`, `dare`, `genai`"""

    @commands.command()
    async def sayhello(self, ctx):
        """Say hello to the bot!"""
        embed = discord.Embed(title="👋 Hello!", color=0x977FD7)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, sides: int = 6):
        """Roll a dice with a specified number of sides (default: 6)."""
        if sides <= 0:
            await ctx.send("Invalid number of sides!")
            return

        import random
        result = random.randint(1, sides)
        embed = discord.Embed(title="🎲 Dice Roll", description=f"You rolled a {result}!", color=0x977FD7)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def chooseit(self, ctx, *choices):
        """Let the bot choose one option from multiple choices separated by spaces."""
        if not choices:
            await ctx.send("Please provide at least one choice!")
            return

        import random
        choice = random.choice(choices)
        embed = discord.Embed(title="🤔 I Choose...", description=f"I choose **{choice}**!", color=0x977FD7)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def flipcoin(self, ctx):
        """Flip a coin and get either heads or tails."""
        import random
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"The coin landed on **{result}**!", color=0x977FD7)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def compliment(self, ctx, user: discord.Member = None):
        """Receive a compliment from the bot or compliment another user."""
        compliments = ["You're amazing!", "You're awesome!", "You're doing great!""You have a great smile!", "I love your sense of style.", "You're so smart and funny!", "I'm so grateful to have you in my life.", "You're an amazing friend.", "Your work is incredible.", "You're so talented!", "You're always so positive and upbeat.", "I love your energy!"]
        import random

        if user is None:
            compliment = random.choice(compliments)
            embed = discord.Embed(title="💖 Compliment", description=compliment, color=0x977FD7)
        else:
            compliment = random.choice(compliments)
            embed = discord.Embed(title="💖 Compliment", description=f"{user.mention}, {compliment}", color=0x977FD7)

        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def vhug(self, ctx, user: discord.Member):
        """Send a virtual hug to a user!"""
        embed = discord.Embed(title="🤗 Virtual Hug", description=f"{ctx.author.mention} sent a hug to {user.mention}!", color=0x977FD7)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))