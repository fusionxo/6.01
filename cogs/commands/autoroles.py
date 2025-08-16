import discord
from discord.ext import commands
import json
from utils import *
from utils.checks import global_check

class Autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'jsons/autorole.json'
        self.load_config()
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def get_guild_config(self, guild_id):
        return self.config.setdefault(str(guild_id), {'bot_roles': [], 'human_roles': []})

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_config = self.get_guild_config(member.guild.id)
        if member.bot:
            role_ids = guild_config.get('bot_roles', [])
            reason = 'Luka | Autorole'
        else:
            role_ids = guild_config.get('human_roles', [])
            reason = 'Luka | Autorole'

        for role_id in role_ids:
            role = member.guild.get_role(role_id)
            if role is not None:
                await member.add_roles(role, reason=reason)

    @commands.group(name='autorole', invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def autorole_group(self, ctx):
        await ctx.send_help(ctx.command)

    @autorole_group.group(name='bots')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_bots_group(self, ctx):
        await ctx.send_help(ctx.command)

    @autorole_bots_group.command(name='add')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_bots_add(self, ctx, role: discord.Role):
        guild_config = self.get_guild_config(ctx.guild.id)
        bot_roles = guild_config.setdefault('bot_roles', [])
        if len(bot_roles) < 3:
            bot_roles.append(role.id)
            self.save_config()
            await ctx.send(f'Bot role {role.name} added')
        else:
            await ctx.send('You can only have up to 3 bot roles')

    @autorole_bots_group.command(name='remove')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_bots_remove(self, ctx, role: discord.Role):
        guild_config = self.get_guild_config(ctx.guild.id)
        bot_roles = guild_config.setdefault('bot_roles', [])
        try:
            bot_roles.remove(role.id)
            self.save_config()
            await ctx.send(f'Bot role {role.name} removed')
        except ValueError:
            await ctx.send(f'Bot role {role.name} not found')

    @autorole_bots_group.command(name='list')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_bots_list(self, ctx):
        guild_config = self.get_guild_config(ctx.guild.id)
        bot_roles = guild_config.get('bot_roles', [])
        if bot_roles:
            roles_text = ', '.join([ctx.guild.get_role(role_id).name for role_id in bot_roles])
            await ctx.send(f'Bot roles: {roles_text}')
        else:
            await ctx.send('No bot roles set')

    @autorole_bots_group.command(name='reset')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_bots_reset(self, ctx):
        guild_config = self.get_guild_config(ctx.guild.id)
        guild_config.pop('bot_roles', None)
        self.save_config()
        await ctx.send('Bot roles reset')

    @autorole_group.group(name='humans')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_humans_group(self, ctx):
        await ctx.send_help(ctx.command)

    @autorole_humans_group.command(name='add')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_humans_add(self, ctx, role: discord.Role):
        guild_config = self.get_guild_config(ctx.guild.id)
        human_roles = guild_config.setdefault('human_roles', [])
        if len(human_roles) < 5:
            human_roles.append(role.id)
            self.save_config()
            await ctx.send(f'Human role {role.name} added')
        else:
            await ctx.send('You can only have up to 5 human roles')

    @autorole_humans_group.command(name='remove')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_humans_remove(self, ctx, role: discord.Role):
        guild_config = self.get_guild_config(ctx.guild.id)
        human_roles = guild_config.setdefault('human_roles', [])
        try:
            human_roles.remove(role.id)
            self.save_config()
            await ctx.send(f'Human role {role.name} removed')
        except ValueError:
            await ctx.send(f'Human role {role.name} not found')

    @autorole_humans_group.command(name='list')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_humans_list(self, ctx):
        guild_config = self.get_guild_config(ctx.guild.id)
        human_roles = guild_config.get('human_roles', [])
        if human_roles:
            roles_text = ', '.join([ctx.guild.get_role(role_id).name for role_id in human_roles])
            await ctx.send(f'Human roles: {roles_text}')
        else:
            await ctx.send('No human roles set')

    @autorole_humans_group.command(name='reset')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_humans_reset(self, ctx):
        guild_config = self.get_guild_config(ctx.guild.id)
        guild_config.pop('human_roles', None)
        self.save_config()
        await ctx.send('Human roles reset')

    @autorole_group.command(name='config')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_config(self, ctx):
        guild_config = self.get_guild_config(ctx.guild.id)
        bot_roles = guild_config.get('bot_roles', [])
        human_roles = guild_config.get('human_roles', [])

        if bot_roles:
            bot_roles_text = ', '.join([ctx.guild.get_role(role_id).name for role_id in bot_roles])
        else:
            bot_roles_text = 'Not set'

        if human_roles:
            human_roles_text = ', '.join([ctx.guild.get_role(role_id).name for role_id in human_roles])
        else:
            human_roles_text = 'Not set'

        await ctx.send(f'Bot roles: {bot_roles_text}\nHuman roles: {human_roles_text}')

    @autorole_group.command(name='reset')
    @commands.has_permissions(manage_guild=True)  
    async def autorole_reset(self, ctx, target=None):
        if target == 'all':
            guild_config = self.get_guild_config(ctx.guild.id)
            guild_config.clear()
            self.save_config()
            await ctx.send('All autoroles reset')
        elif target == 'bots':
            await self.autorole_bots_reset(ctx)
        elif target == 'humans':
            await self.autorole_humans_reset(ctx)
        else:
            await ctx.send_help(ctx.command)

def setup(bot):
    bot.add_cog(Autorole(bot))
