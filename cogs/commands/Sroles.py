import discord
from discord.ext import commands
import json
from utils.Tools import *
from utils.checks import global_check

class Sroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_configs = {}
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)

        # This part was already correct
        try:
            with open('jsons/roles.json', 'r') as f:
                self.role_configs = json.load(f)
        except FileNotFoundError:
            pass

        self.max_roles_per_user = 10

    def help2_custom(self):
        emoji = '<:dice:1295685592092381235>'
        label = "Custom Roles"
        description = "Shows the custom roles commands."
        return emoji, label, description

    @commands.group()
    async def __sroles__(self, ctx: commands.Context):
        """`choose`, `rrole`, `remove`"""
    # --- End of fix ---

    def get_guild_role_config(self, guild_id):
        if guild_id not in self.role_configs:
            self.role_configs[guild_id] = {}
        return self.role_configs[guild_id]


    def save_role_configs(self):
        with open('jsons/roles.json', 'w') as f:
            json.dump(self.role_configs, f)

    @commands.command()
    
    @commands.has_permissions(manage_roles=True)
    async def choose(self, ctx, role_name, role_mention):
        if not role_name or not role_mention:
            await ctx.send('Usage: $choose role_name role_mention')
            return

        role = discord.utils.get(ctx.guild.roles, mention=role_mention)
        if not role:
            await ctx.send(f"Invalid Role '{role_mention}'")
            return

        guild_id = str(ctx.guild.id)
        guild_role_config = self.get_guild_role_config(guild_id)

        # Check if the user has reached the maximum number of roles
        user_roles = [r for r in ctx.author.roles if r.name in guild_role_config.keys()]
        if len(user_roles) >= self.max_roles_per_user:
            await ctx.send(f"You have already reached the maximum of {self.max_roles_per_user} roles.")
            return

        guild_role_config[role_name] = role.id
        self.save_role_configs()

        embed = discord.Embed(title="Success", description=f"<:check:1087776909246607360> {role_name} role has been set to {role.mention}", color=discord.Color.green())
        await ctx.send(embed=embed)


    @commands.command()
    
    @commands.has_permissions(manage_roles=True)
    async def crrole(self, ctx, role_name):
        if not role_name:
            await ctx.send('Usage: $removerole role_name')
            return

        guild_id = str(ctx.guild.id)
        guild_role_config = self.get_guild_role_config(guild_id)

        if role_name not in guild_role_config:
            await ctx.send(f"Role '{role_name}' not found.")
            return

        del guild_role_config[role_name]
        self.save_role_configs()

        embed = discord.Embed(title="Success", description=f"<:check:1087776909246607360> {role_name} role has been removed.", color=discord.Color.green())
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        if not isinstance(message.author, discord.Member):
            return
        
        if not message.author.guild_permissions.manage_roles:
            return

        guild_id = str(message.guild.id)
        guild_role_config = self.get_guild_role_config(guild_id)

        role_names = list(guild_role_config.keys())
        for role_name in role_names:
            if message.content.startswith(role_name):
                role_id = guild_role_config.get(role_name)
                if not role_id:
                    await message.channel.send(f"Invalid Role '{role_name}'")
                    return
                role = discord.utils.get(message.guild.roles, id=role_id)
                if not role:
                    await message.channel.send(f"Role '{role_name}' not found")
                    return
                if message.mentions:
                    member = message.mentions[0]
                    if role in member.roles:
                        embed = discord.Embed(title="Error", description=f"<:wrong:1087776947720953949> {member.mention} already has {role.mention}", color=discord.Color.red())
                        await message.channel.send(embed=embed)
                    else:
                        await member.add_roles(role)
                        embed = discord.Embed(title="Success", description=f"<:check:1087776909246607360> {member.mention} has been given {role.mention}", color=discord.Color.green())
                        await message.channel.send(embed=embed)

                else:
                    await message.channel.send(f"Please mention a user to give {role.mention}")


    @commands.command()
    
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, role_name: str, member: discord.Member):
        guild_id = str(ctx.guild.id)
        guild_role_config = self.get_guild_role_config(guild_id)

        role_id = guild_role_config.get(role_name)
        if not role_id:
            await ctx.send(f"<:wrong:1087776947720953949> Invalid Role '{role_name}'")
            return

        role = discord.utils.get(ctx.guild.roles, id=role_id)
        if not role:
            await ctx.send(f"<:wrong:1087776947720953949> Role '{role_name}' not found")
            return

        if role not in member.roles:
            embed = discord.Embed(title="Error", description=f"<:wrong:1087776947720953949> {member.mention} does not have {role.mention}", color=discord.Color.red())
            await ctx.send(embed=embed)
          
        else:
            await member.add_roles(role)
            embed = discord.Embed(title="Success", description=f"<:check:1087776909246607360> {member.mention} has been given {role.mention}", color=discord.Color.green())
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Sroles(bot))