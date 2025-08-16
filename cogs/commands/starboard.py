import discord
from discord.ext import commands
import motor.motor_asyncio
import pytz
from utils.checks import global_check
from discord.ui import Button, View

MONGO_URI = "mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net"
DB_NAME = 'starboard'
DEFAULT_STAR_LIMIT = 3
STAR_EMOJI = "⭐"
TZ = pytz.timezone('Asia/Kolkata')

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        self.db = self.mongo_client[DB_NAME]
        self.settings_collection = self.db['settings']
        self.posts_collection = self.db['posts']
        self.settings_cache = {}
        self.bot.loop.create_task(self.load_all_settings())

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)

    def help_custom(self):
        emoji = '<:sstar:1089111407712276580>'
        label = "Starboard"
        description = "A robust starboard system."
        return emoji, label, description

    async def load_all_settings(self):
        cursor = self.settings_collection.find({})
        async for document in cursor:
            guild_id = document.get('_id')
            if guild_id:
                self.settings_cache[guild_id] = {
                    'channel_id': document.get('starboard_channel_id'),
                    'limit': document.get('star_limit', DEFAULT_STAR_LIMIT)
                }
        print("Starboard settings loaded into cache.")

    @commands.group(name='starboard', invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def starboard(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        settings = self.settings_cache.get(guild_id)
        if not settings or not settings.get('channel_id'):
            await ctx.send("The starboard is not yet configured. Use `starboard channel <#channel>` to set it up.")
            return
        starboard_channel = self.bot.get_channel(settings['channel_id'])
        embed = discord.Embed(
            title="Starboard Settings",
            color=0x977FD7,
            description=f"Here are the current settings for {ctx.guild.name}'s starboard."
        )
        embed.add_field(name="Channel", value=starboard_channel.mention if starboard_channel else "Not Set or Channel Deleted", inline=False)
        embed.add_field(name="Star Limit", value=settings.get('limit', DEFAULT_STAR_LIMIT), inline=False)
        await ctx.send(embed=embed)

    @starboard.command(name='channel')
    @commands.has_permissions(manage_guild=True)
    async def set_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        try:
            await self.settings_collection.update_one(
                {'_id': guild_id},
                {'$set': {'starboard_channel_id': channel.id}},
                upsert=True
            )
            if guild_id not in self.settings_cache:
                self.settings_cache[guild_id] = {}
            self.settings_cache[guild_id]['channel_id'] = channel.id
            await ctx.send(f"Starboard channel has been set to {channel.mention}.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting the channel: {e}")

    @starboard.command(name='starlimit')
    @commands.has_permissions(manage_guild=True)
    async def set_starlimit(self, ctx: commands.Context, limit: int):
        if limit < 1:
            await ctx.send("The star limit cannot be less than 1.")
            return

        guild_id = ctx.guild.id
        try:
            await self.settings_collection.update_one(
                {'_id': guild_id},
                {'$set': {'star_limit': limit}},
                upsert=True
            )
            if guild_id not in self.settings_cache:
                self.settings_cache[guild_id] = {}
            self.settings_cache[guild_id]['limit'] = limit
            await ctx.send(f"Star limit has been set to **{limit}**.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting the limit: {e}")

    @starboard.command(name='remove')
    @commands.has_permissions(manage_guild=True)
    async def remove_starboard(self, ctx: commands.Context):
        guild_id = ctx.guild.id
        if guild_id not in self.settings_cache:
            await ctx.send("Starboard is not configured on this server.")
            return

        try:
            await self.settings_collection.delete_one({'_id': guild_id})
            del self.settings_cache[guild_id]
            await ctx.send("Starboard has been disabled for this server.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != STAR_EMOJI or not payload.guild_id:
            return
        await self.handle_star_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != STAR_EMOJI or not payload.guild_id:
            return
        await self.handle_star_reaction(payload)

    async def handle_star_reaction(self, payload: discord.RawReactionActionEvent):
        settings = self.settings_cache.get(payload.guild_id)
        if not settings or not settings.get('channel_id'):
            return
        try:
            channel = self.bot.get_channel(payload.channel_id)
            if not channel or isinstance(channel, discord.ForumChannel): return
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        if message.author.id == payload.user_id or message.author.bot:
            return
        starboard_channel = self.bot.get_channel(settings['channel_id'])
        if not starboard_channel:
            return

        star_count = 0
        for reaction in message.reactions:
            if str(reaction.emoji) == STAR_EMOJI:
                star_count = reaction.count
                break
        star_limit = settings.get('limit', DEFAULT_STAR_LIMIT)

        starboard_post_doc = await self.posts_collection.find_one({'_id': message.id})
        if star_count >= star_limit:
            if starboard_post_doc:
                try:
                    starboard_message = await starboard_channel.fetch_message(starboard_post_doc['starboard_message_id'])
                    content = f"{STAR_EMOJI} **{star_count}** | {channel.mention}"
                    await starboard_message.edit(content=content)
                except discord.NotFound:
                    await self.posts_collection.delete_one({'_id': message.id})
                except discord.Forbidden:
                    pass
            else:
                embed = self.create_starboard_embed(message)
                content = f"{STAR_EMOJI} **{star_count}** | {channel.mention}"

                view = View()
                view.add_item(Button(style=discord.ButtonStyle.link, label="Jump to Message", url=message.jump_url))

                try:
                    starboard_message = await starboard_channel.send(content=content, embed=embed, view=view)
                    await self.posts_collection.insert_one({
                        '_id': message.id,
                        'starboard_message_id': starboard_message.id,
                        'guild_id': payload.guild_id
                    })
                except discord.Forbidden:
                    pass

        elif starboard_post_doc:
            try:
                starboard_message = await starboard_channel.fetch_message(starboard_post_doc['starboard_message_id'])
                await starboard_message.delete()
            except (discord.NotFound, discord.Forbidden):
                pass
            finally:
                await self.posts_collection.delete_one({'_id': message.id})

    def create_starboard_embed(self, message: discord.Message) -> discord.Embed:
        embed = discord.Embed(
            color=0x977FD7,
            description=message.content,
            timestamp=message.created_at
        )
        embed.set_author(name=f"{message.author.display_name} ({message.author.name})", icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"ID: {message.id}")
        image_set = False
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/') and not image_set:
                embed.set_image(url=attachment.url)
                image_set = True
            elif attachment.content_type.startswith('video/'):
                embed.add_field(name="Video Attachment", value=f"[Click to Watch]({attachment.url})", inline=False)

        return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(Starboard(bot))
