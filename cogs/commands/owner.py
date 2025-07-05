from __future__ import annotations
from discord.ext import commands
from utils.Tools import *
from utils.config import OWNER_IDS, No_Prefix
import json
import discord
import typing
from typing import Optional
import asyncio
import pymongo


# Replace the connection link, database, and collection names accordingly
MONGO_LINK = "mongodb+srv://hitman25:luka.123@cluster0.xlxhrlj.mongodb.net/"
DATABASE_NAME = "info"
COLLECTION_NAME = "infodata"

# Initialize the MongoDB client and database
mongo_client = pymongo.MongoClient(MONGO_LINK)
db = mongo_client[DATABASE_NAME]
collection = db[COLLECTION_NAME]


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.blacklist_file = 'jsons/blacklistg.json'
        self.load_blacklist()

    def load_blacklist(self):
        try:
            with open(self.blacklist_file, 'r') as f:
                self.blacklist = json.load(f)
        except FileNotFoundError:
            self.blacklist = []

    def save_blacklist(self):
        with open(self.blacklist_file, 'w') as f:
            json.dump(self.blacklist, f)


# https://cdn.discordapp.com/avatars/974984890959425566/7fedaa654af7ec62b211033852e048d0.webp?size=2048


    @commands.command(name="restart", help="Restarts the bot.")
    @commands.is_owner()
    async def _restart(self, ctx: Context):
        await ctx.reply("System restart initiated. Please wait while we optimize and realign key components for peak performance.")
        restart_program()

    @commands.command(name="sync", help="Syncs all database.")
    @commands.is_owner()
    async def _sync(self, ctx: Context):
        await ctx.reply("Syncing...", mention_author=False)
        with open('jsons/anti.json', 'r') as f:
            data = json.load(f)
        for guild in self.client.guilds:
            if str(guild.id) not in data['guild']:
                data['guilds'][str(guild.id)] = 'on'
                with open('jsons/anti.json', 'w') as f:
                    json.dump(data, f, indent=4)
            else:
                pass
        with open('jsons/config.json', 'r') as f:
            data = json.load(f)
        for op in data["guilds"]:
            g = self.client.get_guild(int(op))
            if not g:
                data["guilds"].pop(str(op))
                with open('jsons/config.json', 'w') as f:
                    json.dump(data, f, indent=4)

    @commands.group(name="blacklist", help="let's you add someone in blacklist", aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        if ctx.invoked_subcommand is None:
            with open("jsons/blacklist.json") as file:
                blacklist = json.load(file)
                embed = discord.Embed(
                    title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
                    description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                    color=0x977FD7
                )
                # embed.set_thumbnail(url = "https://cdn.discordapp.com/avatars/977023331117199481/b0270586b291c69b396cd5a24aa11aff.webp?size=2048")
                await ctx.reply(embed=embed, mention_author=False)

    @blacklist.command(name="add")
    @commands.is_owner()
    async def blacklist_add(self, ctx, member: discord.Member):
        try:
            with open('jsons/blacklist.json', 'r') as bl:
                blacklist = json.load(bl)
                if str(member.id) in blacklist["ids"]:
                    embed = discord.Embed(
                        title="Error!", description=f"{member.name} is already blacklisted", color=0x977FD7)
                    await ctx.reply(embed=embed, mention_author=False)
                else:
                    add_user_to_blacklist(member.id)
                    embed = discord.Embed(
                        title="Blacklisted", description=f"<:check:1087776909246607360> | Successfully Blacklisted {member.name}", color=0x977FD7)
                    with open("jsons/blacklist.json") as file:
                        blacklist = json.load(file)
                        embed.set_footer(
                            text=f"There are now {len(blacklist['ids'])} users in the blacklist"
                        )
                        await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**An Error Occurred**",
                color=0x977FD7
            )
            # embed.set_thumbnail(url = "https://cdn.discordapp.com/avatars/977023331117199481/b0270586b291c69b396cd5a24aa11aff.webp?size=2048")
            await ctx.reply(embed=embed, mention_author=False)

    @blacklist.command(name="remove")
    @commands.is_owner()
    async def blacklist_remove(self, ctx, member: discord.Member = None):
        try:
            remove_user_from_blacklist(member.id)
            embed = discord.Embed(
                title="User removed from blacklist",
                description=f"<:check:1087776909246607360> | **{member.name}** has been successfully removed from the blacklist",
                color=0x977FD7
            )
            with open("jsons/blacklist.json") as file:
                blacklist = json.load(file)
                embed.set_footer(
                    text=f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await ctx.reply(embed=embed, mention_author=False)
        except:
            embed = discord.Embed(
                title="Error!",
                description=f"**{member.name}** is not in the blacklist.",
                color=0x977FD7
            )
           # embed.set_thumbnail(url = "https://cdn.discordapp.com/avatars/977023331117199481/b0270586b291c69b396cd5a24aa11aff.webp?size=2048")
            await ctx.reply(embed=embed, mention_author=False)

    @commands.group(name='blacklistg')
    @commands.is_owner()
    async def blacklistg(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid blacklistg command passed...')

    @blacklistg.command()
    async def add(self, ctx, guild_id: int):
        if guild_id not in self.blacklist:
            self.blacklist.append(guild_id)
            self.save_blacklist()
            embed = discord.Embed(
                title=f'Guild with ID {guild_id} has been added to the blacklist.', color=0x977FD7)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f'Guild with ID {guild_id} is already in the blacklist.', color=0x977FD7)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await ctx.send(embed=embed)

    @blacklistg.command()
    async def remove(self, ctx, guild_id: int):
        if guild_id in self.blacklist:
            self.blacklist.remove(guild_id)
            self.save_blacklist()
            embed = discord.Embed(
                title=f'Guild with ID {guild_id} has been removed from the blacklist.', color=0x00ff00)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f'Guild with ID {guild_id} is not in the blacklist.', color=0x977FD7)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await ctx.send(embed=embed)

    @blacklistg.command()
    async def show(self, ctx):
        if not self.blacklist:
            embed = discord.Embed(
                title='The blacklist is empty.', color=0x977FD7)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Blacklisted guilds', description=", ".join(
                map(str, self.blacklist)), color=0x977FD7)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.id in self.blacklist:
            log_channel = self.client.get_channel(1108100644490977320)
            embed = discord.Embed(
                title=f'Blacklisted guild detected: {guild.name} ({guild.id}). Leaving in 5 seconds...', color=0x977FD7)
            thumbnail = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text='Blacklist Log')
            await log_channel.send(embed=embed)
            await asyncio.sleep(5)
            await guild.leave()

    @commands.group(name="np", help="Allows you to add someone in no prefix list (owner only command)")
    @commands.is_owner()
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="add", help="Add user to no prefix")
    @commands.is_owner()
    async def np_add(self, ctx, user: discord.User):
        user_id = str(user.id)
        result = collection.find_one({"_id": "np"})
        if result is not None and user_id in result["users"]:
            embed = discord.Embed(
                title="Luka",
                description=f"**The User You Provided Already In My No Prefix**",
                color=0x977FD7
            )
            await ctx.reply(embed=embed)
        else:
            collection.update_one(
                {"_id": "np"},
                {"$push": {"users": user_id}},
                upsert=True
            )
            embed1 = discord.Embed(
                title="Luka",
                description="<:check:1087776909246607360> | {0} has been added to the **no prefix** successfully!".format(user),
                color=0x977FD7
            )
            await ctx.reply(embed=embed1)

    @_np.command(name="remove", help="Remove user from no prefix")
    @commands.is_owner()
    async def np_remove(self, ctx, user: discord.User):
        user_id = str(user.id)
        result = collection.find_one({"_id": "np"})
        if result is None or user_id not in result["users"]:
            embed = discord.Embed(
                title="Luka",
                description="**{} is not in no prefix!**".format(user),
                color=0x977FD7
            )
            await ctx.reply(embed=embed)
        else:
            collection.update_one(
                {"_id": "np"},
                {"$pull": {"users": user_id}},
            )
            embed2 = discord.Embed(
                title="Luka",
                description="<:check:1087776909246607360> | {0} has been removed from the **no prefix** successfully!".format(user),
                color=0x977FD7
            )
            await ctx.reply(embed=embed2)

    @commands.group(name="bdg", help="Allows owner to add badges for a user")
    @commands.is_owner()
    async def _badge(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_badge.command(name="add", aliases=["give"], help="Add some badges to a user.")
    @commands.is_owner()
    async def badge_add(self, ctx, member: discord.Member, *, badge: str):
        ok = getbadges(member.id)
        badge_dict = {
            "own": "**<:OwnerIcon:1040661621174976563>ㆍOwner**",
            "owner": "**<:OwnerIcon:1040661621174976563>ㆍOwner**",
            "king": "**<:OwnerIcon:1040661621174976563>ㆍOwner**",
            "staff": "**<:pain_GoldModbadge:1040661622055776296>ㆍStaff**",
            "support staff": "**<:pain_GoldModbadge:1040661622055776296>ㆍStaff**",
            "partner": "**<a:rnx_partner:1040661854957092936>ㆍPartner**",
            "sponsor": "**<a:IconServerSecurity:1062704897679700049>ㆍSponsor**",
            "friend": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "friends": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "homies": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "owner's friend": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "early": "**<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter**",
            "supporter": "**<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter**",
            "support": "**<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter**",
            "vip": "**<:pain_vip:1062704229426409563>ㆍVip**",
            "bug": "**<:lnl_bug_hunter:1040662458047672443>ㆍBug Hunter**",
            "hunter": "**<:lnl_bug_hunter:1040662458047672443>ㆍBug Hunter**",
            "all": "**<:OwnerIcon:1040661621174976563>ㆍOwner\n<:pain_GoldModbadge:1040661622055776296>ㆍStaff\n<a:rnx_partner:1040661854957092936>ㆍPartner\n<a:IconServerSecurity:1062704897679700049>ㆍSponsor\n<:Friendship:1062705075396546652>ㆍOwner`s Friends\n<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter\n<:pain_vip:1062704229426409563>ㆍVip\n<:lnl_bug_hunter:1040662458047672443>ㆍBug Hunter**"
        }

        if badge.lower() == "all":
            all_badges = {badge_dict[key] for key in badge_dict if key != "all"}
            current_badges = set(ok)
            new_badges = all_badges - current_badges
            if not new_badges:
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:x:1087776909246607360> | **{member} already has all badges**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
            else:
                ok.extend(list(new_badges))
                makebadges(member.id, ok)
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:check:1087776909246607360> | **Successfully Added All Badges To {member}**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
        elif badge.lower() in badge_dict:
            idk = badge_dict[badge.lower()]
            if idk in ok:
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:x:1087776909246607360> | **{member} already has the `{badge}` badge**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
            else:
                ok.append(idk)
                makebadges(member.id, ok)
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:check:1087776909246607360> | **Successfully Added `{badge}` Badge To {member}**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="Luka",
                description="**Invalid Badge**",
                color=0x977FD7
            )
            await ctx.reply(embed=embed)


    @_badge.command(name="remove", help="Remove badges from a user.", aliases=["re"])
    @commands.is_owner()
    async def badge_remove(self, ctx, member: discord.Member, *, badge: str):
        ok = getbadges(member.id)
        badge_dict = {
            "own": "**<:OwnerIcon:1040661621174976563>ㆍOwner**",
            "owner": "**<:OwnerIcon:1040661621174976563>ㆍOwner**",
            "king": "**<:OwnerIcon:1040661621174976563>ㆍOwner**",
            "staff": "**<:pain_GoldModbadge:1040661622055776296>ㆍStaff**",
            "support staff": "**<:pain_GoldModbadge:1040661622055776296>ㆍStaff**",
            "partner": "**<a:rnx_partner:1040661854957092936>ㆍPartner**",
            "sponsor": "**<a:IconServerSecurity:1062704897679700049>ㆍSponsor**",
            "friend": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "friends": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "homies": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "owner's friend": "**<:Friendship:1062705075396546652>ㆍOwner`s Friends**",
            "early": "**<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter**",
            "supporter": "**<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter**",
            "support": "**<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter**",
            "vip": "**<:pain_vip:1062704229426409563>ㆍVip**",
            "bug": "**<:lnl_bug_hunter:1040662458047672443>ㆍBug Hunter**",
            "hunter": "**<:lnl_bug_hunter:1040662458047672443>ㆍBug Hunter**",
            "all": "**<:OwnerIcon:1040661621174976563>ㆍOwner\n<:pain_GoldModbadge:1040661622055776296>ㆍStaff\n<a:rnx_partner:1040661854957092936>ㆍPartner\n<a:IconServerSecurity:1062704897679700049>ㆍSponsor\n<:Friendship:1062705075396546652>ㆍOwner`s Friends\n<a:pain_moon_early:1062705249107853424>ㆍEarly Supporter\n<:pain_vip:1062704229426409563>ㆍVip\n<:lnl_bug_hunter:1040662458047672443>ㆍBug Hunter**"
        }

        if badge.lower() == "all":
            if not ok:
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:x:1087776909246607360> | **{member} does not have any badges to remove**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
            else:
                ok.clear()
                makebadges(member.id, ok)
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:check:1087776909246607360> | **Successfully Removed All Badges From {member}**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
        elif badge.lower() in badge_dict:
            idk = badge_dict[badge.lower()]
            if idk not in ok:
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:x:1087776909246607360> | **{member} does not have the `{badge}` badge**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
            else:
                ok.remove(idk)
                makebadges(member.id, ok)
                embed = discord.Embed(
                    title="Luka",
                    description=f"<:check:1087776909246607360> | **Successfully Removed `{badge}` Badge From {member}**",
                    color=0x977FD7
                )
                await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="Luka",
                description="**Invalid Badge**",
                color=0x977FD7
            )
            await ctx.reply(embed=embed)



    @commands.command(name="syncs", help="Syncs Slash Commands.")
    @commands.is_owner()
    async def _sync(self, ctx) -> None:
        fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(
            f"Synced {len(fmt)} commands to the current guild."
        )
        channel = await ctx.message.author.create_dm()
        await channel.send('Slash commands synced!')
        return

    @commands.command(help="Make the bot say something in a given channel.")
    @commands.is_owner()
    async def say(self, ctx: commands.Context, channel_id: int, *, message):
        channel = self.bot.get_channel(channel_id)
        guild = channel.guild
        channel = await ctx.message.author.create_dm()
        await ctx.send(f"Sending message to **{guild}** <#{channel.id}>\n> {message}")
        await channel.send(message)
