import discord, json
from discord.ext import commands
from core import Luka, Cog, Context

class Errors(Cog):
  def __init__(self, client:Luka):
    self.client = client
    print(f"Cog Loaded: {self.__class__.__name__}")

  @commands.Cog.listener()
  async def on_command_error(self, ctx: Context, error):
    with open('jsons/blacklist.json', 'r') as f:
      data = json.load(f)
    if isinstance(error, commands.CommandNotFound):
      return
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.NoPrivateMessage):
      hacker = discord.Embed(color=0x977FD7,description=f"You Can\'t Use My Commands In Dm(s)", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
      hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker)
    elif isinstance(error, commands.TooManyArguments):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

    elif isinstance(error, commands.CommandOnCooldown):
      hacker = discord.Embed(color=0x977FD7,description=f"<:wrong:1087776947720953949> | {ctx.author.name} is on cooldown retry after {error.retry_after:.2f} second(s)", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
      hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker)
    elif isinstance(error, commands.MaxConcurrencyReached):
      hacker = discord.Embed(color=0x977FD7,description=f"<:wrong:1087776947720953949> | This Command is already going on, let it finish and retry after", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
      hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker)
      ctx.command.reset_cooldown(ctx)
    elif isinstance(error, commands.MissingPermissions):
      missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
      if len(missing) > 2:
                fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
      else:
                fmt = " and ".join(missing)
      hacker = discord.Embed(color=0x977FD7,description=f"<:wrong:1087776947720953949> | You lack `{fmt}` permission(s) to run `{ctx.command.name}` command!", timestamp=ctx.message.created_at)
      hacker.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar}")
      hacker.set_thumbnail(url =f"{ctx.author.avatar}")
      await ctx.reply(embed=hacker)
      ctx.command.reset_cooldown(ctx)

    elif isinstance(error, commands.BadArgument):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)

    elif isinstance(error, discord.HTTPException):
      pass
    elif isinstance(error, commands.CommandInvokeError):
      pass
    elif isinstance(error, commands.CheckFailure):
      if str(ctx.author.id) in data["ids"]:
        embed = discord.Embed(title="<:wrong:1087776947720953949> Blacklisted", description="You Are Blacklisted From Using My Commands.\nIf You Think That It Is A Mistake, You Can Appeal In Our Support Server By Clicking [here]( https://bit.ly/luka-support)", color=0x977FD7)
        await ctx.reply(embed=embed, mention_author=False)
