import discord
from discord.ext import commands
import json
from utils import *
from utils.checks import global_check


class VCroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vcroles = self.load_vcroles()
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help2_custom(self):
		      emoji = '<:soundfull:1087776969627811891>'
		      label = "VcRoles"
		      description = "Shows the VcRoles commands."
		      return emoji, label, description

    @commands.group()
    async def __VcRoles__(self, ctx: commands.Context):
        """`vcrole bots add`, `vcrole bots remove`, `vcrole bots`, `vcrole humans add`, `vcrole humans remove`, `vcrole humans`, `vcrole reset`, `vcrole config`, `vcrole`"""

    def load_vcroles(self):
        try:
            with open("jsons/vcroles.json", "r") as f:
                vcroles = json.load(f)
        except FileNotFoundError:
            vcroles = {}
        return vcroles

    def save_vcroles(self):
        with open("jsons/vcroles.json", "w") as f:
            json.dump(self.vcroles, f)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            await self.assign_roles(member, after.channel, member.bot)
        elif before.channel is not None and after.channel is None:
            await self.remove_roles(member, before.channel, member.bot)
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            await self.remove_roles(member, before.channel, member.bot)
            await self.assign_roles(member, after.channel, member.bot)

    async def assign_roles(self, member, channel, is_bot):
        guild_vcroles = self.vcroles.get(str(member.guild.id), {})
        if not guild_vcroles:
            return

        if is_bot:
            roles_to_assign = guild_vcroles.get("bots", [])
        else:
            roles_to_assign = guild_vcroles.get("humans", [])

        for role_id in roles_to_assign:
            role = member.guild.get_role(int(role_id))
            if role and role not in member.roles:
                if member.guild.me.guild_permissions.manage_roles:
                    try:
                        await member.add_roles(role, reason=f"Luka VC Roles (Joined VC)")
                    except discord.errors.Forbidden:
                        print(f"Bot lacks permission to assign role {role.name} in guild {member.guild.name}")
                    except Exception as e:
                        print(f"Error assigning role {role.name} to {member.display_name}: {e}")


    async def remove_roles(self, member, channel, is_bot):
        guild_vcroles = self.vcroles.get(str(member.guild.id), {})
        if not guild_vcroles:
            return

        if is_bot:
            roles_to_remove = guild_vcroles.get("bots", [])
        else:
            roles_to_remove = guild_vcroles.get("humans", [])

        for role_id in roles_to_remove:
            role = member.guild.get_role(int(role_id))
            if role and role in member.roles:
                if member.guild.me.guild_permissions.manage_roles:
                    try:
                        await member.remove_roles(role, reason=f"Luka VC Roles (Left VC)")
                    except discord.errors.Forbidden:
                        print(f"Bot lacks permission to remove role {role.name} in guild {member.guild.name}")
                    except Exception as e:
                        print(f"Error removing role {role.name} from {member.display_name}: {e}")


    @commands.group(name="vcrole", invoke_without_command=True)
    async def vcrole_group(self, ctx):
        embed = discord.Embed(
            title="**Luka | VC Roles Help**",
            description="Luka",
            color=0x977FD7
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
        embed.set_footer(text="Luka |")

        embed.add_field(
            name="📁 vcrole humans",
            value="Subcommands for human users.\n`add <role>` - Add role for humans\n`remove <role>` - Remove role from humans",
            inline=False
        )

        embed.add_field(
            name="🤖 vcrole bots",
            value="Subcommands for bot users.\n`add <role>` - Add role for bots\n`remove <role>` - Remove role from bots",
            inline=False
        )

        embed.add_field(
            name="🛠️ vcrole config",
            value="Displays current human & bot VC roles.",
            inline=False
        )

        embed.add_field(
            name="♻️ vcrole reset",
            value="Resets all VC role configurations.",
            inline=False
        )

        await ctx.send(embed=embed)


    @vcrole_group.group(name="humans")
    async def humans_group(self, ctx):
        pass

    @humans_group.command(name="add")
    async def add_human_role(self, ctx, role: discord.Role):
        guild_vcroles = self.vcroles.get(str(ctx.guild.id), {})
        human_roles = guild_vcroles.get("humans", [])

        if str(role.id) in human_roles:
            await ctx.send("Role is already in the list of vcroles for human users.")
            return

        human_roles.append(str(role.id))
        guild_vcroles["humans"] = human_roles
        self.vcroles[str(ctx.guild.id)] = guild_vcroles

        self.save_vcroles()

        await ctx.send(f"Added {role.name} to the list of vcroles for human users.")

    @humans_group.command(name="remove")
    async def remove_human_role(self, ctx, role: discord.Role):
        guild_vcroles = self.vcroles.get(str(ctx.guild.id), {})
        human_roles = guild_vcroles.get("humans", [])

        if str(role.id) not in human_roles:
            await ctx.send("Role is not in the list of vcroles for human users.")
            return

        human_roles.remove(str(role.id))
        guild_vcroles["humans"] = human_roles
        self.vcroles[str(ctx.guild.id)] = guild_vcroles

        self.save_vcroles()

        await ctx.send(f"Removed {role.name} from the list of vcroles for human users.")

    @vcrole_group.command(name="reset")
    async def reset_vcroles(self, ctx):
        self.vcroles[str(ctx.guild.id)] = {}

        self.save_vcroles()

        await ctx.send("VC Roles config has been reset for this server.")


    @vcrole_group.command(name="config")
    async def show_vcroles(self, ctx):
        guild_vcroles = self.vcroles.get(str(ctx.guild.id), {})
        human_roles = guild_vcroles.get("humans", [])
        bot_roles = guild_vcroles.get("bots", [])

        human_roles_str = ", ".join([f"<@&{r_id}>" for r_id in human_roles]) if human_roles else "None"
        bot_roles_str = ", ".join([f"<@&{r_id}>" for r_id in bot_roles]) if bot_roles else "None"

        msg = f"**VC Roles Config for {ctx.guild.name}:**\n\n"
        msg += f"Human Roles: {human_roles_str}\n"
        msg += f"Bot Roles: {bot_roles_str}"

        await ctx.send(msg)

    @vcrole_group.group(name="bots")
    async def bots_group(self, ctx):
        pass

    @bots_group.command(name="add")
    async def add_bot_role(self, ctx, role: discord.Role):
        guild_vcroles = self.vcroles.get(str(ctx.guild.id), {})
        bot_roles = guild_vcroles.get("bots", [])

        if str(role.id) in bot_roles:
            await ctx.send("Role is already in the list of vcroles for bot users.")
            return

        bot_roles.append(str(role.id))
        guild_vcroles["bots"] = bot_roles
        self.vcroles[str(ctx.guild.id)] = guild_vcroles

        self.save_vcroles()

        await ctx.send(f"Added {role.name} to the list of vcroles for bot users.")

    @bots_group.command(name="remove")
    async def remove_bot_role(self, ctx, role: discord.Role):
        guild_vcroles = self.vcroles.get(str(ctx.guild.id), {})
        bot_roles = guild_vcroles.get("bots", [])

        if str(role.id) not in bot_roles:
            await ctx.send("Role is not in the list of vcroles for bot users.")
            return

        bot_roles.remove(str(role.id))
        guild_vcroles["bots"] = bot_roles
        self.vcroles[str(ctx.guild.id)] = guild_vcroles

        self.save_vcroles()

        await ctx.send(f"Removed {role.name} from the list of vcroles for bot users.")

async def setup(bot):
    await bot.add_cog(VCroles(bot))