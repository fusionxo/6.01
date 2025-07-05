import discord
from discord.ext import commands
import json
from utils.Tools import *

class VanityRoles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command(description="Setup vanity roles.", aliases=["vrsetup"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def vr_setup(self, ctx, vanity, role: discord.Role, channel: discord.TextChannel):
        with open("jsons/vanityroles.json", "r") as f:
            idk = json.load(f)
        if role.permissions.administrator or role.permissions.ban_members or role.permissions.kick_members:
            await ctx.send(f'<:info:1087776877898383400> | You cannot use roles with administrator, ban, or kick members permission.')
        else:
            pop = {"vanity": vanity, "role": role.id, "channel": channel.id}
            idk[str(ctx.guild.id)] = pop
            embed=discord.Embed(color=discord.Colour(0x977FD7), description=f"Vanity: {vanity}\nRole: {role.mention}\nChannel: {channel.mention}")
            await ctx.reply(embed=embed, mention_author=False)
        with open('jsons/vanityroles.json', 'w') as f:
            json.dump(idk, f, indent=4)

    @commands.hybrid_command(description="Show vanity roles config.", aliases=["vrshow"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def vr_show(self, ctx):
        with open("jsons/vanityroles.json", "r") as f:
            jnl = json.load(f)
        if str(ctx.guild.id) not in jnl:
            await ctx.reply(f"Setup vanity roles using `,vrsetup`", mention_author=False)
        else:
            vanity = jnl[str(ctx.guild.id)]["vanity"]
            role = jnl[str(ctx.guild.id)]["role"]
            channel = jnl[str(ctx.guild.id)]["channel"]
            gchannel = self.client.get_channel(channel)
            grole = ctx.guild.get_role(role)
            embed=discord.Embed(color=discord.Colour(0x977FD7), description=f"Vanity: {vanity}\nRole: {grole.mention}\nChannel: {gchannel.mention}")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.command(description="Remove vanity roles.", aliases=["vrremove"])
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def vr_remove(self, ctx):
        with open("jsons/vanityroles.json", "r") as f:
            jnl = json.load(f)
            if str(ctx.guild.id) not in jnl:
                await ctx.reply(f"Setup vanity roles using `,vrsetup`", mention_author=False)
            else:
                jnl.pop(str(ctx.guild.id))
                await ctx.reply(f"<:check:1087776909246607360> | Removed the vanity roles system from this server.", mention_author=False)
        with open('jsons/vanityroles.json', 'w') as f:
            json.dump(jnl, f, indent=4) 

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        with open("jsons/vanityroles.json", "r") as f:
            jnl = json.load(f)
        if str(before.guild.id) not in jnl:
            return
        elif str(before.guild.id) in jnl:
            vanity = jnl[str(before.guild.id)]["vanity"]
            role = jnl[str(before.guild.id)]["role"]
            channel = jnl[str(before.guild.id)]["channel"]
            if str(before.raw_status) == "offline":
                return
            else:
                aft = after.activities[0].name if after.activities else None
                bef = before.activities[0].name if before.activities else None
                if aft and vanity in aft:
                    try:
                        if bef is None or vanity not in bef:
                            gchannel = self.client.get_channel(channel)
                            grole = after.guild.get_role(role)
                            await after.add_roles(grole, reason="- Added vanity in status")
                            embed = discord.Embed(title=f"New Vanity Status!", description=f"{after.mention}, Thank you for showing support for `{vanity}` in your status! ❤️ Your support means a lot to us and helps us grow. We truly appreciate it and hope that you continue to enjoy our community. Thank you again!", color=0xFFC0CB)
                            await gchannel.send(embed=embed)
                    except Exception as e:
                        print(e)
                elif bef and vanity in bef:
                    try:
                        gchannel = self.client.get_channel(channel)
                        grole = after.guild.get_role(role)
                        await after.remove_roles(grole, reason="- Removed vanity from status")
                    except Exception as e:
                        print(e)

