import discord
from discord.ext import commands
from difflib import get_close_matches
from contextlib import suppress
from core import Context
from core.Luka import Luka
from core.Cog import Cog
from utils.Tools import getConfig
from itertools import chain
import json
from utils import help as vhelp
from core import *
from utils.Tools import *


client = Luka()


color=0x977FD7




class HelpCommand(commands.HelpCommand):
  async def on_help_command_error(self, ctx, error):
    damn = [commands.CommandOnCooldown, 
           commands.CommandNotFound, discord.HTTPException, 
           commands.CommandInvokeError]
    if not type(error) in damn:
      await self.context.reply(f"Unknown Error Occurred\n{error.original}", mention_author=False)
    else:
      if type(error) == commands.CommandOnCooldown:
        return
      
        return await super().on_help_command_error(ctx, error)

  async def command_not_found(self, string: str) -> None:
    with open('jsons/blacklist.json', 'r') as f:
      bldata = json.load(f)
    data = getIgnore(self.context.guild.id)
    ch = data["channel"]
    iuser = data["user"]
    buser = data["excludeuser"]      
    bl = discord.Embed(description="You are blacklisted from using my commannds.\nreason could be excessive use or spamming commands\nJoin our [Support Server]( https://bit.ly/luka-support) to appeal .", color=0x977FD7)
    embed = discord.Embed(description="This Channel is in ignored channel list try my commands in another channel .", color=0x977FD7)
    ign = discord.Embed(description=f"You are set as a ignored users for {self.context.guild.name} .\nTry my commands or modules in another guild .", color=0x977FD7)

    if str(self.context.author.id) in bldata["ids"]:
      return 
    
    if str(self.context.author.id) in iuser and str(self.context.author.id) not in buser: 
      return 

    if self.context.channel.id in ch and self.context.author.id not in buser:
        return
    else:
      

      if string in ("security", "anti", ""):
        cog = self.context.bot.get_cog("Antinuke")
        with suppress(discord.HTTPException):
          await self.send_cog_help(cog)
      elif string in ("oknchhfehheng3g"):
        cog = self.context.bot.get_cog("Games")
        with suppress(discord.HTTPException):
          await self.send_cog_help(cog)
      else:
        msg = f"Command `{string}` is not found...\n"
        cmds = (str(cmd) for cmd in self.context.bot.walk_commands())
        mtchs = get_close_matches(string, cmds)
        if mtchs:
          for okaay, okay in enumerate(mtchs, start=1):
            msg += f"Did You Mean: \n`[{okaay}]`. `{okay}`\n"
        embed1 = discord.Embed(color=0x977FD7,title=f"Command `{string}` is not found...\n",description=f"Did You Mean: \n`[{okaay}]`. `{okay}`\n")
        embed1.set_footer(name="Made with 💖 by LUKA#5191", icon_url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
        return embed1

  
  async def send_bot_help(self, mapping):
    await self.context.typing()
    with open('jsons/blacklist.json', 'r') as f:
      bled = json.load(f)
    data = getIgnore(self.context.guild.id)
    ch = data["channel"]
    iuser = data["user"]
    buser = data["excludeuser"]
    bl = discord.Embed(description="You are blacklisted from using my commannds.\nreason could be excessive use or spamming commands\nJoin our [Support Server]( https://bit.ly/luka-support) to appeal .", color=0x977FD7)
    embed = discord.Embed(description="This Channel is in ignored channel list try my commands in another channel .", color=0x977FD7)
    ign = discord.Embed(description=f"You are set as a ignored users for {self.context.guild.name} .\nTry my commands or modules in another guild .", color=0x977FD7)

    if str(self.context.author.id) in bled["ids"]:
      return 
    
    if str(self.context.author.id) in iuser and str(self.context.author.id) not in buser: 
      return 

    if self.context.channel.id in ch and self.context.author.id not in buser:
        return
    
    data = getConfig(self.context.guild.id)
    prefix = data["prefix"]
    perms = discord.Permissions.none()
    perms.read_messages = True
    perms.external_emojis = True
    perms.send_messages = True
    perms.manage_roles = True
    perms.manage_channels = True
    perms.ban_members = True
    perms.kick_members = True
    perms.manage_messages = True
    perms.embed_links = True
    perms.read_message_history = True
    perms.attach_files = True
    perms.add_reactions = True
    perms.administrator = True
    inv = discord.utils.oauth_url(self.context.bot.user.id, permissions=perms)
    embed = discord.Embed(
        title="Overview of Help Command:",
        description=(
            f"<:dot:1088106350904610827> The server prefix is `{prefix}`\n"
            f"<:dot:1088106350904610827> Use `{prefix}help <command | module>` for more info.\n"
            f"<:dot:1088106350904610827> Total `{len(set(self.context.bot.walk_commands()))}` Commands Available.\n"
            f"```ansi\n"
            f"\u001b[2;34m<> \u001b[0m - \u001b[2;45mMandatory Parameter\u001b[0m | \u001b[2;34m() \u001b[0m - \u001b[2;45mOptional Parameter\u001b[0m"
            f"```"
        ),
        color=0x977FD7
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
   
    embed.set_footer(
        text="Made with 💖 by LUKA#5191",
        icon_url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png"
    )
    embed.set_author(
        name=self.context.author.name,
        icon_url=self.context.author.display_avatar.url
    )
    embed.timestamp = discord.utils.utcnow()

    # Main Module
    main_module_fields = [
        ("<:search:1088438737727406142>", "General"),
        ("<:music:1088440414744367194>", "Music"),
        ("<:usershield:1087776624486920294>", "Moderation"),
        ("<:securitylock:1087776659396116501>", "Security"),
        ("<:l0ck:1087776868444409917>", "Automod"),
        ("<:logging:1088442287115219087>", "Logging"),
        ("<:welcome:1088445113417605150>", "Welcome"),
        ("<:fun:1088451095795351672>", "Fun"),
        ("<:games:1088451606049198091>", "Games"),
        ("<:autom:1088452318376239114>", "Extra")
    ]

    # Extra Module
    extra_module_fields = [
        ("<:media:1089136852100980806>", "Media"),
        ("<:sstar:1089111407712276580>", "Starboard"),
        ("<:love:1089116684046041158>", "Vanity"),
        ("<:soundfull:1087776969627811891>", "VCRoles"),
        ("<:note:1089137995426308102>", "TextToEmoji"),
        ("<:tiicket:1089113691082993674>", "Ticket"),
        ("<:giftbox:1087776608154304522>", "Giveaway"),
        ("<:dice:1087776927659602030>", "CustomRole"),
        ("<:audio:1089139281441861764>", "Soundboard"),
        ("<:automation:1089140152674308126>", "Autoresponse")
    ]

    # Add fields to embed
    embed.add_field(
        name="__Main Module__",
        value="\n".join([f"{icon} : **{name}**" for icon, name in main_module_fields]),
        inline=True
    )
    embed.add_field(
        name="__Extra Module__",
        value="\n".join([f"{icon} : **{name}**" for icon, name in extra_module_fields]),
        inline=True
    )
    
    embed.add_field(
        name="<:Invitelink:1040661606809473046> __Links__",
        value=f"\n<:dot:1088106350904610827> **[Invite]({inv}) | [Support]( https://bit.ly/luka-support)**",
        inline=False
    )

    view = vhelp.View(mapping=mapping, ctx=self.context, homeembed=embed, ui=2)
    await self.context.reply(embed=embed, mention_author=False, view=view)

 
  async def send_command_help(self, command):
    with open('jsons/blacklist.json', 'r') as f:
       bldata = json.load(f)
    data = getIgnore(self.context.guild.id)
    ch = data["channel"]
    iuser = data["user"]
    buser = data["excludeuser"]
    bl = discord.Embed(description="You are blacklisted from using my commannds.\nreason could be excessive use or spamming commands\nJoin our [Support Server]( https://bit.ly/luka-support) to appeal .", color=0x977FD7)
    embed = discord.Embed(description="This Channel is in ignored channel list try my commands in another channel .", color=0x977FD7)
    ign = discord.Embed(description=f"You are set as a ignored users for {self.context.guild.name} .\nTry my commands or modules in another guild .", color=0x977FD7)

    if str(self.context.author.id) in bldata["ids"]:
      return 
    
    if str(self.context.author.id) in iuser and str(self.context.author.id) not in buser: 
      return 

    if self.context.channel.id in ch and self.context.author.id not in buser:
        return
  
    else:
       hacker = f">>> {command.help}" if command.help else '>>> No Help Provided...'
       embed = discord.Embed( description=f"""```toml\n- [] = optional argument\n- <> = required argument\n- Do NOT Type These When Using Commands !```\n{hacker}""", color=0x977FD7)
       alias = ' | '.join(command.aliases)
      
       embed.add_field(name="**Aliases**", value=f"{alias}" if command.aliases else "No Aliases", inline=False)
       embed.add_field(name="**Usage**", value=f"`{self.context.prefix}{command.signature}`\n")
       embed.set_author(name=f"{command.cog.qualified_name.title()}", icon_url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
       await self.context.reply(embed=embed, mention_author=False)

  def get_command_signature(self, command: commands.Command) -> str:
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = ' | '.join(command.aliases)
            fmt = f'[{command.name} | {aliases}]'
            if parent:
                fmt = f'{parent}'
            alias = f'[{command.name} | {aliases}]'
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

  def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.help or 'No help found...'

  
  async def send_group_help(self, group):
    with open('jsons/blacklist.json', 'r') as f:
        idk = json.load(f)
    data = getIgnore(self.context.guild.id)
    ch = data["channel"]
    iuser = data["user"]
    buser = data["excludeuser"]
    bl = discord.Embed(description="You are blacklisted from using my commannds.\nreason could be excessive use or spamming commands\nJoin our [Support Server]( https://bit.ly/luka-support) to appeal .", color=0x977FD7)
    embed = discord.Embed(description="This Channel is in ignored channel list try my commands in another channel .", color=0x977FD7)
    ign = discord.Embed(description=f"You are set as a ignored users for {self.context.guild.name} .\nTry my commands or modules in another guild .", color=0x977FD7)

    if str(self.context.author.id) in idk["ids"]:
      return 
    
    if str(self.context.author.id) in iuser and str(self.context.author.id) not in buser: 
      return 

    if self.context.channel.id in ch and self.context.author.id not in buser:
        return
    else:
        await self.context.typing()
        data = getConfig(self.context.guild.id)
        prefix = data["prefix"]

        if not group.commands:
            return await self.send_command_help(group)

        embed = discord.Embed(color=0x977FD7)

        embed.title = f""
        _help = group.help or "No description provided..."
        _cmds = "\n\n".join(f"<:arrow:1060839014724280320> `{c.qualified_name}`\n{c.short_doc}" for c in group.commands)

        embed.description = f"\n<...> Duty | [...] Optional\n\n{_cmds}"
        embed.set_footer(text="Made with 💖 by LUKA#5191", icon_url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
        embed.set_author(name=f"{group.qualified_name} Commands", icon_url=self.context.author.display_avatar.url)

      
        if group.aliases:
            #embed.add_field(name="Aliases", value=", ".join(f"`{aliases}`" for aliases in group.aliases), inline=False)
             embed.timestamp = discord.utils.utcnow()
        await self.context.send(embed=embed)

  async def send_cog_help(self, cog):
    with open('jsons/blacklist.json', 'r') as f:
      bldata = json.load(f)
    data = getIgnore(self.context.guild.id)
    ch = data["channel"]
    iuser = data["user"]
    buser = data["excludeuser"]
    bl = discord.Embed(description="You are blacklisted from using my commannds.\nreason could be excessive use or spamming commands\nJoin our [Support Server]( https://bit.ly/luka-support) to appeal .", color=0x977FD7)
    embed = discord.Embed(description="This Channel is in ignored channel list try my commands in another channel .", color=0x977FD7)
    ign = discord.Embed(description=f"You are set as a ignored users for {self.context.guild.name} .\nTry my commands or modules in another guild .", color=0x977FD7)

    if str(self.context.author.id) in bldata["ids"]:
      return 
    
    if str(self.context.author.id) in iuser and str(self.context.author.id) not in buser: 
      return 

    if self.context.channel.id in ch and self.context.author.id not in buser:
        return
    await self.context.typing()
    embed = discord.Embed( color=0x977FD7)
    embed.title = cog.qualified_name.title()
    embed.description = f"""\n<...> Duty | [...] Optional\n\n\n\n"""
    for cmd in cog.get_commands():
      if not cmd.hidden:
        _brief = cmd.short_doc if cmd.short_doc else "No Help Provided..."
        embed.add_field(name=f"<:arrow:1060839014724280320> `{self.context.prefix}{cmd.name}`", value=f"{_brief}\n\n", inline=False)
    embed.timestamp = discord.utils.utcnow()
    embed.set_author(name=self.context.author, icon_url=self.context.author.display_avatar.url)
    embed.set_footer(text="Made with 💖 by LUKA#5191", icon_url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
    await self.context.send(embed=embed)

class Help(Cog, name="help "):
  def __init__(self, client:Luka):
    self._original_help_command = client.help_command
    attributes = {
            'name': "help",
            'aliases': ['h'],
            'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
            'help': 'Shows help about bot, a command or a category'
        }
    client.help_command = HelpCommand(command_attrs=attributes)
    client.help_command.cog = self

  async def cog_unload(self):
    self.help_command = self._original_help_command
