import json
import aiofiles
from discord.ext import commands

async def read_json(path: str) -> dict:
    """Asynchronously reads a JSON file and returns its content."""
    try:
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            return json.loads(await f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        # Return an empty dict if the file is missing or contains invalid JSON
        return {}

async def global_check(ctx: commands.Context) -> bool:
    """
    A global check that runs automatically before every command.
    This function checks for blacklisted users and ignored channels/users.
    It is fully asynchronous and replaces the need for individual decorators.
    """
    # 1. Always allow the bot owner(s) to run commands.
    if await ctx.bot.is_owner(ctx.author):
        return True

    # 2. Asynchronously check the blacklist.
    blacklist_data = await read_json('jsons/blacklist.json')
    if str(ctx.author.id) in blacklist_data.get("ids", []):
        # Silently fail the check for blacklisted users.
        return False

    # 3. Asynchronously perform the ignore check.
    # Ignore checks do not apply in Direct Messages.
    if not ctx.guild:
        return True
        
    ignore_data = await read_json('jsons/ignore.json')
    # Safely get the configuration for the specific guild.
    guild_ignore = ignore_data.get("guilds", {}).get(str(ctx.guild.id), {})
    
    # Check if the user is explicitly excluded from being ignored.
    if str(ctx.author.id) in guild_ignore.get("excludeuser", []):
        return True

    # Check if the user or the channel is in an ignore list.
    if str(ctx.author.id) in guild_ignore.get("user", []):
        return False # User is ignored.
        
    if str(ctx.channel.id) in guild_ignore.get("channel", []):
        return False # Channel is ignored.

    # 4. If all checks pass, allow the command to run.
    return True
