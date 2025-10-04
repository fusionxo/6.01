import discord
from discord.ext import commands
from difflib import get_close_matches
import json
import aiofiles
import time
import psutil
import asyncio
from core import Context, Luka, Cog
from utils.checks import global_check

# --- Configuration ---
SUCCESS_COLOR = 0x4CAF50
ERROR_COLOR = 0xF44336
WARN_COLOR = 0xFF9800
INFO_COLOR = 0x977FD7
THUMBNAIL_URL = 'https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png'

# --- UI Components ---

class SearchModal(discord.ui.Modal, title="🔍 Smart Command Search"):
    """A modal for users to search for commands."""
    query = discord.ui.TextInput(
        label="Search Query",
        placeholder="Enter command name, alias, or category...",
        style=discord.TextStyle.short,
        required=True
    )

    def __init__(self, help_command, bot: Luka):
        super().__init__(timeout=120)
        self.help_command = help_command
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        """Processes the search query and displays results."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        all_commands = list(self.bot.walk_commands())
        query_lower = self.query.value.lower()
        
        results = {}
        for cmd in all_commands:
            if cmd.hidden:
                continue
            
            score = 0
            if query_lower in cmd.name.lower(): score += 10
            if any(query_lower in alias.lower() for alias in cmd.aliases): score += 5
            if cmd.cog_name and query_lower in cmd.cog_name.lower(): score += 2
            
            if score > 0: results[cmd] = score

        if not results:
            command_names = [cmd.name for cmd in all_commands if not cmd.hidden]
            fuzzy_matches = get_close_matches(query_lower, command_names, n=5, cutoff=0.6)
            for match_name in fuzzy_matches:
                cmd = self.bot.get_command(match_name)
                if cmd: results[cmd] = 1

        if not results:
            embed = discord.Embed(
                title="<:error:1088542929158688788> No Results Found",
                description=f"Could not find any commands matching `{self.query.value}`.",
                color=ERROR_COLOR
            )
            return await interaction.followup.send(embed=embed, ephemeral=True)

        sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)[:7]

        prefix = await self.help_command.get_prefix(interaction)
        embed = discord.Embed(
            title=f"🔍 Search Results for `{self.query.value}`",
            description="Here are the top matching commands:",
            color=INFO_COLOR
        )
        for cmd, score in sorted_results:
            embed.add_field(name=f"`{prefix}{cmd.name}`", value=cmd.short_doc or "No description.", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class HelpDropdown(discord.ui.Select):
    """A dropdown menu to select a help category (cog)."""
    def __init__(self, bot: Luka, help_custom_key: str):
        self.bot = bot
        self.help_custom_key = help_custom_key
        options = []
        
        for cog in bot.cogs.values():
            if hasattr(cog, self.help_custom_key):
                emoji, label, description = getattr(cog, self.help_custom_key)()
                options.append(discord.SelectOption(
                    label=label, value=cog.qualified_name, emoji=emoji, description=description
                ))
        
        placeholder = "Select from main module..." if help_custom_key == "help_custom" else "Select from extra module..."
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=sorted(options, key=lambda o: o.label))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)
        if cog:
            self.view.session_interactions += 1
            final_embed = await self.view.help_command.get_cog_help_embed(cog, interaction)
            await interaction.message.edit(embed=final_embed, view=self.view)


class EnhancedHelpView(discord.ui.View):
    """The main view for the help command, containing all UI elements."""
    def __init__(self, bot: Luka, ctx: Context, home_embed: discord.Embed):
        super().__init__(timeout=180)
        self.bot = bot
        self.ctx = ctx
        self.help_command = bot.help_command
        self.home_embed = home_embed
        self.message = None
        self.session_interactions = 0

        main_dropdown = HelpDropdown(bot, "help_custom")
        if main_dropdown.options: self.add_item(main_dropdown)
            
        extra_dropdown = HelpDropdown(bot, "help2_custom")
        if extra_dropdown.options: self.add_item(extra_dropdown)

    def create_animated_embed(self, status_text: str) -> discord.Embed:
        embed = discord.Embed(description=f"⏳ {status_text}", color=INFO_COLOR)
        return embed

    @discord.ui.button(label="Home", style=discord.ButtonStyle.secondary, emoji="🏠", row=2)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.home_embed)
        self.session_interactions += 1

    @discord.ui.button(label="Search", style=discord.ButtonStyle.primary, emoji="🔍", row=2)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SearchModal(self.help_command, self.bot)
        await interaction.response.send_modal(modal)
        self.session_interactions += 1

    @discord.ui.button(label="Stats", style=discord.ButtonStyle.secondary, emoji="📊", row=2)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.session_interactions += 1
        
        animated_embed = self.create_animated_embed("Fetching Live Statistics...")
        await interaction.message.edit(embed=animated_embed, view=self)

        process = psutil.Process()
        latency = round(self.bot.latency * 1000)
        mem_usage = round(process.memory_info().rss / 1024 ** 2, 2)
        
        stats_embed = discord.Embed(title="📊 Live Bot Statistics", color=INFO_COLOR)
        stats_embed.set_thumbnail(url=THUMBNAIL_URL)
        stats_embed.add_field(name="Performance", value=f"```yaml\nLatency: {latency}ms\nMemory: {mem_usage} MB\n```", inline=False)
        stats_embed.add_field(name="Session Info", value=f"```yaml\nUser: {self.ctx.author}\nInteractions: {self.session_interactions}\n```", inline=False)
        stats_embed.set_footer(text="Statistics are updated in real-time.")
        
        await asyncio.sleep(0.7)
        await interaction.message.edit(embed=stats_embed, view=self)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="✖️", row=2)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This is not your help session!", ephemeral=True)
            return False
        return True
        
    async def on_timeout(self) -> None:
        if self.message:
            for item in self.children: item.disabled = True
            try:
                await self.message.edit(content="*This help session has expired.*", view=self)
            except discord.NotFound:
                pass

class NewHelpCommand(commands.HelpCommand):
    """The refactored custom help command with advanced features."""

    async def get_prefix(self, source) -> str:
        if not source.guild: return "$"
        guild_id = source.guild.id
        try:
            async with aiofiles.open('jsons/config.json', 'r') as f:
                config_data = json.loads(await f.read())
            return config_data.get("guilds", {}).get(str(guild_id), {}).get("prefix", "$")
        except (FileNotFoundError, json.JSONDecodeError):
            return "$"

    async def send_bot_help(self, mapping: dict):
        ctx = self.context
        if await self.is_blacklisted_or_ignored(ctx): return
            
        prefix = await self.get_prefix(ctx)
        
        embed = discord.Embed(
            title="Luka Help Desk",
            description=(
                f"**Welcome, {ctx.author.mention}!**\n"
                f"I'm Luka, your multi-purpose assistant. Use the dropdowns below to explore my command modules.\n\n"
                f"**Server Prefix:** `{prefix}`\n"
                f"**Total Commands:** `{len(set(ctx.bot.walk_commands()))}`"
            ),
            color=INFO_COLOR,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=f"Session started by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        view = EnhancedHelpView(ctx.bot, ctx, embed)
        message = await ctx.reply(embed=embed, view=view, mention_author=False)
        view.message = message

    async def get_cog_help_embed(self, cog: commands.Cog, interaction: discord.Interaction = None) -> discord.Embed:
        ctx = self.context
        
        title, description = cog.qualified_name, cog.description or "No description available."
        if hasattr(cog, "help_custom"):
            emoji, label, desc = cog.help_custom()
            title, description = f"{emoji} {label}", desc
        elif hasattr(cog, "help2_custom"):
            emoji, label, desc = cog.help2_custom()
            title, description = f"{emoji} {label}", desc

        embed = discord.Embed(title=title, description=description, color=INFO_COLOR)

        # --- FIX: Re-implement summary command logic ---
        summary_command = None
        for cmd in cog.get_commands():
            if cmd.name.startswith("__"):
                summary_command = cmd
                break
        
        if summary_command and summary_command.help:
            # If a summary command exists, use its docstring.
            embed.add_field(name="Commands", value=f"```yaml\n{summary_command.help}\n```", inline=False)
        else:
            # Fallback to listing individual commands if no summary is found.
            user_commands, admin_commands = [], []
            for cmd in cog.get_commands():
                if cmd.hidden or cmd.name.startswith("__"): continue
                
                is_admin = any(hasattr(check, 'permissions') or check.__qualname__.startswith('is_owner') for check in cmd.checks)
                
                if is_admin: admin_commands.append(cmd)
                else: user_commands.append(cmd)
            
            if user_commands:
                user_cmds_str = " ".join(f"`{cmd.name}`" for cmd in sorted(user_commands, key=lambda c: c.name))
                embed.add_field(name="User Commands", value=user_cmds_str, inline=False)
            
            if admin_commands:
                admin_cmds_str = " ".join(f"`{cmd.name}`" for cmd in sorted(admin_commands, key=lambda c: c.name))
                embed.add_field(name="🔒 Admin Commands", value=admin_cmds_str, inline=False)
        # --- End of Fix ---

        context_source = interaction or ctx
        prefix = await self.get_prefix(context_source)
        embed.set_footer(text=f"Use {prefix}help <command> for more info.")
        return embed

    async def send_command_help(self, command: commands.Command):
        if await self.is_blacklisted_or_ignored(self.context): return

        prefix = await self.get_prefix(self.context)
        embed = discord.Embed(
            title=f"Help for `{command.qualified_name}`",
            description=command.help or "No description provided.",
            color=INFO_COLOR
        )
        embed.add_field(name="Usage", value=f"```\n{prefix}{command.qualified_name} {command.signature}\n```")
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in command.aliases), inline=False)
        
        await self.context.reply(embed=embed, mention_author=False)

    async def command_not_found(self, string: str):
        if await self.is_blacklisted_or_ignored(self.context): return

        embed = discord.Embed(
            title="<:error:1088542929158688788> Command Not Found",
            description=f"The command `{string}` does not exist.",
            color=ERROR_COLOR
        )
        cmds = [cmd.qualified_name for cmd in self.context.bot.walk_commands()]
        matches = get_close_matches(string, cmds)
        if matches:
            embed.add_field(name="Did you mean...?", value="\n".join(f"• `{match}`" for match in matches))
        
        await self.context.reply(embed=embed, mention_author=False)

    async def is_blacklisted_or_ignored(self, ctx: Context) -> bool:
        try:
            async with aiofiles.open('jsons/blacklist.json', 'r') as f:
                bldata = json.loads(await f.read())
            if str(ctx.author.id) in bldata.get("ids", []): return True

            async with aiofiles.open('jsons/ignore.json', 'r') as f:
                ignore_config = json.loads(await f.read())
            
            guild_ignore = ignore_config.get("guilds", {}).get(str(ctx.guild.id), {})
            is_ignored = (str(ctx.author.id) in guild_ignore.get("user", []) or 
                          ctx.channel.id in guild_ignore.get("channel", []))
            is_excluded = str(ctx.author.id) in guild_ignore.get("excludeuser", [])

            if is_ignored and not is_excluded: return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False
        return False

class Help(Cog):
    """The cog that manages the new, enhanced help command."""
    def __init__(self, client: Luka):
        self._original_help_command = client.help_command
        help_attrs = {
            'aliases': ['h'],
            'help': 'Shows help about the bot, a command, or a category.'
        }
        client.help_command = NewHelpCommand(command_attrs=help_attrs)
        # ------------------------
        client.help_command.cog = self

    

    async def cog_unload(self):
        self.bot.help_command = self._original_help_command
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)

async def setup(bot: Luka):
    await bot.add_cog(Help(bot))
