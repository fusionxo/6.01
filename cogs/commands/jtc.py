import discord
from discord.ext import commands
from discord import ui
import asyncio
import sqlite3
import traceback
from utils import *
from utils.checks import global_check

# --- Helper Functions ---

async def get_voice_channel(interaction: discord.Interaction):
    """Helper function to get the voice channel."""
    conn = sqlite3.connect('databases/voice.db')
    c = conn.cursor()
    c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))
    voice = c.fetchone()
    conn.close()
    if not voice:
        await interaction.response.send_message("You don't own a channel.", ephemeral=True)
        return None
    channel = interaction.guild.get_channel(voice[0])
    if not channel:
        await interaction.response.send_message("Channel not found.", ephemeral=True)
        return None
    return channel

async def get_text_channel_id(channel_id):
    """Helper function to get the text channel ID."""
    conn = sqlite3.connect('databases/voice.db')
    c = conn.cursor()
    c.execute("SELECT textChannelID FROM voiceChannel WHERE voiceID = ?", (channel_id,))
    text_channel_data = c.fetchone()
    conn.close()
    if text_channel_data:
        return text_channel_data[0]
    return None

async def send_error(interaction: discord.Interaction, error_message: str):
    """Helper function to send an error message."""
    try:
        await interaction.response.send_message(error_message, ephemeral=True)
    except discord.errors.Forbidden:
        print(f"Bot lacks permission to send messages in this channel: {interaction.channel.id}")

# --- Region Selection ---
class RegionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="", emoji="🌍", style=discord.ButtonStyle.secondary, custom_id="vc_change_region", row=2)

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=60)
        view.add_item(RegionSelect(self.view.bot))
        await interaction.response.send_message("Select a region:", view=view, ephemeral=True)

class RegionSelect(discord.ui.Select):
    def __init__(self, bot):
        options = [

            discord.SelectOption(label="Automatic", description="Let Discord choose the best region", emoji="🌐"),
            discord.SelectOption(label="US West", description="Western United States", emoji="🇺🇸"),
            discord.SelectOption(label="US East", description="Eastern United States", emoji="🇺🇸"),
            discord.SelectOption(label="Brazil", description="Brazil", emoji="🇧🇷"),
            discord.SelectOption(label="Japan", description="Japan", emoji="🇯🇵"),
            discord.SelectOption(label="Singapore", description="Singapore", emoji="🇸🇬"),
            discord.SelectOption(label="Sydney", description="Sydney, Australia", emoji="🇦🇺"),
            discord.SelectOption(label="India", description="India", emoji="🇮🇳"),
            discord.SelectOption(label="South Korea", description="South Korea", emoji="🇰🇷")
        ]
        super().__init__(placeholder="Select Voice Region", options=options, custom_id="region_select")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()
        try:
            c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))
            voice = c.fetchone()

            if not voice:
                await interaction.response.send_message("You don't own a channel.", ephemeral=True)
                return


            channel = interaction.guild.get_channel(voice[0])
            if not channel:
                await interaction.response.send_message("Channel not found.", ephemeral=True)
                return

            region = self.values[0]
            region_map = {
                "US West": "us-west",
                "US East": "us-east",
                "Brazil": "brazil",
                "Japan": "japan",
                "Singapore":  "singapore",
                "Sydney": "sydney",
                "India": "india",
                "South Korea": "south-korea",
                "Automatic": None
            }


            await channel.edit(rtc_region=region_map[region])
            await interaction.response.send_message(f"Voice region changed to {region}!", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        finally:
            conn.close()

# --- Privacy Dropdown ---
class PrivacyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="",
            emoji="🔒",
            style=discord.ButtonStyle.secondary,
            custom_id="vc_privacy",
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=60)
        view.add_item(PrivacySelect(self.view.bot))

        await interaction.response.send_message("Select privacy action:", view=view, ephemeral=True)

class PrivacySelect(discord.ui.Select):
    def __init__(self, bot):
        options = [
            discord.SelectOption(label="Lock", emoji="🔒", description="Prevent others from joining"),
            discord.SelectOption(label="Unlock", emoji="🔓", description="Allow everyone to join"),
            discord.SelectOption(label="Hide", emoji="👻", description="Hide channel from others"),
            discord.SelectOption(label="Unhide", emoji="👋", description="Make channel visible")

        ]
        super().__init__(placeholder="Select privacy action...", options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()
        try:
            c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))
            voice = c.fetchone()

            if not voice:
                await interaction.response.send_message("You don't own a channel.", ephemeral=True)
                return

            channel = interaction.guild.get_channel(voice[0])
            if not channel:
                await interaction.response.send_message("Channel not found.", ephemeral=True)
                return

            action = self.values[0]
            role = interaction.guild.default_role
            owner = interaction.guild.get_member(interaction.user.id)

            if action == "Lock":
                await channel.set_permissions(role, connect=False, view_channel=True)
                await channel.set_permissions(owner, connect=True)
                await interaction.response.send_message("🔒 Channel locked! Others can see but can't join.", ephemeral=True)

            elif action == "Unlock":
                await channel.set_permissions(role, connect=True)
                await interaction.response.send_message("🔓 Channel unlocked!", ephemeral=True)


            elif action == "Hide":
                await channel.set_permissions(role, view_channel=False)
                await channel.set_permissions(owner, view_channel=True)
                await interaction.response.send_message("👻 Channel hidden!", ephemeral=True)

            elif action == "Unhide":

                await channel.set_permissions(role, view_channel=True)
                await interaction.response.send_message("👋 Channel visible!", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        finally:
            conn.close()

# --- User Actions ---
class UserActionSelect(ui.UserSelect):

    def __init__(self, bot, action_type):
        self.action_type = action_type
        placeholder = {
            "trust": "Select user to trust",
            "untrust": "Select user to untrust",
            "block": "Select user to block",
            "unblock": "Select user to unblock",

            "transfer": "Select new owner",
            "kick": "Select user to kick"
        }.get(action_type, "Select user")

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            custom_id=f"{action_type}_select"

        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()
        try:
            c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))
            voice = c.fetchone()


            if not voice:
                await interaction.response.send_message("You don't own a channel.", ephemeral=True)
                return

            channel = interaction.guild.get_channel(voice[0])
            if not channel:

                await interaction.response.send_message("Channel not found.", ephemeral=True)
                return

            user = self.values[0]

            if self.action_type == "block" and user.id == interaction.user.id:
                await interaction.response.send_message("You can't block yourself!", ephemeral=True)

                return

            if self.action_type == "trust":
                await channel.set_permissions(user, connect=True)
                await interaction.response.send_message(f"Trusted {user.display_name}!", ephemeral=True)

            elif self.action_type == "untrust":

                await channel.set_permissions(user, overwrite=None)
                await interaction.response.send_message(f"Removed trust from {user.display_name}!", ephemeral=True)

            elif self.action_type == "block":

                if user.voice and user.voice.channel == channel:
                    await user.move_to(None)
                await channel.set_permissions(user, connect=False)
                await interaction.response.send_message(f"Blocked {user.display_name}!", ephemeral=True)

            elif self.action_type == "unblock":

                await channel.set_permissions(user, overwrite=None)
                await interaction.response.send_message(f"Unblocked {user.display_name}!", ephemeral=True)

            elif self.action_type == "transfer":
                if len(channel.members) < 2:
                    await interaction.response.send_message("No other members in the channel to transfer to!", ephemeral=True)
                    return

                if user.bot:
                    await interaction.response.send_message("Cannot transfer ownership to a bot.", ephemeral=True)
                    return


                c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (user.id, channel.id))
                conn.commit()
                await interaction.response.send_message(f"Ownership transferred to {user.display_name}!", ephemeral=True)
                if hasattr(self.view, 'message'):
                    await self.view.message.edit(content=f"Voice Control Panel - Owner: {user.mention}")

            elif self.action_type == "kick":
                if user.voice and user.voice.channel == channel:
                    await user.move_to(None)
                    await interaction.response.send_message(f"Kicked {user.display_name}!", ephemeral=True)
                else:

                    await interaction.response.send_message("User is not in your channel.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        finally:
            conn.close()

# --- VC Modals ---
class VCModal(ui.Modal):
    def __init__(self, title, action_type):
        super().__init__(title=title, timeout=None)
        self.action_type = action_type

        if action_type == "limit":
            self.add_item(ui.TextInput(
                label="User Limit (0-99)",
                placeholder="Enter number between 0-99",

                min_length=1,
                max_length=2
            ))
        else:
            self.add_item(ui.TextInput(
                label="New Channel Name",
                placeholder="Enter new channel name",

                min_length=1,
                max_length=100
            ))

    async def on_submit(self, interaction: discord.Interaction):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()
        try:
            c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))

            voice = c.fetchone()

            if not voice:
                await interaction.response.send_message("You don't own a channel.", ephemeral=True)
                return

            channel = interaction.guild.get_channel(voice[0])
            if not channel:

                await interaction.response.send_message("Channel not found.", ephemeral=True)
                return

            value = self.children[0].value

            if self.action_type == "limit":

                try:
                    limit = int(value)
                    if 0 <= limit <= 99:
                        await channel.edit(user_limit=limit)

                        await interaction.response.send_message(f"User limit set to {limit}!", ephemeral=True)
                    else:
                        await interaction.response.send_message("Please enter a number between 0-99!", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("Please enter a valid number!", ephemeral=True)
            elif self.action_type == "rename":
                try:
                    await channel.edit(name=value)
                    await interaction.response.send_message(f"Channel renamed to {value}!", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"Couldn't rename channel: {str(e)}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        finally:
            conn.close()

# --- Action Buttons ---
class UserActionButton(discord.ui.Button):
    def __init__(self, label, emoji, style, action_type, row):
        super().__init__(label="", emoji=emoji, style=style, custom_id=f"vc_{action_type}", row=row)
        self.action_type = action_type

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()
        try:
            if self.action_type in ["trust", "block", "transfer", "kick", "untrust", "unblock"]:
                select = UserActionSelect(self.view.bot, self.action_type)

                c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))
                voice = c.fetchone()

                if not voice:
                    await interaction.response.send_message("You don't own a channel.", ephemeral=True)
                    return

                channel = interaction.guild.get_channel(voice[0])

                if self.action_type == "kick":
                    members  = [m for m in channel.members if m.id != interaction.user.id]
                else:
                    members = [m for m in interaction.guild.members if not m.bot and m.id != interaction.user.id]

                if not members:
                    msg = {
                        "kick": "No users in your channel to kick.",
                        "trust": "No users available to trust.",
                        "block": "No  users available to block.",
                        "transfer": "No users available to transfer to.",
                        "untrust": "No users available to untrust.",
                        "unblock": "No users available to unblock."
                    }.get(self.action_type, "No users available.")
                    await interaction.response.send_message(msg, ephemeral=True)
                    return

                members = sorted(members, key=lambda m: m.display_name)[:25]

                select.options = [
                    discord.SelectOption(
                        label=f"{member.display_name} ({member})",
                        value=str(member.id),
                        description=f"ID: {member.id}"
                    ) for member in members
                ]

                view = discord.ui.View(timeout=60)
                view.add_item(select)
                await interaction.response.send_message(f"Select a user to {self.action_type}:", view=view, ephemeral=True)
                return

            elif self.action_type in ["limit", "rename"]:
                modal = VCModal(
                    title=f"VC {self.action_type.capitalize()}",
                    action_type=self.action_type
                )
                await interaction.response.send_modal(modal)
                return

            elif self.action_type == "claim":
                if not interaction.user.voice or not interaction.user.voice.channel:
                    await interaction.response.send_message("You must be in a voice channel to claim it.", ephemeral=True)
                    return

                voice_id = interaction.user.voice.channel.id
                c.execute("SELECT userID FROM voiceChannel WHERE voiceID = ?", (voice_id,))
                owner_data = c.fetchone()

                if not owner_data:
                    await interaction.response.send_message("This channel cannot be claimed.", ephemeral=True)
                    return

                owner_id = owner_data[0]
                owner = interaction.guild.get_member(owner_id)
                channel = interaction.guild.get_channel(voice_id)

                if not channel:
                    await interaction.response.send_message("Channel not found.", ephemeral=True)
                    return

                if owner in channel.members:
                    await interaction.response.send_message("Current owner is still in the channel.", ephemeral=True)
                    return

                try:
                    c.execute("UPDATE voiceChannel SET userID = ? WHERE voiceID = ?", (interaction.user.id, voice_id))
                    conn.commit()
                    await interaction.response.send_message("✅ Channel ownership claimed!", ephemeral=True)
                except sqlite3.Error as e:
                    await interaction.response.send_message(f"Database error: {str(e)}", ephemeral=True)
                return

            elif self.action_type == "delete":
                c.execute("SELECT voiceID FROM voiceChannel WHERE userID = ?", (interaction.user.id,))
                voice = c.fetchone()

                if not voice:
                    await interaction.response.send_message("You don't own a channel.", ephemeral=True)
                    return

                channel = interaction.guild.get_channel(voice[0])
                if not channel:
                    await interaction.response.send_message("Channel not found.", ephemeral=True)
                    return

                await channel.delete()
                c.execute("DELETE FROM voiceChannel WHERE voiceID = ?", (channel.id,))
                conn.commit()
                await interaction.response.send_message("🗑️ Channel deleted!", ephemeral=True)

        except Exception as e:
            traceback.print_exc()
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
        finally:
            conn.close()

# --- Main Control View ---
class VoiceControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot


        self.add_item(PrivacyButton())
        self.add_item(UserActionButton("", "✅", discord.ButtonStyle.secondary, "trust", 0))
        self.add_item(UserActionButton("", "❌", discord.ButtonStyle.secondary, "untrust", 0))
        self.add_item(UserActionButton("", "🚫", discord.ButtonStyle.secondary, "block", 0))

        self.add_item(UserActionButton("", "🔓", discord.ButtonStyle.secondary, "unblock", 1))
        self.add_item(UserActionButton("", "🚪", discord.ButtonStyle.secondary, "kick", 1))
        self.add_item(UserActionButton("", "📝", discord.ButtonStyle.secondary, "rename", 1))
        self.add_item(UserActionButton("", "👥", discord.ButtonStyle.secondary, "limit", 1))

        self.add_item(UserActionButton("", "🔄", discord.ButtonStyle.secondary, "transfer", 2))
        self.add_item(UserActionButton("", "🏷️", discord.ButtonStyle.secondary, "claim", 2))
        self.add_item(UserActionButton("", "🗑️", discord.ButtonStyle.secondary, "delete", 2))
        self.add_item(RegionButton())


# --- Main Cog ---
class Jtc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(VoiceControlView(bot))
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help_custom(self):
		      emoji = '<:automation:1089140152674308126>'
		      label = "Join To Create"
		      description = "Shows the log Join To Create commands."
		      return emoji, label, description

    @commands.group()
    async def __JoinToCreate__(self, ctx: commands.Context):
        """• `jtc setupj2c`, `jtc deletej2c`"""
        

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()
        try:
            if member.bot:
                return

            guild_id = member.guild.id
            c.execute("SELECT voiceChannelID, voiceCategoryID FROM guild WHERE guildID = ?", (guild_id,))
            guild_data = c.fetchone()

            if not guild_data:
                return

            voice_id, category_id = guild_data

            if after.channel and after.channel.id == voice_id:
                category = self.bot.get_channel(category_id)
                voice_channel = await member.guild.create_voice_channel(
                    f"{member.display_name}'s room",
                    category=category
                )

                await member.move_to(voice_channel)

                c.execute("INSERT OR REPLACE INTO voiceChannel (userID, voiceID, textChannelID) VALUES (?, ?, ?)",
                        (member.id, voice_channel.id, None))
                conn.commit()

                embed = discord.Embed(
                    title=f"🎤 {member.display_name}'s Voice Controls",
                    description="Manage your temporary voice channel with the buttons below.",
                    color=0x977FD7
                )
                embed.add_field(name="Commands", value="🔒 Privacy Settings\n✅ Trust users\n❌ Block users\n👥 Set user limit\n📝 Rename channel\n🔄 Transfer ownership\n🚪 Kick users\n🗑️ Delete channel")
                embed.set_footer(text="This channel will be deleted when empty")

                control_message = await voice_channel.send(
                    content=f"Voice Control Panel - Owner: {member.mention}",
                    embed=embed, 
                    view=VoiceControlView(self.bot),
                    allowed_mentions=discord.AllowedMentions(users=False)
                )

                while True:
                    await asyncio.sleep(1)
                    channel = self.bot.get_channel(voice_channel.id)
                    if not channel:
                        break

                    if len(channel.members) == 0:
                        await asyncio.sleep(1)
                        channel = self.bot.get_channel(voice_channel.id)
                        if channel and len(channel.members) == 0:
                            await channel.delete()

                        c.execute("DELETE FROM voiceChannel WHERE voiceID = ?", (voice_channel.id,))
                        conn.commit()
                        break

        except Exception as e:
            traceback.print_exc()
        finally:
            conn.close()

    @commands.hybrid_group()
    async def jtc(self, ctx):
        """Join-to-Create voice channel system"""
        pass

    @jtc.command(description="Set up Join-to-Create system")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()

        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS guild (
                    guildID INTEGER PRIMARY KEY,
                    ownerID INTEGER,
                    voiceChannelID INTEGER,
                    voiceCategoryID INTEGER
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS voiceChannel (
                    userID INTEGER,
                    voiceID INTEGER,
                    textChannelID INTEGER,
                    PRIMARY KEY (userID)
                )
            """)

            category = await ctx.guild.create_category("Temporary Voice Channels")
            jtc_channel = await ctx.guild.create_voice_channel("Join to Create", category=category)

            c.execute("INSERT OR REPLACE INTO guild (guildID, ownerID, voiceChannelID, voiceCategoryID) VALUES (?, ?, ?, ?)",
                    (ctx.guild.id, ctx.author.id, jtc_channel.id, category.id))
            conn.commit()

            embed = discord.Embed(
                title="✅ Join-to-Create System Setup Complete",
                description=f"Created join channel in {category.mention}",
                color=0x00ff00
            )
            embed.add_field(name="How it works", value="1. Users join the 'Join to Create' channel\n2. A personal voice channel is created for them\n3. They get controls to manage their channel")
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
        finally:
            conn.close()

    @jtc.command(description="Delete Join-to-Create system")
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx):
        conn = sqlite3.connect('databases/voice.db')
        c = conn.cursor()

        try:
            c.execute("SELECT voiceChannelID, voiceCategoryID FROM guild WHERE guildID = ?", (ctx.guild.id,))
            data = c.fetchone()

            if not data:
                await ctx.send("No Join-to-Create setup found.")
                return

            voice_id, category_id = data
            category = ctx.guild.get_channel(category_id)

            if category:
                for channel in category.channels:
                    try:
                        await channel.delete()
                    except:
                        continue

                await category.delete()

            c.execute("DELETE FROM guild WHERE guildID = ?", (ctx.guild.id,))
            c.execute("DELETE FROM voiceChannel WHERE voiceID IN (SELECT voiceID FROM voiceChannel JOIN guild ON voiceChannel.userID = guild.ownerID WHERE guild.guildID = ?)", 
                     (ctx.guild.id,))
            conn.commit()

            await ctx.send("❌ Join-to-Create system has been completely removed!")

        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
        finally:
            conn.close()

async def setup(bot):
    await bot.add_cog(Jtc(bot))