import discord
from discord.ext import commands
import pymongo
from utils.Tools import *

class AutoSnipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = pymongo.MongoClient("mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client['autosnipe']
        self.collection = self.db['snipedata']

        # Load autosnipe settings for each guild
        self.autosnipe_settings = {}
        for guild in self.bot.guilds:
            result = self.collection.find_one({'_id': str(guild.id)})
            if result is not None:
                self.autosnipe_settings[str(guild.id)] = result

    @commands.hybrid_group(name="autosnipe", description="autosnipe channel\autosnipe config\autosnipe delete", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def autosnipe(self, ctx):
        """autosnipe channel/autosnipe config/leave delete"""
        x = "$"
        await ctx.send(f"Available Commands: `{x}autosnipe channel`")

    @autosnipe.command(description='Set-up autosnipe channel.')
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        try:
            self.collection.update_one({'_id': str(ctx.guild.id)}, {'$set': {'channel': str(channel.id)}}, upsert=True)
            self.autosnipe_settings[str(ctx.guild.id)] = {'_id': str(ctx.guild.id), 'channel': str(channel.id)}
            await ctx.send(f"<a:xD_tick:1062682152317227068> | autosnipe channel are updated to <#{channel.id}>")
        except Exception as e:
            return await ctx.send(f"An error occurred {e}")

    @autosnipe.command(description='Shows the autosnipe config.', aliases=['show'])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        result = self.collection.find_one({'_id': str(ctx.guild.id)})
        if result is None:
            embed = discord.Embed(title=f"autosnipe channel:", description=f"No autosnipe Channel Found", color = 0x2f3136)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"autosnipe channel:", description=f"<#{result['channel']}>", color = 0x2f3136)
            await ctx.send(embed=embed)

    @autosnipe.command(description='Reset the autosnipe channel.')
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx: commands.Context):
        try:
            self.collection.delete_one({'_id': str(ctx.guild.id)})
            self.autosnipe_settings.pop(str(ctx.guild.id), None)
            await ctx.send(f'<a:xD_tick:1062682152317227068> | Successfully Deleted autosnipe Channel')
        except KeyError:
            await ctx.send(f"No autosnipe channel found for {ctx.guild.name}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        result = self.collection.find_one({'_id': str(payload.guild_id)})
        if result is not None:
            channel = self.bot.get_channel(int(result['channel']))
            if channel is not None:
                embed = discord.Embed(description=f'⚠️ Auto Snipe | Message sent by <@{payload.cached_message.author.id}> deleted in <#{payload.channel_id}>', color=0x977FD7)
                embed.add_field(name=f"Auto Snipe | Deleted By", value=f"<@{payload.cached_message.author.id}>")
                embed.add_field(name="Auto Snipe | Message", value=f"{payload.cached_message.content}")
                await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(AutoSnipe(bot))
           
