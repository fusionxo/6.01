import discord
from core import Luka, Cog
from discord.ext import commands
from utils.Tools import add_user_to_blacklist, getConfig


class AutoBlacklist(Cog):

  def __init__(self, client: Luka):
    self.client = client
    self.spam_cd_mapping = commands.CooldownMapping.from_cooldown(
      5, 5, commands.BucketType.member)
    self.spam_command_mapping = commands.CooldownMapping.from_cooldown(
      6, 10, commands.BucketType.member)

    print("Cog Loaded: AutoBlacklist")

  @commands.Cog.listener()
  async def on_message(self, message):
    bucket = self.spam_cd_mapping.get_bucket(message)
    Luka = '<@1040194948496109569>'
    retry = bucket.update_rate_limit()

    if retry:
      if message.content == Luka or message.content == "<@!1040194948496109569>":
        add_user_to_blacklist(message.author.id)
        await message.channel.send(
          "**Successfully Blacklisted {} For Spam Mentioning Me!**".format(
            message.author.mention))

  @commands.Cog.listener()
  async def on_command(self, ctx):
    bucket = self.spam_command_mapping.get_bucket(ctx.message)
    retry = bucket.update_rate_limit()
    if retry:
      add_user_to_blacklist(ctx.author.id)
      await ctx.reply(
        "**Successfully Blacklisted {} For Spamming My Commands!**".format(
          ctx.author.mention))
