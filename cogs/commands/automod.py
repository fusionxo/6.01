import discord
from discord.ext import commands
import json
import asyncio
import aiofiles
import re
import time
import datetime
from collections import defaultdict, deque
from typing import List
from utils import *
from utils.checks import global_check

# --- Configuration Management ---
class ConfigManager:
    def __init__(self, path):
        self.path = path
        self.lock = asyncio.Lock()
        self.data = {}

    async def load(self):
        async with self.lock:
            try:
                async with aiofiles.open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.loads(await f.read())
            except (FileNotFoundError, json.JSONDecodeError):
                self.data = {}
        return self.data

    async def save(self):
        async with self.lock:
            async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.data, indent=4))

    def get_guild_config(self, guild_id):
        guild_id_str = str(guild_id)
        if guild_id_str not in self.data:
            self.data[guild_id_str] = self.get_default_config()
        
        default_config = self.get_default_config()
        for key, value in default_config.items():
            if key not in self.data[guild_id_str]:
                self.data[guild_id_str][key] = value
            elif isinstance(value, dict):
                for sub_key in value:
                     if sub_key not in self.data[guild_id_str][key]:
                         self.data[guild_id_str][key][sub_key] = value[sub_key]
        return self.data[guild_id_str]

    def get_default_config(self):
        return {
            "log_channel": None,
            "whitelist": {"users": [], "roles": []},
            "modules": {
                "antispam": {"enabled": False, "rate": 5, "per": 5, "action": "timeout", "duration": 600},
                "antilink": {"enabled": False, "action": "delete"},
                "massmention": {"enabled": False, "limit": 5, "action": "warn"},
                "badwords": {"enabled": False, "words": [], "action": "delete"}
            }
        }

# --- Help Menu UI ---
class HelpDropdown(discord.ui.Select):
    def __init__(self, cog_instance):
        self.cog = cog_instance
        options = [
            discord.SelectOption(label="Automod Status", description="View the current automod configuration.", emoji="📊", value="status"),
            discord.SelectOption(label="Toggle Modules", description="Enable or disable automod modules.", emoji="⚙️", value="toggle"),
            discord.SelectOption(label="Set Punishments", description="Configure actions for each module.", emoji="⚖️", value="punishment"),
            discord.SelectOption(label="Whitelist", description="Manage whitelisted users and roles.", emoji="🛡️", value="whitelist"),
            discord.SelectOption(label="Bad Words", description="Manage the server's word blacklist.", emoji="📝", value="badwords"),
            discord.SelectOption(label="Log Channel", description="Set the channel for automod logs.", emoji="📜", value="logchannel"),
        ]
        super().__init__(placeholder="Choose a command category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = self.cog.get_help_embed(interaction.guild, self.values[0])
        await interaction.response.edit_message(embed=embed)

class AutomodHelpView(discord.ui.View):
    def __init__(self, cog_instance, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown(cog_instance))

# --- Main Cog ---
class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = ConfigManager("jsons/automodconfig.json")
        self.spam_tracker = defaultdict(lambda: deque(maxlen=20))
        self.bot.loop.create_task(self.config.load())
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help_custom(self):
		      emoji = '<:autom:1088452318376239114>'
		      label = "Automod"
		      description = "Shows Automod commands."
		      return emoji, label, description

    @commands.group()
    async def __Automod__(self, ctx: commands.Context):
        """`automod antilink on`, `automod antispam on`, `automod whitelist add/remove`"""
        

    def is_whitelisted(self, message):
        if not message.guild: return True
        cfg = self.config.get_guild_config(message.guild.id)
        if message.author.id in cfg["whitelist"]["users"]: return True
        try:
            author_roles = [r.id for r in message.author.roles]
            if any(r_id in cfg["whitelist"]["roles"] for r_id in author_roles): return True
        except AttributeError: return False
        return False

    async def take_action(self, message, module_name, reason):
        cfg = self.config.get_guild_config(message.guild.id)
        module_cfg = cfg["modules"][module_name]
        action = module_cfg.get("action", "warn")
        user = message.author
        original_message = message.content
        
        try:
            if action == "delete":
                await message.delete()
            elif action == "warn":
                await message.delete()
                await message.channel.send(f"{user.mention}, your message was removed. Reason: {reason}", delete_after=10)
            elif action == "timeout":
                duration = datetime.timedelta(seconds=module_cfg.get("duration", 600))
                await message.delete()
                await user.timeout(duration, reason=f"Automod: {reason}")
                await message.channel.send(f"{user.mention} has been timed out. Reason: {reason}", delete_after=10)
            elif action == "kick":
                await message.delete()
                await user.kick(reason=f"Automod: {reason}")
            elif action == "ban":
                await message.delete()
                await user.ban(reason=f"Automod: {reason}")
            
            await self.log_action(message, original_message, reason, action)
        except discord.errors.NotFound:
            pass # Message was already deleted
        except discord.Forbidden:
            await self.log_action(message, original_message, f"Failed to take action: Missing Permissions", "Error")
        except Exception as e:
            await self.log_action(message, original_message, f"An unexpected error occurred: {e}", "Error")

    async def handle_spam_incident(self, user: discord.Member, channel: discord.TextChannel, messages: List[discord.Message], reason: str):
        cfg = self.config.get_guild_config(user.guild.id)
        module_cfg = cfg["modules"]["antispam"]
        action = module_cfg.get("action", "timeout")
        
        try:
            # 1. Take primary action (timeout, kick, ban)
            if action == "timeout":
                duration = datetime.timedelta(seconds=module_cfg.get("duration", 600))
                await user.timeout(duration, reason=f"Automod: {reason}")
                await channel.send(f"{user.mention} has been timed out for spamming.", delete_after=10)
            elif action == "kick":
                await user.kick(reason=f"Automod: {reason}")
            elif action == "ban":
                await user.ban(reason=f"Automod: {reason}")

            # 2. Bulk delete messages
            deletable_messages = [msg for msg in messages if not msg.is_system()]
            if deletable_messages:
                await channel.delete_messages(deletable_messages)

            # 3. Log the entire incident as one event
            content_summary = "\n".join([f"`{msg.id}`: {msg.content[:50]}" for msg in messages])
            await self.log_action(messages[0], content_summary, reason, action)

        except discord.Forbidden:
            await self.log_action(messages[0], "Multiple Messages", f"Failed to take action: Missing Permissions", "Error")
        except Exception as e:
            await self.log_action(messages[0], "Multiple Messages", f"An unexpected error occurred: {e}", "Error")
    
    async def log_action(self, message, original_message, reason, action_taken):
        cfg = self.config.get_guild_config(message.guild.id)
        log_channel_id = cfg.get("log_channel")
        if not log_channel_id: return
        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel: return

        embed = discord.Embed(title="Automod Action Log", color=0x977FD7, timestamp=datetime.datetime.utcnow())
        embed.add_field(name="User", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
        embed.add_field(name="Action Taken", value=action_taken.capitalize(), inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        if len(original_message) > 0:
            embed.add_field(name="Message Content", value=f"```\n{original_message[:1000]}\n```", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.set_footer(text="Luka |")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
        
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot or self.is_whitelisted(message):
            return
        if isinstance(message.author, discord.Member) and message.author.guild_permissions.administrator:
            return

        cfg = self.config.get_guild_config(message.guild.id)
        
        if cfg["modules"]["antispam"]["enabled"] and await self.check_spam(message):
            return
        if cfg["modules"]["antilink"]["enabled"] and await self.check_links(message):
            return
        if cfg["modules"]["massmention"]["enabled"] and await self.check_mentions(message):
            return
        if cfg["modules"]["badwords"]["enabled"] and await self.check_badwords(message):
            return

    async def check_spam(self, message):
        cfg = self.config.get_guild_config(message.guild.id)
        module_cfg = cfg["modules"]["antispam"]
        user_id = message.author.id
        current_time = time.time()
        self.spam_tracker[user_id].append(message)
        
        recent_messages = [msg for msg in self.spam_tracker[user_id] if current_time - msg.created_at.timestamp() < module_cfg["per"]]
        
        if len(recent_messages) >= module_cfg["rate"]:
            await self.handle_spam_incident(message.author, message.channel, list(recent_messages), "Spamming messages")
            self.spam_tracker[user_id].clear()
            return True
        return False

    async def check_links(self, message):
        safe_domains = ["tenor.com", "giphy.com", "twitter.com", "x.com"]
        if any(domain in message.content for domain in safe_domains):
            return False
            
        if re.search(r'(discord\.gg/|discord\.com/invite/)', message.content):
            await self.take_action(message, "antilink", "Sending invite links")
            return True
        return False

    async def check_mentions(self, message):
        cfg = self.config.get_guild_config(message.guild.id)
        limit = cfg["modules"]["massmention"]["limit"]
        if len(message.mentions) > limit or message.mention_everyone:
            reason = f"Mass mentioning more than {limit} users" if not message.mention_everyone else "Pinging @everyone/here"
            await self.take_action(message, "massmention", reason)
            return True
        return False

    async def check_badwords(self, message):
        cfg = self.config.get_guild_config(message.guild.id)
        bad_words = cfg["modules"]["badwords"]["words"]
        if any(word in message.content.lower() for word in bad_words):
            await self.take_action(message, "badwords", "Using a forbidden word")
            return True
        return False

    def get_help_embed(self, guild, page):
        cfg = self.config.get_guild_config(guild.id)
        embed = discord.Embed(color=0x977FD7)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
        embed.set_footer(text="Luka | Automod Help")

        if page == "status":
            embed.title = f"Automod Status for {guild.name}"
            for name, module in cfg["modules"].items():
                status = "✅ Enabled" if module["enabled"] else "❌ Disabled"
                action = module.get('action', 'N/A').capitalize()
                details = f"Action: `{action}`"
                if name == "antispam":
                    details += f"\nRate: `{module['rate']}/{module['per']}s`"
                    if module.get('action') == 'timeout':
                        details += f"\nDuration: `{module['duration']}s`"
                elif name == "massmention":
                    details += f"\nLimit: `{module['limit']}`"
                embed.add_field(name=f"**{name.capitalize()}**", value=f"**Status:** {status}\n{details}", inline=True)
            log_channel = self.bot.get_channel(cfg.get("log_channel"))
            embed.add_field(name="**Logging**", value=f"Channel: {log_channel.mention if log_channel else '`Not Set`'}", inline=False)
        elif page == "toggle":
            embed.title = "Toggle Modules"
            embed.description = "Enable or disable automod features."
            embed.add_field(name="Usage", value="`/automod toggle <module> <True/False>`", inline=False)
            embed.add_field(name="Example", value="`/automod toggle antispam True`", inline=False)
            embed.add_field(name="Modules", value="`antispam`, `antilink`, `massmention`, `badwords`", inline=False)
        elif page == "punishment":
            embed.title = "Set Punishments"
            embed.description = "Configure the action taken for each module violation."
            embed.add_field(name="Usage", value="`/automod punishment <module> <action> [duration]`", inline=False)
            embed.add_field(name="Example", value="`/automod punishment antispam timeout 300`\n`/automod punishment antilink delete`", inline=False)
            embed.add_field(name="Actions", value="`delete`, `warn`, `timeout`, `kick`, `ban`", inline=False)
            embed.add_field(name="Note", value="`duration` (in seconds) is only needed for the `timeout` action.", inline=False)
        elif page == "whitelist":
            embed.title = "Whitelist Management"
            embed.description = "Exempt users or roles from automod."
            embed.add_field(name="Commands", value="`/automod whitelist add <user>`\n`/automod whitelist remove <user>`\n`/automod whitelist addrole <role>`\n`/automod whitelist removerole <role>`", inline=False)
        elif page == "badwords":
            embed.title = "Bad Words Management"
            embed.description = "Manage the server's word blacklist."
            embed.add_field(name="Commands", value="`/automod badwords add <word>`\n`/automod badwords remove <word>`\n`/automod badwords list`", inline=False)
        elif page == "logchannel":
            embed.title = "Log Channel Setup"
            embed.description = "Set the channel where automod actions will be logged."
            embed.add_field(name="Usage", value="`/automod logchannel <#channel>`", inline=False)
        return embed

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx):
        embed = self.get_help_embed(ctx.guild, "status")
        view = AutomodHelpView(self)
        await ctx.send(embed=embed, view=view)

    @automod.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def automod_toggle(self, ctx, module: str, state: bool):
        module = module.lower()
        cfg = self.config.get_guild_config(ctx.guild.id)
        if module not in cfg["modules"]:
            return await ctx.send("Invalid module. Options: `antispam`, `antilink`, `massmention`, `badwords`")
        cfg["modules"][module]["enabled"] = state
        await self.config.save()
        await ctx.send(f"Module `{module}` has been {'enabled' if state else 'disabled'}.")

    @automod.command(name="punishment")
    @commands.has_permissions(administrator=True)
    async def automod_punishment(self, ctx, module: str, action: str, duration_seconds: int = None):
        module, action = module.lower(), action.lower()
        cfg = self.config.get_guild_config(ctx.guild.id)
        if module not in cfg["modules"]:
            return await ctx.send("Invalid module.")
        if action not in ["delete", "warn", "timeout", "kick", "ban"]:
            return await ctx.send("Invalid action. Options: `delete`, `warn`, `timeout`, `kick`, `ban`")
        
        cfg["modules"][module]["action"] = action
        if action == "timeout":
            if duration_seconds is None:
                return await ctx.send("You must provide a duration in seconds for the timeout action.")
            cfg["modules"][module]["duration"] = duration_seconds
        
        await self.config.save()
        await ctx.send(f"Set punishment for `{module}` to `{action}`.")

    @automod.command(name="logchannel")
    @commands.has_permissions(administrator=True)
    async def automod_logchannel(self, ctx, channel: discord.TextChannel):
        cfg = self.config.get_guild_config(ctx.guild.id)
        cfg["log_channel"] = channel.id
        await self.config.save()
        await ctx.send(f"Automod log channel has been set to {channel.mention}")

    @automod.group(name="whitelist", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def automod_whitelist(self, ctx):
        await ctx.send(embed=self.get_help_embed(ctx.guild, "whitelist"))

    @automod_whitelist.command(name="add")
    async def whitelist_add(self, ctx, user: discord.Member):
        cfg = self.config.get_guild_config(ctx.guild.id)
        if user.id not in cfg["whitelist"]["users"]:
            cfg["whitelist"]["users"].append(user.id)
            await self.config.save()
            await ctx.send(f"{user.mention} has been added to the whitelist.")
        else:
            await ctx.send(f"{user.mention} is already whitelisted.")

    @automod_whitelist.command(name="remove")
    async def whitelist_remove(self, ctx, user: discord.Member):
        cfg = self.config.get_guild_config(ctx.guild.id)
        if user.id in cfg["whitelist"]["users"]:
            cfg["whitelist"]["users"].remove(user.id)
            await self.config.save()
            await ctx.send(f"{user.mention} has been removed from the whitelist.")
        else:
            await ctx.send(f"{user.mention} is not whitelisted.")
    
    @automod_whitelist.command(name="addrole")
    async def whitelist_addrole(self, ctx, role: discord.Role):
        cfg = self.config.get_guild_config(ctx.guild.id)
        if role.id not in cfg["whitelist"]["roles"]:
            cfg["whitelist"]["roles"].append(role.id)
            await self.config.save()
            await ctx.send(f"Role {role.mention} has been added to the whitelist.")
        else:
            await ctx.send(f"Role {role.mention} is already whitelisted.")

    @automod_whitelist.command(name="removerole")
    async def whitelist_removerole(self, ctx, role: discord.Role):
        cfg = self.config.get_guild_config(ctx.guild.id)
        if role.id in cfg["whitelist"]["roles"]:
            cfg["whitelist"]["roles"].remove(role.id)
            await self.config.save()
            await ctx.send(f"Role {role.mention} has been removed from the whitelist.")
        else:
            await ctx.send(f"Role {role.mention} is not whitelisted.")

    @automod.group(name="badwords", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def automod_badwords(self, ctx):
        await ctx.send(embed=self.get_help_embed(ctx.guild, "badwords"))
    
    @automod_badwords.command(name="add")
    async def badwords_add(self, ctx, *, word: str):
        cfg = self.config.get_guild_config(ctx.guild.id)
        word = word.lower()
        if word not in cfg["modules"]["badwords"]["words"]:
            cfg["modules"]["badwords"]["words"].append(word)
            await self.config.save()
            await ctx.send(f"Word `{word}` has been added to the blacklist.")
        else:
            await ctx.send(f"Word `{word}` is already blacklisted.")

    @automod_badwords.command(name="remove")
    async def badwords_remove(self, ctx, *, word: str):
        cfg = self.config.get_guild_config(ctx.guild.id)
        word = word.lower()
        if word in cfg["modules"]["badwords"]["words"]:
            cfg["modules"]["badwords"]["words"].remove(word)
            await self.config.save()
            await ctx.send(f"Word `{word}` has been removed from the blacklist.")
        else:
            await ctx.send(f"Word `{word}` is not blacklisted.")

    @automod_badwords.command(name="list")
    async def badwords_list(self, ctx):
        cfg = self.config.get_guild_config(ctx.guild.id)
        words = cfg["modules"]["badwords"]["words"]
        if not words:
            return await ctx.send("There are no blacklisted words for this server.")
        description = ", ".join(f"`{w}`" for w in words)
        embed = discord.Embed(title="Blacklisted Words", description=description, color=0x977FD7)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Auto(bot))
