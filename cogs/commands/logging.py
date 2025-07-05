import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import datetime
import pytz
from utils import *


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cluster = MongoClient(
            "mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net/loggings?retryWrites=true&w=majority"
        )
        self.db = self.cluster["loggings"]
        self.collection = self.db["loggingdata"]

    @commands.hybrid_group(
        name="logging",
        description="Logging channel\nLogging config\nLogging delete",
        invoke_without_command=True
    )
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def logging(self, ctx):
        if ctx.subcommand_passed is None:
            await ctx.send_help(ctx.command)
            ctx.command.reset_cooldown(ctx)

    @logging.command(
        description="Set the logging channel.",
        name='channel',
        usage="logging channel <channel>"
    )
    async def set_channel(self, ctx, channel: discord.TextChannel):
        self.collection.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'channel': channel.id}},
            upsert=True
        )
        await ctx.send(f'Logging channel set to {channel.mention}')

    @logging.command(
        description="Shows the logging config.",
        name='config',
        aliases=['show'],
        usage="logging config"
    )
    async def config(self, ctx):
        guild_data = self.collection.find_one({'_id': ctx.guild.id})
        if guild_data:
            channel = ctx.guild.get_channel(guild_data['channel'])
            if channel:
                await ctx.send(f'Logging channel: {channel.mention}')
            else:
                await ctx.send('Invalid logging channel')
        else:
            await ctx.send('No logging channel set')

    @logging.command(
        description="Delete the logging configuration.",
        name='delete',
        usage="logging delete"
    )
    async def delete(self, ctx):
        self.collection.delete_one({'_id': ctx.guild.id})
        await ctx.send('Logging configuration deleted')

    async def send_log(self, guild, message=None, embed=None):
        guild_data = self.collection.find_one({'_id': guild.id})
        if guild_data:
            channel = guild.get_channel(guild_data['channel'])
            if channel:
                try:
                    if embed:
                        await channel.send(embed=embed)
                    else:
                        utc_time = datetime.datetime.utcnow()
                        ist = pytz.timezone('Asia/Kolkata')
                        ist_time = utc_time.replace(tzinfo=pytz.utc).astimezone(ist)
                        formatted_time = ist_time.strftime("%Y-%m-%d %I:%M:%S %p")
                        embed = discord.Embed(description=message, color=0x977FD7)
                        embed.set_author(
                            name=f'Luka Logs | {guild.name}',
                            icon_url=guild.icon.url if guild.icon else None
                        )
                        embed.set_footer(text=f"Luka Loggings | {formatted_time}")
                        await channel.send(embed=embed)
                except discord.errors.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.bot.wait_until_ready()
        if not member.guild or not member.guild.me.guild_permissions.view_audit_log:
            return

        is_bot = member.bot
        added_by = None
        if is_bot:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                if entry.target.id == member.id:
                    added_by = entry.user

        embed = discord.Embed(
            title="Bot Added" if is_bot else "Member Joined",
            description=(
                f"**User:** {member.mention}\n"
                f"**ID:** {member.id}\n"
                f"**Created:** <t:{int(member.created_at.timestamp())}:R>"
            ),
            color=0x977FD7
        )
        if added_by:
            embed.add_field(name="Added By", value=f"{added_by.mention} ({added_by.id})")
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        await self.send_log(member.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.bot.wait_until_ready()
        if not member.guild or not member.guild.me.guild_permissions.view_audit_log:
            return

        kicked = False
        kicked_by = None
        reason = None
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                kicked = True
                kicked_by = entry.user
                reason = entry.reason

        roles = [role.mention for role in member.roles if role != member.guild.default_role]

        embed = discord.Embed(
            title="Member Kicked" if kicked else "Member Left",
            description=(
                f"**User:** {member.mention}\n"
                f"**ID:** {member.id}\n"
                f"**Created:** <t:{int(member.created_at.timestamp())}:R>\n"
                f"**Roles:** {', '.join(roles) if roles else 'None'}"
            ),
            color=0x977FD7
        )

        if kicked:
            if kicked_by:
                embed.add_field(name="Kicked By", value=f"{kicked_by.mention} ({kicked_by.id})")
            if reason:
                embed.add_field(name="Reason", value=reason)

        embed.set_author(name=str(member), icon_url=member.display_avatar.url)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Left at {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")

        await self.send_log(member.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await self.bot.wait_until_ready()
        if not after.guild or not after.guild.me.guild_permissions.view_audit_log:
            return

        embed = None
        if before.display_name != after.display_name:
            async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                changed_by = entry.user
            embed = discord.Embed(
                title="Nickname Changed",
                description=(
                    f"**User:** {after.mention}\n"
                    f"**Before:** {before.display_name}\n"
                    f"**After:** {after.display_name}"
                ),
                color=0x977FD7
            )
            embed.add_field(name="Changed By", value=f"{changed_by.mention} ({changed_by.id})")

        elif len(before.roles) != len(after.roles):
            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)
            async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update):
                changed_by = entry.user
                reason = entry.reason
            embed = discord.Embed(
                title="Roles Updated",
                description=f"**User:** {after.mention}",
                color=0x977FD7
            )
            if added:
                embed.add_field(name="Added Roles", value=', '.join([r.mention for r in added]))
            if removed:
                embed.add_field(name="Removed Roles", value=', '.join([r.mention for r in removed]))
            embed.add_field(name="Updated By", value=f"{changed_by.mention} ({changed_by.id})")
            if reason:
                embed.add_field(name="Reason", value=reason)

        if embed:
            embed.set_author(name=str(after), icon_url=after.display_avatar.url)
            await self.send_log(after.guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.bot.wait_until_ready()
        if not guild.me.guild_permissions.view_audit_log:
            return

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            banned_by = entry.user
            reason = entry.reason

        embed = discord.Embed(
            title="Member Banned",
            description=(
                f"**User:** {user.mention}\n"
                f"**ID:** {user.id}\n"
                f"**Created:** <t:{int(user.created_at.timestamp())}:R>"
            ),
            color=0x977FD7
        )
        embed.add_field(name="Banned By", value=f"{banned_by.mention} ({banned_by.id})")
        if reason:
            embed.add_field(name="Reason", value=reason)
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        await self.send_log(guild, embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await self.bot.wait_until_ready()
        if not guild.me.guild_permissions.view_audit_log:
            return

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            unbanned_by = entry.user
            reason = entry.reason

        embed = discord.Embed(
            title="Member Unbanned",
            description=(
                f"**User:** {user.mention}\n"
                f"**ID:** {user.id}\n"
                f"**Created:** <t:{int(user.created_at.timestamp())}:R>"
            ),
            color=0x977FD7
        )
        embed.add_field(name="Unbanned By", value=f"{unbanned_by.mention} ({unbanned_by.id})")
        if reason:
            embed.add_field(name="Reason", value=reason)
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        await self.send_log(guild, embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        message = payload.cached_message
        if not message or not message.attachments:
            return

        guild = self.bot.get_guild(payload.guild_id)
        embed = discord.Embed(
            title="Image Message Deleted",
            description=f"**Channel:** {message.channel.mention}\n**Author:** {message.author.mention}",
            color=0xff0000
        )
        embed.set_image(url=message.attachments[0].proxy_url)
        await self.send_log(guild, embed=embed)
        
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        embed = discord.Embed(
            title="Invite Created",
            description=f"**Code:** {invite.code}\n**Uses:** {invite.max_uses}\n**Expires:** {invite.expires_at}",
            color=0x00ff00
        )
        await self.send_log(invite.guild, embed=embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        embed = discord.Embed(
            title="Invite Deleted",
            description=f"**Code:** {invite.code}",
            color=0xff0000
        )
        await self.send_log(invite.guild, embed=embed)
        
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.timed_out_until != after.timed_out_until:
            async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_update):
                moderator = entry.user
                break

            embed = discord.Embed(
                title="Member Timed Out" if after.timed_out_until else "Timeout Removed",
                description=f"**Member:** {after.mention}\n**Expires:** {after.timed_out_until}",
                color=0xffa500
            )
            embed.add_field(name="Moderator", value=moderator.mention)
            await self.send_log(after.guild, embed=embed)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.cog_name == "Moderation":
            embed = discord.Embed(
                title="Mod Command Used",
                description=f"**Command:** {ctx.command}\n**User:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}",
                color=0x7289da
            )
            await self.send_log(ctx.guild, embed=embed)



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not before.channel and after.channel:
            # Join
            embed = discord.Embed(
                title="Voice Channel Joined",
                description=f"**Member:** {member.mention}\n**Channel:** {after.channel.mention}",
                color=0x00ff00
            )
        elif before.channel and not after.channel:
            # Leave
            embed = discord.Embed(
                title="Voice Channel Left",
                description=f"**Member:** {member.mention}\n**Channel:** {before.channel.mention}",
                color=0xff0000
            )
        elif before.channel != after.channel:
            # Move
            embed = discord.Embed(
                title="Voice Channel Moved",
                description=f"**Member:** {member.mention}\n**From:** {before.channel.mention}\n**To:** {after.channel.mention}",
                color=0x0000ff
            )
        else:
            return

        await self.send_log(member.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        for emoji in after:
            old_emoji = next((e for e in before if e.id == emoji.id), None)
            if old_emoji and old_emoji.name != emoji.name:
                embed = discord.Embed(
                    title="Emoji Renamed",
                    description=f"**Old Name:** {old_emoji.name}\n**New Name:** {emoji.name}",
                    color=0xffff00
                )
                embed.set_thumbnail(url=emoji.url)
                await self.send_log(guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.bot.wait_until_ready()
        if not role.guild.me.guild_permissions.view_audit_log:
            return

        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            created_by = entry.user

        perms = ', '.join([perm for perm, value in role.permissions if value])
        embed = discord.Embed(
            title="Role Created",
            description=f"**Role:** {role.mention}",
            color=0x977FD7
        )
        embed.add_field(name="Name", value=role.name)
        embed.add_field(name="Color", value=str(role.color))
        embed.add_field(name="Permissions", value=perms or "None")
        embed.add_field(name="Created By", value=f"{created_by.mention} ({created_by.id})")
        embed.set_author(name=str(role.guild), icon_url=role.guild.icon.url if role.guild.icon else None)
        await self.send_log(role.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.bot.wait_until_ready()
        if not role.guild.me.guild_permissions.view_audit_log:
            return

        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            deleted_by = entry.user

        embed = discord.Embed(
            title="Role Deleted",
            description=f"**Role:** {role.name}",
            color=0x977FD7
        )
        embed.add_field(name="Name", value=role.name)
        embed.add_field(name="Color", value=str(role.color))
        embed.add_field(name="Deleted By", value=f"{deleted_by.mention} ({deleted_by.id})")
        embed.set_author(name=str(role.guild), icon_url=role.guild.icon.url if role.guild.icon else None)
        await self.send_log(role.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        await self.bot.wait_until_ready()
        if not after.guild.me.guild_permissions.view_audit_log:
            return

        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
            updated_by = entry.user

        embed = discord.Embed(
            title="Role Updated",
            description=f"**Role:** {after.mention}",
            color=0x977FD7
        )
        if before.name != after.name:
            embed.add_field(name="Name", value=f"{before.name} → {after.name}")
        if before.color != after.color:
            embed.add_field(name="Color", value=f"{before.color} → {after.color}")
        if before.permissions != after.permissions:
            added = [perm for perm, value in after.permissions if perm not in before.permissions or before.permissions[perm] != value]
            removed = [perm for perm, value in before.permissions if perm not in after.permissions or after.permissions[perm] != value]
            if added:
                embed.add_field(name="Added Permissions", value=', '.join(added))
            if removed:
                embed.add_field(name="Removed Permissions", value=', '.join(removed))
        embed.add_field(name="Updated By", value=f"{updated_by.mention} ({updated_by.id})")
        embed.set_author(name=str(after.guild), icon_url=after.guild.icon.url if after.guild.icon else None)
        await self.send_log(after.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.bot.wait_until_ready()
        if not channel.guild.me.guild_permissions.view_audit_log:
            return

        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            created_by = entry.user

        embed = discord.Embed(
            title=f"{str(channel.type).title()} Channel Created",
            description=f"**Channel:** {channel.mention}",
            color=0x977FD7
        )
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Created By", value=f"{created_by.mention} ({created_by.id})")
        embed.set_author(name=str(channel.guild), icon_url=channel.guild.icon.url if channel.guild.icon else None)
        await self.send_log(channel.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.bot.wait_until_ready()
        if not channel.guild.me.guild_permissions.view_audit_log:
            return

        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            deleted_by = entry.user

        embed = discord.Embed(
            title=f"{str(channel.type).title()} Channel Deleted",
            description=f"**Channel:** {channel.name}",
            color=0x977FD7
        )
        embed.add_field(name="Name", value=channel.name)
        embed.add_field(name="Deleted By", value=f"{deleted_by.mention} ({deleted_by.id})")
        embed.set_author(name=str(channel.guild), icon_url=channel.guild.icon.url if channel.guild.icon else None)
        await self.send_log(channel.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        await self.bot.wait_until_ready()
        if not after.guild.me.guild_permissions.view_audit_log:
            return

        async for entry in after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
            updated_by = entry.user

        embed = discord.Embed(
            title=f"{str(after.type).title()} Channel Updated",
            description=f"**Channel:** {after.mention}",
            color=0x977FD7
        )
        if before.name != after.name:
            embed.add_field(name="Name", value=f"{before.name} → {after.name}")
        if isinstance(before, discord.TextChannel) and isinstance(after, discord.TextChannel):
            if before.topic != after.topic:
                embed.add_field(name="Topic", value=f"{before.topic} → {after.topic}")
        embed.add_field(name="Updated By", value=f"{updated_by.mention} ({updated_by.id})")
        embed.set_author(name=str(after.guild), icon_url=after.guild.icon.url if after.guild.icon else None)
        await self.send_log(after.guild, embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        await self.bot.wait_until_ready()
        if not after.me.guild_permissions.view_audit_log:
            return

        async for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            updated_by = entry.user

        embed = discord.Embed(
            title="Server Updated",
            color=0x977FD7
        )
        if before.name != after.name:
            embed.add_field(name="Name", value=f"{before.name} → {after.name}")
        if before.icon != after.icon:
            embed.add_field(name="Icon", value="Updated")
        if before.owner != after.owner:
            embed.add_field(name="Owner", value=f"{before.owner.mention} → {after.owner.mention}")
        embed.add_field(name="Updated By", value=f"{updated_by.mention} ({updated_by.id})")
        embed.set_author(name=str(after), icon_url=after.icon.url if after.icon else None)
        embed.add_field(name="Updated By", value=f"{updated_by.mention} ({updated_by.id})")
        
        # Banner changes
        if before.banner != after.banner:
            before_banner = f"[Before Banner]({before.banner.url})" if before.banner else "None"
            after_banner = f"[After Banner]({after.banner.url})" if after.banner else "None"
            embed.add_field(name="Banner Changed", value=f"{before_banner} → {after_banner}", inline=False)

        # Description changes
        if before.description != after.description:
            embed.add_field(
                name="Description Changed",
                value=f"**Before:**\n{before.description or 'None'}\n**After:**\n{after.description or 'None'}",
                inline=False
            )

        # Verification level changes
        if before.verification_level != after.verification_level:
            embed.add_field(
                name="Verification Level",
                value=f"{str(before.verification_level).title()} → {str(after.verification_level).title()}"
            )

        # Server features changes
        if before.features != after.features:
            added = [f"✅ {f.replace('_', ' ').title()}" for f in after.features if f not in before.features]
            removed = [f"❌ {f.replace('_', ' ').title()}" for f in before.features if f not in after.features]
            
            if added or removed:
                features_text = "\n".join(added + removed)
                embed.add_field(name="Features Updated", value=features_text, inline=False)

        # System channel changes
        if before.system_channel != after.system_channel:
            before_channel = before.system_channel.mention if before.system_channel else "None"
            after_channel = after.system_channel.mention if after.system_channel else "None"
            embed.add_field(name="System Channel", value=f"{before_channel} → {after_channel}")

        # Rules channel changes
        if before.rules_channel != after.rules_channel:
            before_rules = before.rules_channel.mention if before.rules_channel else "None"
            after_rules = after.rules_channel.mention if after.rules_channel else "None"
            embed.add_field(name="Rules Channel", value=f"{before_rules} → {after_rules}")

        # AFK Channel/Timeout changes
        if before.afk_channel != after.afk_channel or before.afk_timeout != after.afk_timeout:
            afk_text = ""
            if before.afk_channel != after.afk_channel:
                before_afk = before.afk_channel.mention if before.afk_channel else "None"
                after_afk = after.afk_channel.mention if after.afk_channel else "None"
                afk_text += f"**Channel:** {before_afk} → {after_afk}\n"
            if before.afk_timeout != after.afk_timeout:
                afk_text += f"**Timeout:** {before.afk_timeout//60}m → {after.afk_timeout//60}m"
            embed.add_field(name="AFK Settings Changed", value=afk_text)

        # Vanity URL changes
        if 'VANITY_URL' in before.features and 'VANITY_URL' in after.features:
            try:
                before_vanity = await before.vanity_invite()
                after_vanity = await after.vanity_invite()
                if before_vanity.code != after_vanity.code:
                    embed.add_field(
                        name="Vanity URL Changed",
                        value=f"`discord.gg/{before_vanity.code}` → `discord.gg/{after_vanity.code}`",
                        inline=False
                    )
            except discord.NotFound:
                pass

        # Splash screen changes
        if before.splash != after.splash:
            before_splash = f"[Before Splash]({before.splash.url})" if before.splash else "None"
            after_splash = f"[After Splash]({after.splash.url})" if after.splash else "None"
            embed.add_field(name="Splash Screen Changed", value=f"{before_splash} → {after_splash}", inline=False)

        # Add audit log reason if available
        if entry.reason:
            embed.add_field(name="Reason", value=entry.reason, inline=False)

        # Finalize embed formatting
        embed.set_author(name=str(after), icon_url=after.icon.url if after.icon else None)
        embed.set_thumbnail(url=after.icon.url if after.icon else None)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f"Server ID: {after.id}")

        await self.send_log(after, embed=embed)       
        
        
def setup(bot):
    bot.add_cog(Logging(bot))
