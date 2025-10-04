import discord
from discord.ext import commands
import json
from utils.Tools import *
from utils.checks import global_check

class Autorespond(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autoresponses = {}
        self.max_responses = 5
        self.load_autoresponses()
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help2_custom(self):
		      emoji = '<:audio:1089139281441861764>'
		      label = "Autorespond"
		      description = "Shows the autorespond commands."
		      return emoji, label, description

    @commands.group()
    async def __autorespond1__(self, ctx: commands.Context):
        """`autoresponder create`, `autoresponder delete`, `autoresponder config`, `autoresponder edit`"""

    def load_autoresponses(self):
      try:
          with open('jsons/autor.json', 'r') as f:
              self.autoresponses = json.load(f)
      except FileNotFoundError:
          self.autoresponses = {}


    def save_autoresponses(self):
      with open('jsons/autor.json', 'w') as f:
          json.dump(self.autoresponses, f, indent=4)


    @commands.hybrid_group(name="autoresponder",
                    description='Shows the autoresponder subcommands.',
                    invoke_without_command=True,
                    aliases=['ar'])
    async def _ar(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @_ar.command(name="create",
                description='Create some autoresponses.')
    @commands.has_permissions(administrator=True)
    async def _create(self, ctx, name, *, message):
        with open("jsons/autor.json", "r") as f:
            autoresponse = json.load(f)
        numbers = []
        if str(ctx.guild.id) in autoresponse:
            for autoresponsecount in autoresponse[str(ctx.guild.id)]:
                numbers.append(autoresponsecount)
            if len(numbers) >= 20:
                hacker6 = discord.Embed(
                    title="Luka",
                    description=
                    f"<:info:1087776877898383400> You can\\'t add more than 20 autoresponses in {ctx.guild.name}",
                    color=0x977FD7)
                hacker6.set_author(name=f"{ctx.author}",
                                   icon_url=f"{ctx.author.display_avatar.url}")
                hacker6.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
                return await ctx.send(embed=hacker6)
        if str(ctx.guild.id) in autoresponse:
            if name in autoresponse[str(ctx.guild.id)]:
                hacker = discord.Embed(
                    title="Luka",
                    description=
                    f"<:info:1087776877898383400> The autoresponse with the `{name}` is already in {ctx.guild.name}",
                    color=0x977FD7)
                hacker.set_author(name=f"{ctx.author}",
                                  icon_url=f"{ctx.author.display_avatar.url}")
                hacker.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
                return await ctx.send(embed=hacker)
        if str(ctx.guild.id) in autoresponse:
            autoresponse[str(ctx.guild.id)][name] = message
            with open("jsons/autor.json", "w") as f:
                json.dump(autoresponse, f, indent=4)
            hacker1 = discord.Embed(
                title="Luka",
                description=
                f"<:check:1087776909246607360> | Successfully Created Autoresponder in {ctx.guild.name} with the `{name}`",
                color=0x977FD7)
            hacker1.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.display_avatar.url}")
            hacker1.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
            return await ctx.reply(embed=hacker1)

        data = {
            name: message,
        }
        autoresponse[str(ctx.guild.id)] = data

        with open("jsons/autor.json", "w") as f:
            json.dump(autoresponse, f, indent=4)
            hacker2 = discord.Embed(
                title="Luka",
                description=
                f"<:check:1087776909246607360> | Successfully Created Autoresponder  in {ctx.guild.name} with the `{name}`",
                color=0x977FD7)
            hacker2.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.display_avatar.url}")
            hacker2.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
            return await ctx.reply(embed=hacker2)

    @_ar.command(name="delete",
                description='Delete a particular autoresponder.')
    @commands.has_permissions(administrator=True)
    async def _delete(self, ctx, name):
        with open("jsons/autor.json", "r") as f:
            autoresponse = json.load(f)

        if str(ctx.guild.id) in autoresponse:
            if name in autoresponse[str(ctx.guild.id)]:
                del autoresponse[str(ctx.guild.id)][name]
                with open("jsons/autor.json", "w") as f:
                    json.dump(autoresponse, f, indent=4)
                hacker1 = discord.Embed(
                    title="Luka",
                    description=
                    f"<:check:1087776909246607360> | Successfully Deleted Autoresponder in {ctx.guild.name} with the `{name}`",
                    color=0x977FD7)
                hacker1.set_author(name=f"{ctx.author}",
                                   icon_url=f"{ctx.author.display_avatar.url}")
                hacker1.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
                return await ctx.reply(embed=hacker1)
            else:
                hacker = discord.Embed(
                    title="Luka",
                    description=
                    f"<:info:1087776877898383400> No Autoresponder Found With The Name `{name}` In {ctx.guild.name}",
                    color=0x977FD7)
                hacker.set_author(name=f"{ctx.author}",
                                  icon_url=f"{ctx.author.display_avatar.url}")
                hacker.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
                return await ctx.reply(embed=hacker)
        else:
            hacker2 = discord.Embed(
                title="Luka",
                description=
                f"<:info:1087776877898383400> There is no Autoresponder in {ctx.guild.name}",
                color=0x977FD7)
            hacker2.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.display_avatar.url}")
            hacker2.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
            return await ctx.reply(embed=hacker2)

    @_ar.command(name="config",
                description='Shows the autoresponder config.')
    @commands.has_permissions(administrator=True)
    async def _config(self, ctx):
        with open("jsons/autor.json", "r") as f:
            autoresponse = json.load(f)
        autoresponsenames = []
        guild = ctx.guild
        if str(ctx.guild.id) in autoresponse:
            for autoresponsecount in autoresponse[str(ctx.guild.id)]:
                autoresponsenames.append(autoresponsecount)
            embed = discord.Embed(color=0x977FD7)
            st, count = "", 1
            for autoresponse in autoresponsenames:
                st += f"`{'0' + str(count) if count < 20 else count}. `    **{autoresponse.upper()}**\n"
                test = count
                count += 1

                embed.title = f"{test} Autoresponders In {guild}"
            embed.description = st
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.display_avatar.url}")
            embed.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
            await ctx.send(embed=embed)

    @_ar.command(name="edit",
                description='Edit a particular autoresponder.')
    @commands.has_permissions(administrator=True)
    async def _edit(self, ctx, name, *, message):
        with open("jsons/autor.json", "r") as f:
            autoresponse = json.load(f)
        if str(ctx.guild.id) in autoresponse:
            if name in autoresponse[str(ctx.guild.id)]:
                autoresponse[str(ctx.guild.id)][name] = message
                with open("jsons/autor.json", "w") as f:
                    json.dump(autoresponse, f, indent=4)
                hacker1 = discord.Embed(
                    title="Luka",
                    description=
                    f"<:check:1087776909246607360> | Successfully Edited Autoresponder in {ctx.guild.name} with the `{name}`",
                    color=0x977FD7)
                hacker1.set_author(name=f"{ctx.author}",
                                   icon_url=f"{ctx.author.display_avatar.url}")
                hacker1.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
                return await ctx.send(embed=hacker1)
        else:
            hacker2 = discord.Embed(
                title="Luka",
                description=
                f"<:info:1087776877898383400> No Autoresponder Found With The Name `{name}` In {ctx.guild.name}",
                color=0x977FD7)
            hacker2.set_author(name=f"{ctx.author}",
                               icon_url=f"{ctx.author.display_avatar.url}")
            hacker2.set_thumbnail(url=f"{ctx.author.display_avatar.url}")
            return await ctx.send(embed=hacker2)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        guild_id = str(message.guild.id)
        if guild_id in self.autoresponses:
            trigger = message.content.lower()
            if trigger in self.autoresponses[guild_id]:
                response = self.autoresponses[guild_id][trigger]
                await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(Autorespond(bot))