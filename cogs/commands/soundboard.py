import discord
from discord.ext import commands
import os
from utils.Tools import *
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class soundboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def disconnect_vc(self, vc):
        if vc and vc.is_connected():
            try:
                await vc.disconnect()
            except Exception as e:
                logger.error("Error disconnecting voice client: %s", e)

    @commands.command(name="b")
    @blacklist_check()
    @ignore_check()    
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, sound_name: str):
        vc = ctx.voice_client
        user = ctx.author

        if not user.voice or not user.voice.channel:
            await ctx.send("You need to be in a voice channel to run this command!")
            return

        try:
            if vc is None:
                vc = await user.voice.channel.connect()
            else:
                vc.stop()

            audio_file = f'audio/{sound_name}.mp3'

            if os.path.isfile(audio_file):
                FFMPEG_OPTIONS = {'options': '-vn'}
                source = discord.FFmpegPCMAudio(executable="ffmpeg", source=audio_file, **FFMPEG_OPTIONS)

                def after_playing(error):
                    if error:
                        logger.error("Error during playback: %s", error)
                    fut = asyncio.run_coroutine_threadsafe(self.disconnect_vc(vc), self.bot.loop)
                    try:
                        fut.result()
                    except Exception as e:
                        logger.error("Error in disconnect callback: %s", e)
                    asyncio.run_coroutine_threadsafe(ctx.message.add_reaction('\u2705'), self.bot.loop)

                source.after = after_playing

                vc.play(discord.PCMVolumeTransformer(source, volume=0.25))

                await ctx.send(f'Playing sound: {sound_name}')
            else:
                await ctx.send(f'Sound "{sound_name}" not found.')

        except Exception as e:
            logger.error("Unexpected error in play command: %s", e)
            await ctx.send("An unexpected error occurred.")

def setup(bot):
    bot.add_cog(soundboard(bot))
