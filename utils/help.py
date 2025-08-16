import discord
from discord.ext import commands
from difflib import get_close_matches
from contextlib import suppress
from core import Context, Luka, Cog
from utils.Tools import getConfig, blacklist_check, ignore_check
import json

class HelpDropdown(discord.ui.Select):
    """A dropdown menu to select a help category (cog)."""
    def __init__(self, bot: Luka, mapping: dict):
        self.bot = bot
        self.mapping = mapping
        options = []
        # Dynamically create options from cogs that have a help_custom method
        for cog in bot.cogs.values():
            if hasattr(cog, "help_custom"):
                emoji, label, description = cog.help_custom()
                options.append(discord.SelectOption(label=label, value=cog.qualified_name, emoji=emoji, description=description))
            if hasattr(cog, "help2_custom"):
                emoji, label, description = cog.help2_custom()
                options.append(discord.SelectOption(label=label, value=cog.qualified_name, emoji=emoji, description=description))


        super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # When a user selects an option, generate and send the help for that cog
        cog_name = self.values[0]
        cog = self.bot.get_cog(cog_name)
        if cog:
            embed = await self.view.help_command.get_cog_help_embed(cog)
            await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    """The main view for the help command, containing the dropdown and navigation."""
    def __init__(self, bot: Luka, mapping: dict, ctx: Context, home_embed: discord.Embed):
        super().__init__(timeout=180)
        self.bot = bot
        self.mapping = mapping
        self.ctx = ctx
        self.help_command = bot.help_command
        self.home_embed = home_embed
        self.add_item(HelpDropdown(bot, mapping))

    @discord.ui.button(label="Home", style=discord.ButtonStyle.green, emoji="🏠")
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.home_embed)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, emoji="✖️")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This is not your help session!", ephemeral=True)
            return False
        return True

class NewHelpCommand(commands.HelpCommand):
    """The refactored custom help command."""

    async def send_bot_help(self, mapping: dict):
        """This is what is called when the main help command is invoked."""
        ctx = self.context
        bot = ctx.bot

        # Basic permission/ignore checks
        if await self.is_blacklisted_or_ignored(ctx):
            return
            
        prefix = getConfig(ctx.guild.id)["prefix"]
        
        embed = discord.Embed(
            title="Luka Help Desk",
            description=(
                f"<:dot:1088106350904610827> The server prefix is `{prefix}`\n"
                f"<:dot:1088106350904610827> Use the dropdown to select a category.\n"
                f"<:dot:1088106350904610827> Total `{len(set(bot.walk_commands()))}` Commands Available.\n"
            ),
            color=0x977FD7
        )
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        view = HelpView(bot, mapping, ctx, embed)
        await ctx.reply(embed=embed, view=view, mention_author=False)

    async def get_cog_help_embed(self, cog: commands.Cog) -> discord.Embed:
        """Generates the help embed for a specific cog."""
        ctx = self.context
        bot = ctx.bot
        
        # This is the key part: Find the special summary command (e.g., __Pfps__)
        summary_command = None
        for cmd in cog.get_commands():
            if cmd.name.startswith("__"):
                summary_command = cmd
                break
        
        # Determine title and description
        title = cog.qualified_name
        description = cog.description or "No description available."

        if hasattr(cog, "help_custom"):
            emoji, label, desc = cog.help_custom()
            title = f"{emoji} {label}"
            description = desc
        elif hasattr(cog, "help2_custom"):
            emoji, label, desc = cog.help2_custom()
            title = f"{emoji} {label}"
            description = desc

        embed = discord.Embed(title=title, description=description, color=0x977FD7)
        
        # If we found a summary command, use its docstring for the command list
        if summary_command and summary_command.help:
            embed.add_field(name="Commands", value=f"```\n{summary_command.help}\n```", inline=False)
        else:
            # Fallback for cogs that don't have the special summary command
            commands_list = []
            for cmd in cog.get_commands():
                if not cmd.hidden and not cmd.name.startswith("__"):
                    commands_list.append(f"`{cmd.name}`")
            if commands_list:
                embed.add_field(name="Commands", value=", ".join(commands_list), inline=False)

        embed.set_footer(text=f"Use {getConfig(ctx.guild.id)['prefix']}help <command> for more info on a command.")
        return embed

    async def send_command_help(self, command: commands.Command):
        """Handles help for a specific command."""
        if await self.is_blacklisted_or_ignored(self.context):
            return

        embed = discord.Embed(
            title=f"Help for `{command.qualified_name}`",
            description=command.help or "No description provided.",
            color=0x977FD7
        )
        embed.add_field(name="Usage", value=f"```\n{self.context.prefix}{command.qualified_name} {command.signature}\n```")
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in command.aliases), inline=False)
        
        await self.context.reply(embed=embed, mention_author=False)

    async def command_not_found(self, string: str):
        """Handles when a command is not found."""
        if await self.is_blacklisted_or_ignored(self.context):
            return

        msg = f"Command `{string}` not found."
        cmds = [cmd.qualified_name for cmd in self.context.bot.walk_commands()]
        matches = get_close_matches(string, cmds)
        if matches:
            msg += f"\n\nDid you mean:\n" + "\n".join(f"• `{match}`" for match in matches)
        
        await self.context.reply(msg, ephemeral=True)

    async def is_blacklisted_or_ignored(self, ctx: Context) -> bool:
        """Helper to check blacklist and ignore status."""
        # This is a simplified check. You should ideally use your async versions.
        # For now, this uses the synchronous ones to match your current code.
        try:
            with open('jsons/blacklist.json', 'r') as f:
                bldata = json.load(f)
            if str(ctx.author.id) in bldata["ids"]:
                return True
            
            ignore_data = getIgnore(ctx.guild.id)
            if str(ctx.author.id) in ignore_data["user"] and str(ctx.author.id) not in ignore_data["excludeuser"]:
                return True
            if ctx.channel.id in ignore_data["channel"] and str(ctx.author.id) not in ignore_data["excludeuser"]:
                return True
        except Exception:
            pass # File not found etc.
        return False

class Help(Cog):
    """The cog that manages the new help command."""
    def __init__(self, client: Luka):
        self._original_help_command = client.help_command
        client.help_command = NewHelpCommand()
        client.help_command.cog = self

    async def cog_unload(self):
        self.bot.help_command = self._original_help_command

async def setup(bot: Luka):
    await bot.add_cog(Help(bot))
