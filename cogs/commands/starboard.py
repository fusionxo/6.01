import discord
from discord.ext import commands
from pymongo import MongoClient
import pytz
from discord.ui import Button

# MongoDB configuration
MONGO_URI = 'mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net'
DB_NAME = 'starboard'
COLLECTION_NAME = 'starboarddata'

# Default star limit
DEFAULT_STAR_LIMIT = 3

# Command Group: starboard
class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_channels = {}  # Guild ID: Starboard Channel ID
        self.star_limits = {}  # Guild ID: Star Limit
        self.starboard_messages = {}  # (Guild ID, Original Message ID): Starboard Message ID
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.load_starboard_settings()

    def load_starboard_settings(self):
        # Load starboard settings from the database
        for document in self.collection.find():
            guild_id = document['_id']
            self.starboard_channels[guild_id] = document.get('starboard_channel_id')
            self.star_limits[guild_id] = document.get('star_limit')

    def save_starboard_settings(self):
        # Save starboard settings to the database
        for guild_id in self.starboard_channels:
            document = {
                '_id': guild_id,
                'starboard_channel_id': self.starboard_channels[guild_id],
                'star_limit': self.star_limits.get(guild_id, DEFAULT_STAR_LIMIT)
            }
            self.collection.update_one({'_id': guild_id}, {'$set': document}, upsert=True)

    # Subcommand: starboard channel
    @commands.group(name='starboard')
    async def starboard(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid starboard command.')

    @starboard.group(name='channel')
    async def channel(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            # Get the current starboard channel
            guild_id = ctx.guild.id
            starboard_channel_id = self.starboard_channels.get(guild_id)
            if starboard_channel_id:
                starboard_channel = self.bot.get_channel(starboard_channel_id)
                if starboard_channel:
                    await ctx.send(f"The starboard channel is set to: {starboard_channel.mention}")
                else:
                    await ctx.send("The starboard channel no longer exists.")
            else:
                await ctx.send("The starboard channel is not set.")
        else:
            # Set the starboard channel
            self.starboard_channels[ctx.guild.id] = channel.id
            self.save_starboard_settings()
            await ctx.send(f"The starboard channel has been set to: {channel.mention}")

    # Subcommand: starboard starlimit
    @starboard.group(name='starlimit')
    async def starlimit(self, ctx, limit: int = DEFAULT_STAR_LIMIT):
        if limit < 1:
            await ctx.send("Star limit cannot be less than 1.")
        else:
            self.star_limits[ctx.guild.id] = limit
            self.save_starboard_settings()
            await ctx.send(f"The star limit has been set to: {limit}")

    # Subcommand: starboard remove
    @starboard.group(name='remove')
    async def remove(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.starboard_channels:
            del self.starboard_channels[guild_id]
            if guild_id in self.star_limits:
                del self.star_limits[guild_id]
            self.save_starboard_settings()
            await ctx.send("Starboard settings have been removed.")
        else:
            await ctx.send("Starboard settings are not set for this server.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) == "⭐":
            guild_id = payload.guild_id
            if guild_id in self.starboard_channels:
                channel = self.bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                star_count = sum([reaction.count for reaction in message.reactions if str(reaction.emoji) == "⭐"])
                star_limit = self.star_limits.get(guild_id, DEFAULT_STAR_LIMIT)
                if star_count >= star_limit:
                    starboard_channel = self.bot.get_channel(self.starboard_channels[guild_id])
                    if starboard_channel:
                        # Check if the bot is not the author of the message
                        if message.author != self.bot.user:
                            starboard_message_id = self.starboard_messages.get((guild_id, message.id))
                            if starboard_message_id:
                                # If there is already a starboard message for this original message, update it
                                starboard_message = await starboard_channel.fetch_message(starboard_message_id)
                                content = f"⭐ {star_count} | {channel.mention}"
                                embed = starboard_message.embeds[0]
                                embed.description = message.content
                                embed.set_footer(text=embed.footer.text)  # Keep the original timestamp
                                await starboard_message.edit(content=content, embed=embed)
                            else:
                                # If there is no starboard message for this original message, send a new one
                                content = f"⭐ {star_count} | {channel.mention}"
                                embed = discord.Embed(color=0x977FD7)
                                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                                tz = pytz.timezone('Asia/Kolkata')
                                timestamp = message.created_at.astimezone(tz)
                                embed.set_footer(text=timestamp.strftime("%m/%d/%Y %I:%M %p"))

                                # Add the additional fields to the embed
                                embed.add_field(name="__**Channel**__", value=f"{channel.mention}", inline=False)
                                embed.add_field(name="__**Content**__", value=message.content, inline=False)

                                # Add media attachments to the embed
                                attachments = message.attachments
                                if attachments:
                                    for attachment in attachments:
                                        if attachment.url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                            embed.set_image(url=attachment.url)
                                            break

                                # Add video attachments to the embed
                                videos = [attachment for attachment in attachments if attachment.url.endswith(('.mp4', '.mov'))]
                                if videos:
                                    embed.add_field(name="Videos", value='\n'.join([video.url for video in videos]), inline=False)

                                starboard_message = await starboard_channel.send(content=content, embed=embed)

                                # Create a button for jumping to the message
                                button = Button(style=discord.ButtonStyle.link, label="Jump to message", url=message.jump_url)
                                view = discord.ui.View()
                                view.add_item(button)

                                await starboard_message.edit(content=content, embed=embed, view=view)

                                self.starboard_messages[(guild_id, message.id)] = starboard_message.id


def setup(bot):
    bot.add_cog(Starboard(bot))
