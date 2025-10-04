# music.py
import discord
from discord.ext import commands
import wavelink
import logging
from typing import Optional, cast, List, Dict, Any, Tuple
import random
import asyncio
from functools import wraps
import aiofiles
import json
import io
from datetime import datetime

# --- Basic Setup ---
logger = logging.getLogger(__name__)

# --- Music Data Manager (async JSON storage: musicdata.json) ---


class MusicDataManager:
    """
    Async manager for musicdata.json.
    Schema (in-memory): { "<user_id>": [ { "title":..., "uri":..., "author":..., "liked_at":... }, ... ] }
    """

    def __init__(self, path: str = "musicdata.json"):
        self.path = path
        self._lock = asyncio.Lock()
        self._data: Dict[str, List[Dict[str, Any]]] = {}

    async def load(self) -> None:
        """Load JSON file into memory; create file if missing."""
        async with self._lock:
            try:
                async with aiofiles.open(self.path, "r", encoding="utf-8") as f:
                    text = await f.read()
                    if not text:
                        self._data = {}
                    else:
                        self._data = json.loads(text)
            except FileNotFoundError:
                # create empty file
                self._data = {}
                await self.save()
            except json.JSONDecodeError:
                # corrupted file -> back up and reset
                logger.exception("musicdata.json is corrupted; resetting.")
                self._data = {}
                await self.save()

    async def save(self) -> None:
        """Persist in-memory data to disk safely (async)."""
        async with self._lock:
            tmp = json.dumps(self._data, indent=2, ensure_ascii=False)
            async with aiofiles.open(self.path, "w", encoding="utf-8") as f:
                await f.write(tmp)

    async def get_likes(self, user_id: int) -> List[Dict[str, Any]]:
        return list(self._data.get(str(user_id), []))

    async def add_like(self, user_id: int, track_info: Dict[str, Any]) -> bool:
        """
        Add a like for a user.
        Returns True if added, False if it already existed.
        Comparison by 'uri' primarily.
        """
        uid = str(user_id)
        uri = track_info.get("uri")
        if not uri:
            return False
        async with self._lock:
            user_list = self._data.setdefault(uid, [])
            exists = any(item.get("uri") == uri for item in user_list)
            if exists:
                return False
            # Add timestamp if not provided
            if "liked_at" not in track_info:
                track_info["liked_at"] = datetime.utcnow().isoformat()
            user_list.append(track_info)
            # persist
            await self.save()
            return True

    async def remove_like_by_uri(self, user_id: int, uri: str) -> bool:
        uid = str(user_id)
        async with self._lock:
            user_list = self._data.get(uid, [])
            new_list = [t for t in user_list if t.get("uri") != uri]
            if len(new_list) == len(user_list):
                return False
            self._data[uid] = new_list
            await self.save()
            return True

    async def remove_like_by_index(self, user_id: int, index: int) -> Optional[Dict[str, Any]]:
        """1-based index"""
        uid = str(user_id)
        async with self._lock:
            user_list = self._data.get(uid, [])
            if index < 1 or index > len(user_list):
                return None
            item = user_list.pop(index - 1)
            self._data[uid] = user_list
            await self.save()
            return item

    async def clear_likes(self, user_id: int) -> int:
        uid = str(user_id)
        async with self._lock:
            count = len(self._data.get(uid, []))
            self._data[uid] = []
            await self.save()
            return count

    async def export_likes_bytes(self, user_id: int) -> bytes:
        """Return bytes of the user's likes as a pretty JSON."""
        likes = await self.get_likes(user_id)
        content = json.dumps(likes, indent=2, ensure_ascii=False)
        return content.encode("utf-8")

    async def import_likes_list(self, user_id: int, likes_list: List[Dict[str, Any]], merge: bool = True) -> Tuple[int, int]:
        """
        Import a list of likes (list-of-dict). If merge True, add new unique entries.
        Returns (added_count, total_after_import).
        """
        uid = str(user_id)
        async with self._lock:
            user_list = self._data.setdefault(uid, [])
            existing_uris = {t.get("uri") for t in user_list}
            added = 0
            for item in likes_list:
                uri = item.get("uri")
                if not uri:
                    continue
                if uri in existing_uris:
                    continue
                if "liked_at" not in item:
                    item["liked_at"] = datetime.utcnow().isoformat()
                user_list.append(item)
                existing_uris.add(uri)
                added += 1
            self._data[uid] = user_list
            await self.save()
            return added, len(user_list)

    async def get_top_liked_songs(self, guild: discord.Guild, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Count likes in the guild only (counts only members present in guild).
        Returns list of (uri, count) sorted desc.
        """
        # build set of member ids (strings)
        member_ids = {str(m.id) for m in guild.members}
        counts: Dict[str, int] = {}
        async with self._lock:
            for uid, likes in self._data.items():
                if uid not in member_ids:
                    continue
                for t in likes:
                    uri = t.get("uri")
                    if not uri:
                        continue
                    counts[uri] = counts.get(uri, 0) + 1
        # convert to sorted list by count desc
        sorted_list = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_list[:top_n]


# --- Custom Player & Views ---


class LavalinkPlayer(wavelink.Player):
    """Custom Wavelink Player with a queue, state management, and history."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = wavelink.Queue()
        self.text_channel: Optional[discord.TextChannel] = None
        self.loop_mode = False
        self.autoplay_mode = False
        self.original_track: Optional[wavelink.Playable] = None
        self.last_played_tracks: list[wavelink.Playable] = []
        self.now_playing_message: Optional[discord.Message] = None
        self.max_history = 10

    def add_to_history(self, track: wavelink.Playable):
        """Adds a track to the playback history."""
        self.last_played_tracks.append(track)
        if len(self.last_played_tracks) > self.max_history:
            self.last_played_tracks.pop(0)

    async def clear_state_and_disconnect(self):
        """Resets all player states and disconnects safely."""
        self.loop_mode = False
        self.autoplay_mode = False
        self.original_track = None
        self.last_played_tracks.clear()
        self.queue.clear()

        if self.now_playing_message:
            try:
                await self.now_playing_message.edit(content="Playback has ended.", embed=None, view=None)
            except discord.HTTPException:
                pass
            self.now_playing_message = None

        await self.disconnect()


class MusicControlView(discord.ui.View):
    """A view with buttons to control the music player."""

    def __init__(self, player: LavalinkPlayer, music_cog: "Music"):
        super().__init__(timeout=None)
        self.player = player
        self.music_cog = music_cog
        # set button style for loop (attribute exists because discord.ui creates instances)
        try:
            self.loop_button.style = discord.ButtonStyle.success if self.player.loop_mode else discord.ButtonStyle.secondary
        except Exception:
            # defensive: just ignore if attribute not ready
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Allow the 'like' button even if the user is not in the same voice channel.
        For other controls, require same voice channel.
        """
        # custom_id value will be set explicitly on the like button
        cid = None
        try:
            cid = interaction.data.get("custom_id")
        except Exception:
            cid = None

        if cid == "music_like_button":
            return True  # allow liking regardless of voice channel membership

        # otherwise, enforce same voice channel
        if not interaction.user.voice or interaction.user.voice.channel != self.player.channel:
            await interaction.response.send_message("❌ You must be in the same voice channel as the bot.", ephemeral=True)
            return False
        return True

    # Primary controls
    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.secondary, row=1)
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.playing:
            return await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

        if self.player.paused:
            await self.player.pause(False)
            button.emoji = "⏸️"
        else:
            await self.player.pause(True)
            button.emoji = "▶️"

        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, row=1)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.player.playing:
            return await interaction.response.send_message("❌ Nothing is playing to skip.", ephemeral=True)

        await self.player.skip(force=True)
        await interaction.response.send_message("⏭️ Skipped the song.", ephemeral=True)

    @discord.ui.button(emoji="🔄", style=discord.ButtonStyle.secondary, row=1)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.loop_mode = not self.player.loop_mode
        if self.player.loop_mode:
            button.style = discord.ButtonStyle.success
            await interaction.response.send_message("🔁 Loop enabled for the current track.", ephemeral=True)
        else:
            button.style = discord.ButtonStyle.secondary
            await interaction.response.send_message("🔁 Loop disabled.", ephemeral=True)

        # edit the embed view to update style
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=1)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.player.clear_state_and_disconnect()
        await interaction.response.send_message("⏹️ Playback stopped and disconnected.", ephemeral=True)

    # Like button (toggle). set explicit custom_id so interaction_check can detect it
    @discord.ui.button(emoji="❤️", style=discord.ButtonStyle.secondary, row=0, custom_id="music_like_button")
    async def like_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Toggle like/unlike for the invoking user for the current track.
        - Works regardless of voice channel.
        - Uses MusicDataManager via music_cog.data_manager.
        """
        # simple per-user cooldown to avoid spam (1.5s)
        now = asyncio.get_event_loop().time()
        last = getattr(self.music_cog, "_like_cooldowns", {}).get(interaction.user.id, 0)
        if now - last < 1.5:
            return await interaction.response.send_message("⏳ You're liking too fast — try again shortly.", ephemeral=True)
        # update cooldown
        self.music_cog._like_cooldowns[interaction.user.id] = now

        track = getattr(self.player, "current", None)
        if not track:
            return await interaction.response.send_message("❌ No song is currently playing to like.", ephemeral=True)

        # skip streams
        if getattr(track, "is_stream", False):
            return await interaction.response.send_message("⚠️ Live streams cannot be saved as liked songs.", ephemeral=True)

        track_info = {
            "title": getattr(track, "title", "<unknown>"),
            "uri": getattr(track, "uri", None),
            "author": getattr(track, "author", None),
            "liked_at": datetime.utcnow().isoformat(),
        }
        if not track_info["uri"]:
            return await interaction.response.send_message("⚠️ This track lacks a valid uri and cannot be saved.", ephemeral=True)

        added = await self.music_cog.data_manager.add_like(interaction.user.id, track_info)
        if added:
            await interaction.response.send_message(f"✅ Added **{track_info['title']}** to your liked songs.", ephemeral=True)
        else:
            # already exists -> remove (toggle)
            removed = await self.music_cog.data_manager.remove_like_by_uri(interaction.user.id, track_info["uri"])
            if removed:
                await interaction.response.send_message(f"💔 Removed **{track_info['title']}** from your liked songs.", ephemeral=True)
            else:
                # unexpected: show already present message
                await interaction.response.send_message(f"ℹ️ **{track_info['title']}** is already in your liked songs.", ephemeral=True)


# --- Decorators for Command Checks ---


def voice_connected():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            if not ctx.author.voice or not ctx.author.voice.channel:
                await ctx.send("❌ You must be in a voice channel to use this command.")
                return
            await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def player_check():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            player = cast(LavalinkPlayer, ctx.voice_client)
            if not player:
                await ctx.send("❌ The bot is not connected to a voice channel.")
                return
            if ctx.author.voice.channel != player.channel:
                await ctx.send("❌ You must be in the same voice channel as the bot.")
                return
            await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


# --- Main Music Cog ---


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.setup_hook = self.setup_hook
        # initialize data manager and cooldown mapping
        self.data_manager = MusicDataManager("musicdata.json")
        self._like_cooldowns: Dict[int, float] = {}  # user_id -> last_like_time

    async def setup_hook(self) -> None:
        nodes = [wavelink.Node(identifier='Serenetia-V4', uri='https://lavalinkv4.serenetia.com:443', password='https://dsc.gg/ajidevserver')]
        await wavelink.Pool.connect(client=self.bot, nodes=nodes)
        # load or create musicdata.json
        await self.data_manager.load()

    # --- Event Listeners ---
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        logger.info(f"Lavalink Node '{payload.node.identifier}' is ready.")

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload: wavelink.TrackExceptionEventPayload):
        player = payload.player
        logger.error(f"Playback error in guild {player.guild_id}: {payload.exception}")
        if player.text_channel:
            await player.text_channel.send(f"❌ An error occurred while playing **{payload.track.title}**. It has been skipped.")
        await player.skip(force=True)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = cast(LavalinkPlayer, payload.player)
        if not player:
            return

        if player.now_playing_message:
            try:
                await player.now_playing_message.delete()
            except discord.HTTPException:
                pass
            player.now_playing_message = None

        if payload.track:
            player.add_to_history(payload.track)

        # Loop handling
        if player.loop_mode and player.original_track:
            return await self.start_playback(player, player.original_track)

        # Next in queue
        if not player.queue.is_empty:
            return await self.start_playback(player, player.queue.get())

        # Autoplay: try similar, then user's likes, then guild/global likes
        if player.autoplay_mode:
            similar_track = await self.find_similar_track(player)
            if similar_track:
                similar_track.requester = self.bot.user
                return await self.start_playback(player, similar_track)

            # try to pick from last requester if possible
            if payload.track and hasattr(payload.track, "requester"):
                last_req = getattr(payload.track, "requester", None)
                # If requester is a discord Member or User with id
                try:
                    last_req_id = getattr(last_req, "id", None) or (int(last_req) if isinstance(last_req, (str, int)) else None)
                except Exception:
                    last_req_id = None
                if last_req_id:
                    likes = await self.data_manager.get_likes(int(last_req_id))
                    if likes:
                        item = random.choice(likes)
                        try:
                            tracks = await wavelink.Playable.search(item["uri"])
                            if tracks:
                                tracks[0].requester = self.bot.user
                                return await self.start_playback(player, tracks[0])
                        except Exception:
                            pass

            # fallback: pick from guild toplikes
            try:
                guild_obj = player.guild
                top = await self.data_manager.get_top_liked_songs(guild_obj, top_n=10)
                if top:
                    # top is list of (uri, count)
                    uri_choice = random.choice(top)[0]
                    # pick a user's likes that contains this uri
                    # scan in-memory for a user who liked this uri and is in guild
                    async with self.data_manager._lock:
                        for uid, likes in self.data_manager._data.items():
                            if any(t.get("uri") == uri_choice for t in likes):
                                likes_for_user = likes
                                selected = next((t for t in likes_for_user if t.get("uri") == uri_choice), None)
                                if selected:
                                    try:
                                        tracks = await wavelink.Playable.search(selected["uri"])
                                        if tracks:
                                            tracks[0].requester = self.bot.user
                                            return await self.start_playback(player, tracks[0])
                                    except Exception:
                                        continue
            except Exception:
                pass

        await self.start_inactivity_check(player)

    async def start_inactivity_check(self, player: LavalinkPlayer):
        await asyncio.sleep(60)
        if player and not player.playing and player.is_connected():
            if player.text_channel:
                await player.text_channel.send("👋 Disconnecting due to inactivity.")
            await player.clear_state_and_disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.id == self.bot.user.id and before.channel and not after.channel:
            player = cast(LavalinkPlayer, before.channel.guild.voice_client)
            if player:
                await player.clear_state_and_disconnect()

        if before.channel and len(before.channel.members) == 1 and before.channel.members[0] == self.bot.user:
            player = cast(LavalinkPlayer, before.channel.guild.voice_client)
            if player:
                await asyncio.sleep(60)
                if player.is_connected() and len(player.channel.members) == 1:
                    if player.text_channel:
                        await player.text_channel.send("👋 Disconnecting as I was left alone.")
                    await player.clear_state_and_disconnect()

    # --- Helper Methods ---
    async def start_playback(self, player: LavalinkPlayer, track: wavelink.Playable):
        await player.play(track)
        if player.loop_mode:
            player.original_track = track
        if player.text_channel:
            await self.send_now_playing_embed(player, track)

    async def send_now_playing_embed(self, player: LavalinkPlayer, track: wavelink.Playable):
        """Creates and sends the 'Now Playing' controller to match the image."""
        embed = discord.Embed(title="Now Playing..", color=0x977FD7)

        duration = "🔴 Live" if track.is_stream else self.format_duration(track.length)
        requester = "Autoplay" if track.requester == self.bot.user else (track.requester.mention if hasattr(track.requester, "mention") else str(track.requester))

        description = (
            f"🔹 **Song:** [{track.title}]({track.uri})\n"
            f"🔹 **Author:** {track.author}\n"
            f"🔹 **Duration:** `{duration}`\n"
            f"🔹 **Requester:** {requester}"
        )
        embed.description = description

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        view = MusicControlView(player, self)
        player.now_playing_message = await player.text_channel.send(embed=embed, view=view)

    def format_duration(self, milliseconds: int) -> str:
        minutes, seconds = divmod(int(milliseconds / 1000), 60)
        return f"{minutes:02}:{seconds:02}"

    # --- Commands ---
    @commands.command(name='play', aliases=['p'])
    @voice_connected()
    async def play(self, ctx: commands.Context, *, query: str):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=LavalinkPlayer)
            except Exception:
                return await ctx.send("❌ Could not connect to the voice channel.")

        player.text_channel = ctx.channel

        tracks = await wavelink.Playable.search(query)
        if not tracks:
            return await ctx.reply(embed=discord.Embed(description=f"❌ No results found for: `{query}`", color=0xFF0000))

        added_embed = discord.Embed(color=0x00FF00)
        if isinstance(tracks, wavelink.Playlist):
            for track in tracks.tracks:
                track.requester = ctx.author
            player.queue.extend(tracks.tracks)
            added_embed.description = f"✅ Added **{len(tracks.tracks)}** tracks from playlist **{tracks.name}**."
        else:
            track = tracks[0]
            track.requester = ctx.author
            await player.queue.put_wait(track)
            added_embed.description = f"✅ Added to queue **{track.title}**"

        await ctx.reply(embed=added_embed, mention_author=False)

        if not player.playing:
            await self.start_playback(player, player.queue.get())

    @commands.command(name='stop', aliases=['dc'])
    @player_check()
    async def stop(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        await player.clear_state_and_disconnect()
        await ctx.send("⏹️ Playback stopped and disconnected.")

    @commands.command(name='skip')
    @player_check()
    async def skip(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if not player.playing:
            return await ctx.send("❌ Nothing is playing to skip.")
        await ctx.send(f"⏭️ Skipped **{player.current.title}**.")
        await player.skip(force=True)

    @commands.command(name='pause')
    @player_check()
    async def pause(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if not player.playing:
            return await ctx.send("❌ Nothing is playing.")
        if player.paused:
            return await ctx.send("Playback is already paused.")
        await player.pause(True)
        await ctx.send("⏸️ Playback paused.")

    @commands.command(name='resume')
    @player_check()
    async def resume(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if not player.paused:
            return await ctx.send("❌ Playback is not paused.")
        await player.pause(False)
        await ctx.send("▶️ Playback resumed.")

    @commands.command(name='queue', aliases=['q'])
    @player_check()
    async def queue(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if player.queue.is_empty and not player.current:
            return await ctx.send("❌ The queue is empty.")
        embed = discord.Embed(title="📜 Song Queue", color=0x977FD7)
        if player.current:
            embed.add_field(name="Now Playing", value=f"**[{player.current.title}]({player.current.uri})**", inline=False)
        if not player.queue.is_empty:
            queue_text = "\n".join(f"`{i+1}.` {t.title}" for i, t in enumerate(list(player.queue)[:10]))
            embed.add_field(name="Up Next", value=queue_text, inline=False)
            if len(player.queue) > 10:
                embed.set_footer(text=f"...and {len(player.queue) - 10} more.")
        await ctx.send(embed=embed)

    @commands.command(name='nowplaying', aliases=['nowp'])
    @player_check()
    async def nowplaying(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if not player.current:
            return await ctx.send("❌ Nothing is currently playing.")
        if player.now_playing_message:
            try:
                await player.now_playing_message.delete()
            except discord.HTTPException:
                pass
        await self.send_now_playing_embed(player, player.current)

    @commands.command(name='qclear')
    @player_check()
    async def clear(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if player.queue.is_empty:
            return await ctx.send("❌ The queue is already empty.")
        player.queue.clear()
        await ctx.send("🗑️ The queue has been cleared.")

    @commands.command(name='qremove')
    @player_check()
    async def remove(self, ctx: commands.Context, index: int):
        player = cast(LavalinkPlayer, ctx.voice_client)
        if index < 1 or index > len(player.queue):
            return await ctx.send("❌ Invalid track number.")

        track_to_remove = player.queue[index - 1]
        del player.queue[index - 1]
        await ctx.send(f"🗑️ Removed **{track_to_remove.title}** from the queue.")

    @commands.command(name='volume', aliases=['v'])
    @player_check()
    async def volume(self, ctx: commands.Context, value: int):
        if not 0 <= value <= 100:
            return await ctx.send("❌ Volume must be between 0 and 100.")
        player = cast(LavalinkPlayer, ctx.voice_client)
        await player.set_volume(value)
        await ctx.send(f"🔊 Volume set to {value}%.")

    @commands.command(name='autoplay', aliases=['ap'])
    @player_check()
    async def autoplay(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        player.autoplay_mode = not player.autoplay_mode
        status = "enabled" if player.autoplay_mode else "disabled"
        await ctx.send(f"🔄 Autoplay is now **{status}**.")

    @commands.command(name='loop')
    @player_check()
    async def loop(self, ctx: commands.Context):
        player = cast(LavalinkPlayer, ctx.voice_client)
        player.loop_mode = not player.loop_mode
        if player.loop_mode:
            player.original_track = player.current
            await ctx.send("🔁 Loop is now **enabled** for the current track.")
        else:
            player.original_track = None
            await ctx.send("🔁 Loop is now **disabled**.")

    async def find_similar_track(self, player: LavalinkPlayer) -> Optional[wavelink.Playable]:
        if not player.last_played_tracks:
            tracks = await wavelink.Playable.search("new popular music")
            return tracks[0] if tracks else None

        last_track = player.last_played_tracks[-1]
        query = f"music similar to {last_track.author} - {last_track.title}"
        tracks = await wavelink.Playable.search(query)
        return tracks[0] if tracks else None

    # ----------------------
    # Liked songs interface
    # ----------------------

    @commands.command(name='likedsongs', aliases=['likes', 'mylikes'])
    async def likedsongs(self, ctx: commands.Context, page: int = 1):
        """Show paginated list of the invoking user's liked songs."""
        likes = await self.data_manager.get_likes(ctx.author.id)
        if not likes:
            return await ctx.send("ℹ️ You have no liked songs yet. Use the ❤️ button while a track is playing to add one.")

        per = 10
        page = max(1, page)
        start = (page - 1) * per
        chunk = likes[start:start + per]
        description = "\n".join(f"`{i+1+start}.` [{it['title']}]({it['uri']}) — {it.get('author', 'Unknown')}" for i, it in enumerate(chunk))
        embed = discord.Embed(title=f"❤️ Your Liked Songs", description=description or "No songs on this page.", color=0x977FD7)
        if len(likes) > per:
            embed.set_footer(text=f"Page {page}/{(len(likes) + per - 1) // per}")
        await ctx.send(embed=embed)

    @commands.command(name='playlikedsong', aliases=['playlikes', 'likedsong'])
    @voice_connected()
    async def play_liked_songs(self, ctx: commands.Context, mode: Optional[str] = None):
        """
        Play your liked songs. mode='shuffle' to randomize.
        """
        likes = await self.data_manager.get_likes(ctx.author.id)
        if not likes:
            return await ctx.send("ℹ️ You have no liked songs yet. Use the ❤️ button while a track is playing to add one.")

        # resolve each like by uri
        playables: List[wavelink.Playable] = []
        for item in likes:
            uri = item.get("uri")
            if not uri:
                continue
            try:
                tracks = await wavelink.Playable.search(uri)
            except Exception:
                tracks = None
            if not tracks:
                # fallback: try search by title+author
                qry = f"{item.get('title', '')} {item.get('author', '')}"
                try:
                    tracks = await wavelink.Playable.search(qry)
                except Exception:
                    tracks = None
            if tracks:
                tr = tracks[0]
                tr.requester = ctx.author
                playables.append(tr)

        if not playables:
            return await ctx.send("❌ Couldn't resolve any of your liked songs to playable tracks.")

        if mode and mode.lower() in ("shuffle", "random"):
            random.shuffle(playables)

        player = cast(LavalinkPlayer, ctx.voice_client)
        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=LavalinkPlayer)
            except Exception:
                return await ctx.send("❌ Could not connect to the voice channel.")
        player.text_channel = ctx.channel

        for tr in playables:
            await player.queue.put_wait(tr)

        await ctx.send(f"✅ Queued {len(playables)} liked songs{' (shuffled)' if mode and mode.lower() in ('shuffle','random') else ''}.")

        if not player.playing:
            await self.start_playback(player, player.queue.get())

    @commands.command(name='unlike')
    async def unlike(self, ctx: commands.Context, *, query: str):
        """
        Remove a liked song by index (1-based from likedsongs) or by partial title/uri.
        Usage:
        - !unlike 3
        - !unlike Never Gonna Give You Up
        """
        likes = await self.data_manager.get_likes(ctx.author.id)
        if not likes:
            return await ctx.send("ℹ️ You have no liked songs to remove.")

        # try index
        idx = None
        try:
            idx = int(query)
        except Exception:
            idx = None

        if idx is not None:
            removed = await self.data_manager.remove_like_by_index(ctx.author.id, idx)
            if removed:
                return await ctx.send(f"🗑️ Removed **{removed.get('title', 'Unknown')}** from your likes.")
            else:
                return await ctx.send("❌ Invalid index.")

        # else by partial match on title or uri
        qlow = query.lower()
        matches = [t for t in likes if qlow in (t.get("title", "").lower() + " " + (t.get("author", "") or "").lower() + " " + (t.get("uri", "") or "").lower())]
        if not matches:
            return await ctx.send("❌ Could not find a liked song matching that query.")

        # if multiple matches, remove the first
        target = matches[0]
        removed = await self.data_manager.remove_like_by_uri(ctx.author.id, target.get("uri"))
        if removed:
            return await ctx.send(f"🗑️ Removed **{target.get('title', 'Unknown')}** from your likes.")
        else:
            return await ctx.send("❌ Failed to remove that liked song.")

    @commands.command(name='clearlikes')
    async def clearlikes(self, ctx: commands.Context, confirm: Optional[str] = None):
        """
        Clear all liked songs. Usage: !clearlikes confirm
        """
        if confirm != "confirm":
            return await ctx.send("⚠️ This will remove ALL your liked songs. To confirm, run: `!clearlikes confirm`")
        count = await self.data_manager.clear_likes(ctx.author.id)
        await ctx.send(f"🗑️ Cleared {count} liked songs from your account.")

    @commands.command(name='exportlikes')
    async def exportlikes(self, ctx: commands.Context):
        """
        Export your liked songs as a JSON file (sent via DM).
        """
        likes = await self.data_manager.get_likes(ctx.author.id)
        if not likes:
            return await ctx.send("ℹ️ You have no liked songs to export.")
        data_bytes = await self.data_manager.export_likes_bytes(ctx.author.id)
        filename = f"liked_songs_{ctx.author.id}.json"
        buffer = io.BytesIO(data_bytes)
        buffer.seek(0)
        try:
            await ctx.author.send(embed=discord.Embed(description="📤 Here is your liked songs export.", color=0x00FF00), file=discord.File(fp=buffer, filename=filename))
            await ctx.send("✅ I have sent your liked songs via DM.")
        except discord.Forbidden:
            await ctx.send("❌ I couldn't DM you. Please enable DMs from this server or use `!exportlikes` in a place where I can DM you.")

    @commands.command(name='importlikes')
    async def importlikes(self, ctx: commands.Context):
        """
        Import liked songs by attaching a JSON file (format exported by exportlikes).
        Upload a JSON as an attachment to this command message.
        """
        if not ctx.message.attachments:
            return await ctx.send("⚠️ Attach a JSON file exported by `!exportlikes` to import.")
        att = ctx.message.attachments[0]
        try:
            raw = await att.read()
            parsed = json.loads(raw.decode("utf-8"))
            if not isinstance(parsed, list):
                return await ctx.send("❌ Invalid format. Expected a JSON array of liked song objects.")
            # basic validation
            valid_items = []
            for it in parsed:
                if isinstance(it, dict) and it.get("uri") and it.get("title"):
                    if "liked_at" not in it:
                        it["liked_at"] = datetime.utcnow().isoformat()
                    valid_items.append({"title": it["title"], "uri": it["uri"], "author": it.get("author"), "liked_at": it["liked_at"]})
            added, total = await self.data_manager.import_likes_list(ctx.author.id, valid_items, merge=True)
            await ctx.send(f"✅ Imported {added} new liked songs. You now have {total} liked songs.")
        except json.JSONDecodeError:
            await ctx.send("❌ That file didn't look like valid JSON.")
        except Exception:
            logger.exception("importlikes failed")
            await ctx.send("❌ Import failed due to an unexpected error.")

    @commands.command(name='toplikes')
    async def toplikes(self, ctx: commands.Context, top_n: int = 10):
        """
        Show top liked songs in this guild (counts of how many different members liked a given URI).
        """
        guild = ctx.guild
        if not guild:
            return await ctx.send("❌ This command must be used in a server.")
        top = await self.data_manager.get_top_liked_songs(guild, top_n=top_n)
        if not top:
            return await ctx.send("ℹ️ No likes in this guild yet.")
        desc_lines = []
        for i, (uri, count) in enumerate(top, start=1):
            # try to find title from any user that liked it (cheap scan)
            title = uri
            async with self.data_manager._lock:
                found = None
                for uid, likes in self.data_manager._data.items():
                    for t in likes:
                        if t.get("uri") == uri:
                            found = t.get("title") or uri
                            break
                    if found:
                        break
            desc_lines.append(f"`{i}.` [{found}]({uri}) — **{count}** likes")
        embed = discord.Embed(title="🔥 Top Liked Songs (Guild)", description="\n".join(desc_lines), color=0xFFD166)
        await ctx.send(embed=embed)


# Add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
