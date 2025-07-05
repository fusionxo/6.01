"""import discord
import wavelink
from discord.ext import commands

class ChordAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx: commands.Context) -> None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if not ctx.voice_client:
                await channel.connect(cls=wavelink.Player)
                await ctx.send(f'Connected to {channel.name}.')
            else:
                await ctx.send(f'Already connected to a voice channel.')
        else:
            await ctx.send('You are not connected to a voice channel.')

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        if not ctx.voice_client:
            await ctx.send('I am not connected to a voice channel.')
            return

        vc: wavelink.Player = ctx.voice_client
        tracks = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send(f'No tracks found with query: `{search}`')
            return

        track = tracks[0]
        await vc.play(track)
        await ctx.send(f'Now playing: {track.title}')

    @commands.command()
    async def skip(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('Skipped the current track.')
        else:
            await ctx.send('No track is currently playing.')

    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_playing():
            await ctx.voice_client.pause()
            await ctx.send('Paused the current track.')
        else:
            await ctx.send('No track is currently playing.')

    @commands.command()
    async def resume(self, ctx: commands.Context) -> None:
        if ctx.voice_client and ctx.voice_client.is_paused():
            await ctx.voice_client.resume()
            await ctx.send('Resumed the current track.')
        else:
            await ctx.send('No track is currently paused.')

    @commands.command()
    async def stop(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.stop()
            await ctx.send('Stopped playback and cleared the queue.')
        else:
            await ctx.send('I am not connected to a voice channel.')

    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int) -> None:
        if ctx.voice_client:
            if 0 <= volume <= 100:
                ctx.voice_client.volume = volume / 100
                await ctx.send(f'Set volume to {volume}%.')
            else:
                await ctx.send('Volume must be between 0 and 100.')
        else:
            await ctx.send('I am not connected to a voice channel.')

    @commands.command()
    async def loop(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            ctx.voice_client.loop = not ctx.voice_client.loop
            state = 'enabled' if ctx.voice_client.loop else 'disabled'
            await ctx.send(f'Looping is now {state}.')
        else:
            await ctx.send('I am not connected to a voice channel.')

    @commands.command()
    async def leave(self, ctx: commands.Context) -> None:
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Disconnected from the voice channel.')
        else:
            await ctx.send('I am not connected to a voice channel.')

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChordAI(bot))
"""