import discord
from gtts import gTTS, gTTSError
from discord.ext import commands
from utils.Tools import *
import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_path = "tts/tts-audio.mp3"

        os.makedirs("tts", exist_ok=True)

    async def disconnect_vc(self, vc):
        if vc and vc.is_connected():
            try:
                await vc.disconnect()
            except Exception as e:
                logger.error("Error disconnecting voice client: %s", e)

    @commands.command()
    @blacklist_check()
    @ignore_check()
    @premium_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tts(self, ctx, *args):
        text = " ".join(args)
        if not text:
            await ctx.send("Please provide some text for TTS.")
            return

        user = ctx.author
        if not user.voice or not user.voice.channel:
            await ctx.send("You need to be in a voice channel to run this command!")
            return

        vc = ctx.voice_client
        try:
            if vc is None:
                vc = await user.voice.channel.connect()
            elif vc.channel != user.voice.channel:
                await vc.move_to(user.voice.channel)

            if vc.is_playing():
                vc.stop()

            try:
                tts_audio = gTTS(text=text, lang="en-IN", slow=False)
                tts_audio.save(self.audio_path)
            except gTTSError as e:
                logger.error("TTS generation error: %s", e)
                await ctx.send("There was an error generating the TTS audio.")
                return

            try:
                source = await discord.FFmpegOpusAudio.from_probe(self.audio_path, method="fallback")
            except Exception as e:
                logger.error("Error creating audio source: %s", e)
                await ctx.send("There was an error processing the audio file.")
                return

            def after_playback(error):
                if error:
                    logger.error("Error during playback: %s", error)
                fut = asyncio.run_coroutine_threadsafe(self.disconnect_vc(vc), self.bot.loop)
                try:
                    fut.result()
                except Exception as e:
                    logger.error("Error in disconnect callback: %s", e)

            vc.play(source, after=after_playback)
            await ctx.send("Playing TTS audio...")

            timeout = 120
            total_wait = 0
            while vc.is_playing() and total_wait < timeout:
                await asyncio.sleep(1)
                total_wait += 1

            if vc.is_connected():
                await self.disconnect_vc(vc)

        except Exception as e:
            logger.error("Unexpected error in TTS command: %s", e)
            await ctx.send("An unexpected error occurred.")
        finally:
            if os.path.exists(self.audio_path):
                try:
                    os.remove(self.audio_path)
                except Exception as e:
                    logger.error("Error removing audio file: %s", e)

def setup(bot):
    bot.add_cog(TTS(bot))
