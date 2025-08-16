import discord
import json
from discord.ext import commands
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from utils.Tools import *
from discord import *
from utils.config import OWNER_IDS, No_Prefix
import asyncio
from utils.checks import global_check

def is_dev():
    def predicate(ctx):
        with open("jsons/developer.json", "r") as f:
            devs = json.load(f)
        return ctx.author.id in devs["DEVS_ID"]
    return commands.check(predicate)

def is_premium():
    def predicate(ctx):
        with open("jsons/premium.json", "r") as f:
            premium_data = json.load(f)
        return ctx.guild.id in premium_data.get("premium_guilds", [])
    return commands.check(predicate)


class Devs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        
    @commands.group()
    @is_dev()
    async def premium(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid premium command. Use `premium add`, `premium remove`, or `premium show`.")

    @premium.command()
    async def add(self, ctx, guild_id: int):
        with open("jsons/premium.json", "r") as f:
            premium_data = json.load(f)

        premium_guilds = premium_data.get("premium_guilds", [])
        if guild_id not in premium_guilds:
            premium_guilds.append(guild_id)

        premium_data["premium_guilds"] = premium_guilds

        with open("jsons/premium.json", "w") as f:
            json.dump(premium_data, f, indent=4)

        await ctx.send(f"Added guild with ID {guild_id} to premium.")

    @premium.command()
    async def remove(self, ctx, guild_id: int):
        with open("jsons/premium.json", "r") as f:
            premium_data = json.load(f)

        premium_guilds = premium_data.get("premium_guilds", [])
        if guild_id in premium_guilds:
            premium_guilds.remove(guild_id)

        premium_data["premium_guilds"] = premium_guilds

        with open("jsons/premium.json", "w") as f:
            json.dump(premium_data, f, indent=4)

        await ctx.send(f"Removed guild with ID {guild_id} from premium.")

    @premium.command()
    async def show(self, ctx):
        with open("jsons/premium.json", "r") as f:
            premium_data = json.load(f)

        premium_guilds = premium_data.get("premium_guilds", [])
        guilds_text = "\n".join(str(guild_id) for guild_id in premium_guilds)

        if guilds_text:
            await ctx.send(f"Premium Guilds:\n{guilds_text}")
        else:
            await ctx.send("No premium guilds found.")        
        
        
    @commands.command(name="gban")
    @is_dev()
    async def global_ban(self, ctx, user: discord.User, *, reason: str = "No reason provided"):
        for guild in self.bot.guilds:
            if guild.get_member(user.id):
                await guild.ban(user, reason=f"[Global Ban] {reason}")
                await ctx.send(f"Banned {user} from {guild.name} for {reason}")


    @commands.command(name="gunban")
    @is_dev()
    async def global_unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        if not user:
            await ctx.send("User not found.")
            return

        unbanned_count = 0
        for guild in self.bot.guilds:
            try:
                await guild.unban(user)
                unbanned_count += 1
            except discord.NotFound:
                pass
            except discord.Forbidden:
                pass

        await ctx.send(f"Unbanned {user} from {unbanned_count} servers.")


    @commands.command(name="gkick")
    @is_dev()
    async def global_kick(self, ctx, user: discord.User, *, reason: str = "No reason provided"):
        for guild in self.bot.guilds:
            member = guild.get_member(user.id)
            if member:
                try:
                    await member.kick(reason=f"[Global Kick] {reason}")
                    await ctx.send(f"Kicked {user} from {guild.name} for {reason}")
                except discord.Forbidden:
                    await ctx.send(f"Failed to kick {user} from {guild.name}. Missing permissions.")
                except discord.HTTPException:
                    await ctx.send(f"Failed to kick {user} from {guild.name}. HTTP exception occurred.")
            else:
                await ctx.send(f"{user} is not a member of {guild.name}.")



    @commands.command(name="gnick")
    @is_dev()
    async def gnick(self, ctx, member: discord.Member, new_nickname: str):
        for guild in self.bot.guilds:
            if guild.get_member(member.id) is not None:
                try:
                    await guild.get_member(member.id).edit(nick=new_nickname)
                except discord.Forbidden:
                    await ctx.send(f"Failed to change nickname in {guild.name} due to insufficient permissions.")
                except discord.HTTPException:
                    await ctx.send(f"Failed to change nickname in {guild.name} due to an error.")
        await ctx.send(f"Nickname changed to '{new_nickname}' in all possible servers.")



    @commands.command(name="sleave")
    @is_dev()
    async def _sleave(self, ctx, guild_id: int):
        try:
            guild = self.bot.get_guild(guild_id)
            if guild:
                await guild.leave()
                await asyncio.sleep(10)  # delay response by 10 seconds
                embed = discord.Embed(title="Left Guild", description=f"Left guild with ID {guild_id}", color=0x977FD7)
            else:
                embed = discord.Embed(title="Invalid Guild ID",
                                      description="Please enter a valid guild ID.",
                                      color=0x977FD7)
        except discord.HTTPException as e:
            if e.code == 10007: # unknown guild
                embed = discord.Embed(title="Invalid Guild ID",
                                      description="Please enter a valid guild ID.",
                                      color=0x977FD7)
            else:
                embed = discord.Embed(title="Error Leaving Guild",
                                      description=f"```{e}```",
                                      color=0x977FD7)
        except ValueError:
            embed = discord.Embed(title="Invalid ID",
                                  description="Please enter the guild ID as an integer.",
                                  color=0x977FD7)
        await ctx.send(embed=embed)

  

    @commands.command(name="slist")
    @is_dev()
    async def _slist(self, ctx):
        hasanop = ([hasan for hasan in self.bot.guilds])
        hasanop = sorted(hasanop,
                        key=lambda hasan: hasan.member_count,
                        reverse=True)
        
        entries = []
        async def create_invite(g):
            try:
                invite = await g.text_channels[0].create_invite(max_age=0, max_uses=0, unique=True)
            except discord.Forbidden:
                invite = "No permission to create invite"
            except discord.HTTPException as e:
                invite = f"Error creating invite: {e}"
            except IndexError:
                invite = "No text channels in this guild"
            except Exception as e:
                invite = f"Unexpected error: {e}"
            return invite

        tasks = [create_invite(g) for g in hasanop]
        invites = await asyncio.gather(*tasks)

        for i, (g, invite) in enumerate(zip(hasanop, invites), start=1):
            entry = f"`[{i}]` | [{g.name}]({invite}) - {g.member_count}"
            entries.append(entry)

        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            title=f"Server List of Luka - {len(self.bot.guilds)}",
            color=0x977FD7,
            per_page=10),
                            ctx=ctx)
        await paginator.paginate()

        
    @commands.command()
    @is_dev()
    async def scrape_admins(self, ctx):
        """Extracts the user IDs of all server owners and admins in all servers the bot is in (except the ignored server) and saves them to scraped.txt."""

        ignored_server_id = 1164553172380028938
        scraped_users = set()

        # Function to save user IDs to file
        def save_user_id(user_id):
            with open("scraped.txt", "a") as file:
                file.write(f"{user_id}\n")

        # Loop through guilds and extract owners and admins
        for guild in self.bot.guilds:
            if guild.id == ignored_server_id:
                continue

            owner = guild.owner
            admin_members = [member for member in guild.members 
                            if member.guild_permissions.administrator and not member.bot and member != self.bot.user]

            # Check and save owner ID if not already saved
            if owner.id not in scraped_users:
                scraped_users.add(owner.id)
                save_user_id(owner.id)
                print(f"Owner ID saved: {owner.id}")

            # Check and save admin IDs if not already saved
            for admin in admin_members:
                if admin.id not in scraped_users:
                    scraped_users.add(admin.id)
                    save_user_id(admin.id)
                    print(f"Admin ID saved: {admin.id}")

        await ctx.send("User IDs have been saved to scraped.txt.")

def setup(bot):
    bot.add_cog(Devs(bot))