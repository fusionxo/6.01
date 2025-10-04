import discord
import logging
from discord.ext import commands
import pymongo

import discord
import logging
from discord.ext import commands
import pymongo

class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x2f3136
        self.connection = pymongo.MongoClient("mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net/ready?retryWrites=true&w=majority")
        self.db = self.connection["ready"]["readydata"]

    @commands.Cog.listener()
    async def on_ready(self):
        for server in self.bot.guilds:
            data = self.db.find_one({"guild": server.id})
            if data == None:
                self.db.insert_one(
                    {
                        "guild": server.id,
                        "log-channel": None,
                        "delete-after" : None,
                        "joinvc": {
                            "channelid": None,
                            "enabled": False
                        },
                        "vcrole": {
                            "roleid": None,
                            "enabled": False
                        },
                        "autorole": [],
                        "humans": [],
                        "bots": [],
                        "welcome": {
                            "message": None,
                            "channel": None,
                            "enabled": False,
                            "embed": False,
                            "title": None,
                            "description": None,
                            "thumbnail": None,
                            "image": None
                        }
                    }
                )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.db.insert_one(
            {
                "guild": guild.id,
                "log-channel": None, 
                "delete-after" : None,
                "joinvc": {
                    "channelid": None,
                    "enabled": False
                },
                "vcrole": {
                    "roleid": None,
                    "enabled": False
                },
                "autorole": [],
                "humans": [],
                "bots": [],
                "welcome": {
                    "message": None,
                    "channel": None,
                    "enabled": False,
                    "embed": False,
                    "title": None,
                    "description": None,
                    "thumbnail": None,
                    "image": None
                }
            }
        )

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        logging.info("Shard #%s is ready" % (shard_id))

    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        logging.info("Shard #%s has connected" % (shard_id))

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        logging.info("Shard #%s has disconnected" % (shard_id))

    @commands.Cog.listener()
    async def on_shard_resume(self, shard_id):
        logging.info("Shard #%s has resumed" % (shard_id))

async def setup(bot):
    await bot.add_cog(Ready(bot))
