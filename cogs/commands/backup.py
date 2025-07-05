import discord
from discord.ext import commands, tasks
import zipfile
import os
import time
import asyncio

class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authorized_ids = [980763915749322773, 171410152690417664, 912934555776868372]
        self.user_ids = [912934555776868372, 978599431563784203]
        self.backup_task.start()

    def cog_unload(self):
        self.backup_task.cancel()

    async def create_backup(self):
        with zipfile.ZipFile('backup.zip', 'w') as zf:
            for folder in ['jsons', 'databases', 'giveaway_users', 'cogs', 'utils', 'core']:
                for dirname, subdirs, files in os.walk(folder):
                    zf.write(dirname)
                    for filename in files:
                        os.utime(os.path.join(dirname, filename), (time.time(), time.time()))
                        zf.write(os.path.join(dirname, filename))

    async def send_backup(self):
        for user_id in self.user_ids:
            try:
                user = await self.bot.fetch_user(user_id)
                if user:
                    with open('backup.zip', 'rb') as f:
                        await user.send(file=discord.File(f))
                    await asyncio.sleep(1)
            except discord.HTTPException as e:
                print(f"Failed to send backup to {user_id}: {e}")

        os.remove('backup.zip')

    @commands.command()
    async def manual_backup(self, ctx):
        if ctx.message.author.id in self.authorized_ids:
            await self.create_backup()
            await self.send_backup()
            await ctx.send("Manual backup completed and sent.")

    @tasks.loop(hours=12)
    async def backup_task(self):
        await self.create_backup()
        await self.send_backup()

    @backup_task.before_loop
    async def before_backup(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Backup(bot))
