from discord.ext import commands
from core import Luka, Cog
import discord, requests
import json
from utils.Tools import *
from discord.ui import View, Button

bled = [110373943822540800,
        997499786380972122,
        9953967096805593128]

class Guild(Cog):
    def __init__(self, client: Luka):
        self.client = client

    @commands.Cog.listener(name="on_guild_join")
    async def on_guild_join(self, guild):
        # First listener logic
        embed = discord.Embed(title="Luka | New Server", color=0x977FD7)
        embed.add_field(name="Name", value=str(guild.name), inline=False)

        # Safe invite fetching
        invite = await guild.vanity_invite()
        if not invite:
            try:
                invites = await guild.invites()
                for inv in invites:
                    if inv.max_age == 0 and inv.max_uses == 0:
                        invite = inv
                        break
            except discord.Forbidden:
                pass # Can't get invites, oh well

        me = self.client.get_channel(1063498287971323995)
        embed.add_field(name="Member Count", value=f"{guild.member_count} Member(s)", inline=False)
        embed.add_field(name="Owner", value=f"[{guild.owner}](https://discord.com/users/{guild.owner_id})", inline=False)
        embed.add_field(name="Server ID", value=str(guild.id), inline=False)
        embed.add_field(name="Invite", value=f"[here]({invite.url})" if invite else "No Invite Found", inline=False)
        if me:
            await me.send(embed=embed)

        # Second listener logic
        with open('jsons/vanity.json', 'r') as f:
            vanity = json.load(f)
        vanity[str(guild.id)] = guild.vanity_url_code if guild.vanity_url_code else ""
        with open('jsons/vanity.json', 'w') as f:
            json.dump(vanity, f, indent=4)

    @commands.Cog.listener(name="on_guild_remove")
    async def on_g_remove(self, guild):
        await self.client.wait_until_ready()
        idk = self.client.get_channel(1063498287971323995)
        if idk:
            embed = discord.Embed(title="Luka | Got Removed", color=0x977FD7)
            embed.add_field(name="Name", value=str(guild.name), inline=False)
            embed.add_field(name="Member Count", value=f"{guild.member_count} Member(s)", inline=False)
            embed.add_field(name="Owner", value=f"[{guild.owner}](https://discord.com/users/{guild.owner_id})", inline=False)
            await idk.send(embed=embed)
        with open('jsons/vanity.json', 'r') as f:
            vanity = json.load(f)

        if str(guild.id) in vanity:
            vanity.pop(str(guild.id))

        with open('jsons/vanity.json', 'w') as f:
            json.dump(vanity, f, indent=4)

async def setup(bot):
    await bot.add_cog(Guild(bot))