import discord
from discord.ext import commands
 
import asyncio
import os
import logging
from utils.checks import global_check

# --- Setup logging ---
logger = logging.getLogger(__name__)

class Soundboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.audio_dir = "audio"
        # Ensure the directory for audio files exists
        os.makedirs(self.audio_dir, exist_ok=True)
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)

    # --- Metadata for the Help Command (from soundboard1.py) ---
    def help2_custom(self):
        """Provides metadata for the custom help command."""
        emoji = '<:audio:1089139281441861764>'
        label = "Soundboard"
        description = "Shows the soundboard commands."
        return emoji, label, description

    @commands.group(name="__Soundboard__")
    async def __Soundboard__(self, ctx: commands.Context):
        """`b virus`, `b cutekimochi`,`b kimochi`, `b gigachad`, `b sigma`, `b bosrike`, `b hmoan`, `b uaregey`, `b whyugey`, `b stepbro`, `b pstepbro`, `b omgunoob`, `b modibkl`, `b biharkid`, `b haatomc`, `b ninjahatori`, `b bengali`, `b marathi`, `b narutosad`, `b abdi`, `b ahshit`, `b airhorn`, `b araara`, `b bhau`, `b bruh`, `b cuteuwu`, `b disconnected`, `b game-over`, `b giggle`, `b ha-gay`, `b hellomf`, `b honk`, `b illuminati`, `b john-cena`, `b laugh`, `b magic`, `b margayamc`, `b moin-meister`, `b nani`, `b oioi`, `b oioioi`, `b onichan`, `b pew-pew`, `b ph-intro`, `b quack-quack`, `b rickroll`, `b samsung-notification`, `b sheesh`, `b sike`, `b skype`, `b siuuu`, `b superidol`, `b surprisemf`, `b sus`, `b uwu`, `b verpissdich`, `b wow`, `b iphone-notification`, `b gimme-ohyeah`, `b amogus`, `b nogodno`, `b dattebayo`, `b afewmomentslater`, `b ilikecutg`, `b oppai-dragon`"""
        pass
    # --- End of Help Command Metadata ---

    @commands.command(name="b", aliases=["sound"])
    
    
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.guild, wait=True)
    async def play_sound(self, ctx: commands.Context, *, sound_name: str):
        """Plays a short sound effect in your voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You must be in a voice channel to use the soundboard.", ephemeral=True)
            # Release the concurrency lock if the user is not in a voice channel
            self.play_sound.get_cooldown_mapping(ctx).get_bucket(ctx.message).reset()
            self.play_sound.get_max_concurrency(ctx.message).release(ctx.message)
            return

        # Sanitize input to prevent directory traversal attacks
        safe_sound_name = "".join(c for c in sound_name.lower() if c.isalnum() or c in ('-', '_'))
        audio_file = os.path.join(self.audio_dir, f"{safe_sound_name}.mp3")

        # Asynchronously check if the file exists
        def file_exists():
            return os.path.exists(audio_file)

        if not await self.bot.loop.run_in_executor(None, file_exists):
            await ctx.send(f'Sound "`{sound_name}`" not found.', ephemeral=True)
            self.play_sound.get_max_concurrency(ctx.message).release(ctx.message)
            return

        vc = ctx.voice_client

        try:
            # Connect or move to the user's voice channel
            if vc is None:
                vc = await ctx.author.voice.channel.connect(timeout=15.0)
            elif vc.channel != ctx.author.voice.channel:
                await vc.move_to(ctx.author.voice.channel)

        except discord.ClientException as e:
            logger.error(f"Error connecting/moving voice client: {e}")
            await ctx.send("There was an error connecting to the voice channel.")
            self.play_sound.get_max_concurrency(ctx.message).release(ctx.message)
            return
        except asyncio.TimeoutError:
            await ctx.send("Connecting to the voice channel timed out.")
            self.play_sound.get_max_concurrency(ctx.message).release(ctx.message)
            return

        # --- Playback with Robust After-Callback ---
        def after_playback(error):
            if error:
                logger.error(f"Error during soundboard playback: {error}")
            
            # Create a task to disconnect after a short delay if idle
            async def delayed_disconnect(voice_client):
                await asyncio.sleep(15) # 15-second idle timeout
                if voice_client and voice_client.is_connected() and not voice_client.is_playing():
                    await voice_client.disconnect()

            asyncio.run_coroutine_threadsafe(delayed_disconnect(vc), self.bot.loop)

        try:
            source = discord.FFmpegPCMAudio(audio_file)
            # Use PCMVolumeTransformer to control volume
            vc.play(discord.PCMVolumeTransformer(source, volume=0.25), after=after_playback)
            await ctx.message.add_reaction("🔊")

        except Exception as e:
            logger.error(f"Error playing sound file {audio_file}: {e}")
            await ctx.send("There was an error trying to play that sound.")
            if vc and vc.is_connected():
                await vc.disconnect()

async def setup(bot):
    await bot.add_cog(Soundboard(bot))
