"""import discord
import json
import difflib
import requests
from datetime import datetime, timedelta
import asyncio
from profanity import profanity
import re
import logging
from textblob import TextBlob
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

WEBHOOK_URL = "https://discord.com/api/webhooks/1252164363876565033/rx2goSoniu2zmwPVGFUBdda8nISUIV6qvmXohxThqTRoTDgLFOir6d6HDJbQcHs_xYWG"
IGNORED_USER_IDS = [684281787178156060]
MAX_WARNINGS = 5
DEFAULT_FEATURES = {
    "blocked_words": True,
    "sentiment_analysis": True,
    "anti_spam": True,
    "anti_link": True,
    "hindi_profanity": True,
    "profanity_filter": True
}

"" TDL :
            MAKE THE LOG CHANNEL CREATE AFTER THE EXECUTION OF AIMOD ENABLE
            FIX BUGS
""


class AIMO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_messages = {}  # To track recent messages for spam detection
        self.user_warnings = {}
        self.blocked_words = []
        self.blocked_messages = []
        self.hindi_profane_words = []
        self.log_channels = {}
        self.load_data()

    def load_data(self):
        self.blocked_words = self.load_json('jsons/blocked_words.json', [])
        self.blocked_messages = self.load_json('jsons/blocked_messages.json', [])
        self.user_warnings = self.load_json('jsons/user_warnings.json', {})
        self.hindi_profane_words = self.load_txt('txts/hindiprofan.txt')
        self.log_channels = self.load_json('jsons/aimochnl.json', {})

    @staticmethod
    def load_json(filepath, default):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"{filepath} not found, initializing with default.")
            return default

    @staticmethod
    def load_txt(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f]
        except FileNotFoundError:
            logging.error(f"{filepath} not found, initializing with an empty list.")
            return []

    def save_data(self):
        self.save_json('jsons/user_warnings.json', self.user_warnings)
        self.save_json('jsons/blocked_words.json', self.blocked_words)
        self.save_json('jsons/blocked_messages.json', self.blocked_messages)
        self.save_json('jsons/aimochnl.json', self.log_channels)

    @staticmethod
    def save_json(filepath, data):
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def get_guild_features(self, guild_id):
        return self.log_channels.get(str(guild_id), DEFAULT_FEATURES.copy())

    def save_guild_settings(self):
        self.save_json('jsons/aimochnl.json', self.log_channels)

    def is_word_blocked(self, word):
        return any(difflib.SequenceMatcher(None, blocked_word, word).ratio() >= 0.8 for blocked_word in self.blocked_words)

    def is_hindi_profane(self, word):
        return any(difflib.SequenceMatcher(None, profane_word, word).ratio() >= 0.8 for profane_word in self.hindi_profane_words)

    def contains_link(self, message_content):
        return re.search(r"https?://\S+|www\.\S+", message_content)

    def contains_invite(self, message_content):
        return re.search(r"(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/[A-Za-z0-9]+", message_content)

    def check_blocked_words(self, message_content):
        message_words = message_content.split()
        return any(self.is_word_blocked(word) or profanity.contains_profanity(word) or self.is_hindi_profane(word) for word in message_words) \
            or self.contains_link(message_content) or self.contains_invite(message_content)

    def is_spam(self, message):
        user_id = message.author.id
        current_time = datetime.utcnow()

        if user_id not in self.recent_messages:
            self.recent_messages[user_id] = []

        self.recent_messages[user_id].append((current_time, message))

        # Remove messages older than 10 seconds
        self.recent_messages[user_id] = [msg for msg in self.recent_messages[user_id] if (current_time - msg[0]).seconds < 10]

        if len(self.recent_messages[user_id]) > 5:  # More than 5 messages in 10 seconds
            return [msg[1] for msg in self.recent_messages[user_id]]
        return False

    def analyze_sentiment(self, text):
        return TextBlob(text).sentiment.polarity

    async def timeout_member(self, member, duration, reason=None):
        try:
            timed_out_until = discord.utils.utcnow() + timedelta(minutes=duration)
            await member.edit(timed_out_until=timed_out_until, reason=reason)
        except discord.Forbidden:
            await self.send_log(member.guild.id, f"**Insufficient permissions to timeout {member.mention}.**")
        except Exception as e:
            logging.error(f"Error timing out member: {e}")

    async def send_log(self, guild_id, message):
        log_channel_id = self.log_channels.get(str(guild_id))
        channel = self.bot.get_channel(log_channel_id) if log_channel_id else None

        if not channel:
            guild = self.bot.get_guild(guild_id)
            channel = await guild.create_text_channel("luka-aimo-logs")
            self.log_channels[str(guild_id)] = channel.id
            self.save_guild_settings()

        await channel.send(embed=discord.Embed(description=message, color=discord.Color.red()))

    async def send_embed(self, channel, title, description, view=None):
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        await channel.send(embed=embed, view=view)

    @commands.group(name="aimod", invoke_without_command=True)
    async def aimod(self, ctx):
        await ctx.send("Use `aimod enable`, `aimod disable`, or `aimod recommended` to manage AI moderation.")

    # Multi-Select Dropdown Menu
    class MultiSelectDropdown(discord.ui.Select):
        def __init__(self, current_settings):
            options = [
                discord.SelectOption(label="Blocked Words", value="blocked_words", default=current_settings.get("blocked_words", False)),
                discord.SelectOption(label="Sentiment Analysis", value="sentiment_analysis", default=current_settings.get("sentiment_analysis", False)),
                discord.SelectOption(label="Anti-Spam", value="anti_spam", default=current_settings.get("anti_spam", False)),
                discord.SelectOption(label="Anti-Link", value="anti_link", default=current_settings.get("anti_link", False)),
                discord.SelectOption(label="Hindi Profanity", value="hindi_profanity", default=current_settings.get("hindi_profanity", False)),
                discord.SelectOption(label="Profanity Filter", value="profanity_filter", default=current_settings.get("profanity_filter", False))
            ]
            super().__init__(placeholder="Select features to enable/disable...", min_values=1, max_values=len(options), options=options)

        async def callback(self, interaction: discord.Interaction):
            guild_id = interaction.guild.id
            guild_features = self.view.cog.get_guild_features(guild_id)

            for feature in self.values:
                guild_features[feature] = not guild_features.get(feature, False)

            self.view.cog.save_guild_settings()
            await interaction.response.send_message(f"Features updated: {', '.join(self.values)}", ephemeral=True)

    class FeatureToggleView(discord.ui.View):
        def __init__(self, cog, current_settings):
            super().__init__()
            self.cog = cog
            self.add_item(AIMO.MultiSelectDropdown(current_settings))

    @aimod.command(name="enable", description="Enable AI moderation features")
    async def enable_aimod(self, ctx):
        current_settings = self.get_guild_features(ctx.guild.id)
        view = self.FeatureToggleView(self, current_settings)
        await self.send_embed(ctx.channel, "Enable/Disable Features", "Select features to enable/disable from the dropdown.", view=view)

    @aimod.command(name="disable", description="Disable AI moderation features")
    async def disable_aimod(self, ctx):
        current_settings = self.get_guild_features(ctx.guild.id)
        view = self.FeatureToggleView(self, current_settings)
        await self.send_embed(ctx.channel, "Enable/Disable Features", "Select features to disable from the dropdown.", view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.id in IGNORED_USER_IDS:
            return

        content = message.content.lower()
        guild_features = self.get_guild_features(message.guild.id)

        # Sentiment analysis
        if guild_features.get("sentiment_analysis") and self.analyze_sentiment(content) < -0.5:
            await self.on_message_action(message, "Message removed due to negative sentiment.")
            return

        spam_messages = self.is_spam(message)

        if (guild_features.get("blocked_words") and self.check_blocked_words(content)) or \
           (guild_features.get("anti_spam") and spam_messages):
            await self.on_message_action(message, "Message removed due to violation.")
            for msg in spam_messages:
                await msg.delete()

            user_id = str(message.author.id)
            self.user_warnings[user_id] = self.user_warnings.get(user_id, 0) + 1
            remaining_warnings = MAX_WARNINGS - self.user_warnings[user_id]

            if remaining_warnings <= 0:
                await self.timeout_member(message.author, 30, reason="AI Moderation | Max Warnings Reached")
                del self.user_warnings[user_id]
            else:
                await self.send_embed(message.channel, "Warning", f"{message.author.mention} has been warned. Warnings remaining: {remaining_warnings}")

            self.save_data()

    async def on_message_action(self, message, reason):
        await message.delete()
        await self.send_log(message.guild.id, f"Message from {message.author.mention} was deleted. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(AIMO(bot))
"""