import discord
from discord.ext import commands
from gtts import gTTS, gTTSError
import asyncio
import os
import logging
from utils.checks import global_check
from utils.Tools import premium_check

# --- Setup logging ---
logger = logging.getLogger(__name__)

class TTS(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tts_audio_dir = "tts_audio"
        # Ensure the directory for audio files exists
        os.makedirs(self.tts_audio_dir, exist_ok=True)
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)

    def help2_custom(self):
        """Provides metadata for the custom help command."""
        emoji = '<:sound:1087776618723950593>'
        label = "TTS"
        description = "Converts text to speech in a voice channel."
        return emoji, label, description
    
    @commands.group()
    async def __TTS__(self, ctx: commands.Context):
        """`tts <text>`"""

    async def cleanup(self, vc: discord.VoiceClient, audio_path: str):
        """A robust cleanup function to disconnect and delete the audio file."""
        if vc and vc.is_connected():
            await vc.disconnect()
        
        # Attempt to remove the audio file
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError as e:
                logger.error(f"Error removing audio file {audio_path}: {e}")

    @commands.command(name="tts")
    
    
    @premium_check()
    @commands.cooldown(1, 10, commands.BucketType.user) # 10-second cooldown
    @commands.max_concurrency(1, commands.BucketType.guild) # One TTS per guild at a time
    async def tts(self, ctx: commands.Context, *, text: str):
        """Converts text to speech and plays it in your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel to use this command.", ephemeral=True)
            return

        # Check for text length
        if len(text) > 500:
            await ctx.send("The text is too long (max 500 characters).", ephemeral=True)
            return

        vc = ctx.voice_client
        # Generate a unique path for this specific TTS request to avoid conflicts
        audio_path = os.path.join(self.tts_audio_dir, f"tts-audio-{ctx.message.id}.mp3")

        try:
            # Connect or move to the user's voice channel
            if vc is None:
                vc = await ctx.author.voice.channel.connect()
            elif vc.channel != ctx.author.voice.channel:
                await vc.move_to(ctx.author.voice.channel)

            if vc.is_playing():
                await ctx.send("I'm already playing something. Please wait.", ephemeral=True)
                return

            # --- Non-Blocking Audio Generation ---
            # This is a blocking function, so we run it in an executor
            def generate_audio():
                tts_audio = gTTS(text=text, lang="en-IN", slow=False)
                tts_audio.save(audio_path)

            # Send a thinking message to the user
            await ctx.message.add_reaction("⏳")
            
            # Run the blocking gTTS call in a separate thread
            await self.bot.loop.run_in_executor(None, generate_audio)

            # --- Playback with Robust Error Handling ---
            # Define the 'after' callback for cleanup
            def after_playback(error):
                if error:
                    logger.error(f"Error during playback: {error}")
                # Use asyncio.run_coroutine_threadsafe for thread-safe operations
                asyncio.run_coroutine_threadsafe(self.cleanup(vc, audio_path), self.bot.loop)

            # Create the audio source
            source = discord.FFmpegPCMAudio(audio_path)
            vc.play(source, after=after_playback)

            # Remove the thinking reaction and confirm playback
            await ctx.message.remove_reaction("⏳", self.bot.user)
            await ctx.message.add_reaction("🔊")

        except gTTSError as e:
            logger.error(f"gTTS API Error: {e}")
            await ctx.send("Sorry, there was an issue with the Text-to-Speech service. Please try again later.", ephemeral=True)
            await self.cleanup(vc, audio_path) # Cleanup on failure
        except discord.ClientException as e:
            logger.error(f"Discord Client Exception: {e}")
            await ctx.send("I'm having trouble connecting to the voice channel.", ephemeral=True)
            await self.cleanup(vc, audio_path) # Cleanup on failure
        except Exception as e:
            logger.error(f"An unexpected error occurred in TTS command: {e}")
            await ctx.send("An unexpected error occurred. The developers have been notified.", ephemeral=True)
            await self.cleanup(vc, audio_path) # Cleanup on failure

async def setup(bot):
    await bot.add_cog(TTS(bot))
