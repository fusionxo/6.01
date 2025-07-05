import discord
from discord.ext import commands
import json

class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open('jsons/media.json', 'r') as f:
            self.config = json.load(f)

    def save_config(self):
        with open('jsons/media.json', 'w') as f:
            json.dump(self.config, f, indent=4)

    async def can_delete(self, message):
        if message.author == message.guild.owner:
            return False
        elif message.author.guild_permissions.administrator:
            return False
        else:
            return True

    @commands.hybrid_group()
    async def media(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid media command. Please use `$media setup`, `$media reset`, or `$media config`.')

    @media.command(description="Set-Up media channel.")
    async def setup(self, ctx, channel: discord.TextChannel):
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.config:
            self.config[guild_id] = []
            
        if len(self.config[guild_id]) >= 3:
            await ctx.send('<:error:1088542929158688788> | You already have the maximum number of media-only channels.')
            return
        
        if channel.id in self.config[guild_id]:
            await ctx.send(f'<:error:1088542929158688788> | {channel.mention} is already a media-only channel.')
        else:
            self.config[guild_id].append(channel.id)
            self.save_config()
            await ctx.send(f'<:yes:1087776758415228998> | Set up {channel.mention} as a media-only channel.')

    @media.command(description="Reset media config.")
    async def reset(self, ctx):
        if str(ctx.guild.id) in self.config:
            self.config[str(ctx.guild.id)] = []
            self.save_config()
            await ctx.send('<:error:1088542929158688788> | Reset media-only channels.')
        else:
            await ctx.send('<:error:1088542929158688788> | There are no media-only channels to reset.')

    @media.command(description="Shows the media config.")
    async def config(self, ctx):
        if str(ctx.guild.id) in self.config:
            channels = self.config[str(ctx.guild.id)]
            if len(channels) > 0:
                channel_mentions = [f'<#{channel}>' for channel in channels]
                await ctx.send(f'<:arrow:1088544668117106708> | Media-only channels: {", ".join(channel_mentions)}')
            else:
                await ctx.send('<:error:1088542929158688788> | There are no media-only channels configured.')
        else:
            await ctx.send('<:error:1088542929158688788> | There are no media-only channels configured.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return

        if str(message.guild.id) not in self.config:
            return

        if message.channel.id not in self.config[str(message.guild.id)]:
            return

        if message.attachments:
            return

        can_delete = await self.can_delete(message)
        if can_delete:
            await message.delete()
            await message.channel.send(f"<:info:1087776877898383400> | {message.author.mention}, this is a media-only channel. Please only send messages with media attachments here.", delete_after=5)