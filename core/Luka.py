from __future__ import annotations
from discord.ext import commands
import discord
import aiohttp
import json
import jishaku, time
import asyncio
import typing
from utils.config import OWNER_IDS, EXTENSIONS, No_Prefix
from utils import getConfig, updateConfig
from .Context import Context
import pymongo
from utils.checks import global_check 


# Replace the connection link, database, and collection names accordingly
MONGO_LINK = "mongodb+srv://hitman25:luka.123@cluster0.xlxhrlj.mongodb.net/"
DATABASE_NAME = "info"
COLLECTION_NAME = "infodata"

# Initialize the MongoDB client and database
mongo_client = pymongo.MongoClient(MONGO_LINK)
db = mongo_client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

 
class Luka(commands.AutoShardedBot):
    def __init__(self, *arg, **kwargs):
      self.topgg_headers = {"Authorization": "[REDACTED_TOKEN]"}
      intents = discord.Intents.all()
      super().__init__(command_prefix=self.get_prefix,
                         case_insensitive=True,
                         intents=intents,
                         strip_after_prefix=True,
                         owner_ids=OWNER_IDS,
                         allowed_mentions=discord.AllowedMentions(everyone=False, replied_user=False,roles=False),
                         shard_count=1)
      self.add_check(global_check)

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
                print(f"Loaded extension: {extension}")
            except Exception as e:
                print(f"Failed to load extension: {extension}")
                print(e)
        await self.tree.sync()

    async def on_ready(self):
        print("Connected as {}".format(self.user))

    async def on_connect(self):
      await self.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name=f'$help'))

    async def send_raw(self, channel_id: int, content: str,
                       **kwargs) -> typing.Optional[discord.Message]:
        await self.http.send_message(channel_id, content, **kwargs)

    async def invoke_help_command(self, ctx: Context) -> None:
        """Invoke the help command or default help command if help extensions is not loaded."""
        return await ctx.send_help(ctx.command)

    async def fetch_message_by_channel(
        self, channel: discord.TextChannel, messageID: int
    ) -> typing.Optional[discord.Message]:
        async for msg in channel.history(
            limit=1,
            before=discord.Object(messageID + 1),
            after=discord.Object(messageID - 1),
        ):
            return msg

    async def get_prefix(self, message: discord.Message):
        user_id = str(message.author.id)

        result = collection.find_one({"_id": "np", "users": user_id})
        if result:
            return commands.when_mentioned_or('$', '')(self, message)

        if message.guild:
            data = getConfig(message.guild.id)
            prefix = data["prefix"]
            return commands.when_mentioned_or(prefix)(self, message)
        
        return commands.when_mentioned_or('$')(self, message)
    

    async def on_message_edit(self, before, after):
        ctx: Context = await self.get_context(after, cls=Context)
        if before.content != after.content:
            if after.guild is None or after.author.bot:
                return
            if ctx.command is None:
                return
            if isinstance(ctx.channel, discord.Thread):
                return
            await self.invoke(ctx)
        else:
            return
