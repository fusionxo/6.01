import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import asyncio
import datetime
import random
import time
from typing import List, Optional

DB_PATH = "databases/giveaways.db"

class GiveawayManager:
    def __init__(self, bot):
        self.bot = bot
        self.db_path = DB_PATH
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaways (
                    message_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    host_id INTEGER NOT NULL,
                    prize TEXT NOT NULL,
                    end_timestamp REAL NOT NULL,
                    winner_count INTEGER NOT NULL,
                    is_ended INTEGER DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    message_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY (message_id, user_id)
                )
            """)
            await db.commit()

    async def add_participant(self, message_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("INSERT INTO participants (message_id, user_id) VALUES (?, ?)", (message_id, user_id))
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def remove_participant(self, message_id, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM participants WHERE message_id = ? AND user_id = ?", (message_id, user_id))
            await db.commit()
            return cursor.rowcount > 0

    async def get_participant_count(self, message_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM participants WHERE message_id = ?", (message_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0

    async def get_active_giveaways(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE is_ended = 0 AND end_timestamp <= ?", (time.time(),)) as cursor:
                return await cursor.fetchall()

    async def get_giveaway(self, message_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,)) as cursor:
                return await cursor.fetchone()

    async def get_participants(self, message_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id FROM participants WHERE message_id = ?", (message_id,)) as cursor:
                return [row[0] for row in await cursor.fetchall()]

    async def end_giveaway(self, message_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE giveaways SET is_ended = 1 WHERE message_id = ?", (message_id,))
            await db.commit()

    async def get_ended_giveaways(self, guild_id, limit=25):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE guild_id = ? AND is_ended = 1 ORDER BY end_timestamp DESC LIMIT ?", (guild_id, limit)) as cursor:
                return await cursor.fetchall()

    async def get_all_active_giveaways(self, guild_id, limit=25):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM giveaways WHERE guild_id = ? AND is_ended = 0 ORDER BY end_timestamp ASC LIMIT ?", (guild_id, limit)) as cursor:
                return await cursor.fetchall()

    async def clean_old_giveaways(self, days_old=30):
        cutoff_timestamp = time.time() - (days_old * 86400)
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT message_id FROM giveaways WHERE is_ended = 1 AND end_timestamp < ?", (cutoff_timestamp,)) as cursor:
                to_delete = await cursor.fetchall()
            
            if not to_delete: return 0
                
            giveaway_ids = [row[0] for row in to_delete]
            await db.execute(f"DELETE FROM participants WHERE message_id IN ({','.join('?' for _ in giveaway_ids)})", giveaway_ids)
            await db.execute(f"DELETE FROM giveaways WHERE message_id IN ({','.join('?' for _ in giveaway_ids)})", giveaway_ids)
            await db.commit()
            return len(giveaway_ids)

class GiveawayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="0", emoji="🎉", style=discord.ButtonStyle.secondary, custom_id="giveaway:join")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        manager = interaction.client.get_cog("Giveaway").manager
        
        is_new_participant = await manager.add_participant(interaction.message.id, interaction.user.id)
        
        if is_new_participant:
            await interaction.response.send_message("You have successfully entered the giveaway!", ephemeral=True)
        else:
            await manager.remove_participant(interaction.message.id, interaction.user.id)
            await interaction.response.send_message("You have left the giveaway.", ephemeral=True)
            
        count = await manager.get_participant_count(interaction.message.id)
        button.label = str(count)
        await interaction.message.edit(view=self)

class GiveawaySelect(discord.ui.Select):
    def __init__(self, giveaways, custom_id):
        options = [discord.SelectOption(label=f"{gw['prize'][:80]}...", value=str(gw['message_id'])) for gw in giveaways]
        super().__init__(placeholder="Select a giveaway...", options=options, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("Giveaway")
        if self.custom_id == "giveaway:reroll_select":
            await cog.do_reroll(interaction, int(self.values[0]))
        elif self.custom_id == "giveaway:end_select":
            await cog.do_end(interaction, int(self.values[0]))

class GiveawayInputModal(discord.ui.Modal):
    def __init__(self, view, title, label, placeholder, style=discord.TextStyle.short):
        super().__init__(title=title)
        self.original_view = view
        self.input = discord.ui.TextInput(label=label, placeholder=placeholder, style=style, max_length=100)
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.original_view.update_value(interaction, self.input.label, self.input.value)

class GiveawaySetupView(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.prize = None
        self.duration = None
        self.winner_count = None
        self.channel = None
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("You are not the host of this giveaway setup.", ephemeral=True)
            return False
        return True

    def create_embed(self):
        embed = discord.Embed(title="🎉 Giveaway Setup", color=0x977FD7)
        embed.description = "Use the buttons below to configure your giveaway. All fields are required."
        embed.add_field(name="Prize", value=self.prize or "Not Set", inline=False)
        embed.add_field(name="Duration", value=self.duration or "Not Set", inline=False)
        embed.add_field(name="Winners", value=self.winner_count or "Not Set", inline=False)
        embed.add_field(name="Channel", value=self.channel.mention if self.channel else "Not Set", inline=False)
        return embed

    async def update_view(self, interaction: discord.Interaction):
        all_set = all([self.prize, self.duration, self.winner_count, self.channel])
        self.children[-2].disabled = not all_set
        await interaction.message.edit(embed=self.create_embed(), view=self)

    async def update_value(self, interaction: discord.Interaction, label: str, value: str):
        if label.lower() == "prize":
            self.prize = value
        elif label.lower() == "duration":
            self.duration = value
        elif label.lower() == "winners":
            self.winner_count = value
        
        await interaction.response.defer()
        await self.update_view(interaction)
    
    @discord.ui.button(label="Set Prize", style=discord.ButtonStyle.secondary, row=0)
    async def set_prize_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GiveawayInputModal(self, "Set Prize", "Prize", "e.g., 1 Million Coins"))

    @discord.ui.button(label="Set Duration", style=discord.ButtonStyle.secondary, row=0)
    async def set_duration_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GiveawayInputModal(self, "Set Duration", "Duration", "e.g., 1d, 12h, 30m"))

    @discord.ui.button(label="Set Winners", style=discord.ButtonStyle.secondary, row=0)
    async def set_winners_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GiveawayInputModal(self, "Set Winner Count", "Winners", "e.g., 1"))

    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text], placeholder="Select a channel...", row=1)
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        self.channel = select.values[0]
        await interaction.response.defer()
        await self.update_view(interaction)

    @discord.ui.button(label="Start Giveaway", style=discord.ButtonStyle.green, row=2, disabled=True)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog("Giveaway")
        await cog.start_giveaway_from_view(interaction, self)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="Giveaway setup cancelled.", embed=None, view=None)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = GiveawayManager(bot)
        self.giveaway_ender.start()

    async def cog_load(self):
        self.bot.add_view(GiveawayView())

    def cog_unload(self):
        self.giveaway_ender.cancel()

    @tasks.loop(seconds=15)
    async def giveaway_ender(self):
        await self.bot.wait_until_ready()
        active_giveaways = await self.manager.get_active_giveaways()
        for gw in active_giveaways:
            await self.end_giveaway_logic(gw)

    async def end_giveaway_logic(self, giveaway_data, interaction: Optional[discord.Interaction] = None):
        channel = self.bot.get_channel(giveaway_data["channel_id"])
        if not channel: return await self.manager.end_giveaway(giveaway_data["message_id"])

        try:
            message = await channel.fetch_message(giveaway_data["message_id"])
        except discord.NotFound:
            return await self.manager.end_giveaway(giveaway_data["message_id"])

        participants = await self.manager.get_participants(giveaway_data["message_id"])
        winner_count = giveaway_data["winner_count"]
        
        winners_str = "No one entered the giveaway. 😭"
        if participants:
            num_to_draw = min(winner_count, len(participants))
            winner_ids = random.sample(participants, num_to_draw)
            winners_str = " ".join(f"<@{w_id}>" for w_id in winner_ids)
        
        host = self.bot.get_user(giveaway_data["host_id"])
        
        embed = discord.Embed(
            title=f"🎉 Giveaway Ended 🎉",
            description=f"**Prize:** {giveaway_data['prize']}\n"
                        f"**Winner(s):** {winners_str}\n"
                        f"Hosted by: {host.mention if host else 'Unknown'}",
            color=0x36393F
        )
        
        disabled_view = GiveawayView()
        for item in disabled_view.children: item.disabled = True
        
        await message.edit(embed=embed, view=disabled_view)
        
        if "No one entered" not in winners_str:
            await channel.send(f"Congratulations {winners_str}! You won the **{giveaway_data['prize']}**!")
        
        await self.manager.end_giveaway(giveaway_data["message_id"])
        if interaction:
            await interaction.response.send_message(f"Successfully ended the giveaway for **{giveaway_data['prize']}**.", ephemeral=True)

    async def start_giveaway_from_view(self, interaction: discord.Interaction, view: GiveawaySetupView):
        def convert_duration(d):
            pos = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            unit = d[-1].lower()
            if unit not in pos: return None
            try: val = int(d[:-1])
            except ValueError: return None
            return val * pos[unit]

        duration_seconds = convert_duration(view.duration)
        if duration_seconds is None:
            return await interaction.response.send_message("Invalid duration format.", ephemeral=True)

        try:
            winner_count = int(view.winner_count)
            if winner_count < 1: raise ValueError
        except ValueError:
            return await interaction.response.send_message("Winner count must be a positive number.", ephemeral=True)
        
        prize = view.prize
        channel = interaction.guild.get_channel(view.channel.id) # Fetch the full channel object
        if not channel:
            return await interaction.response.send_message("Could not find the selected channel.", ephemeral=True)

        end_timestamp = time.time() + duration_seconds

        embed = discord.Embed(
            title=f"🎉 {prize} 🎉",
            description=f"React with 🎉 to enter!\n"
                        f"Ends: <t:{int(end_timestamp)}:R>\n"
                        f"Hosted by: {interaction.user.mention}",
            color=0x977FD7,
            timestamp=datetime.datetime.fromtimestamp(end_timestamp)
        )
        embed.set_footer(text=f"{winner_count} Winner(s) | Ends at")

        giveaway_view = GiveawayView()
        giveaway_message = await channel.send(embed=embed, view=giveaway_view)
        
        async with aiosqlite.connect(self.manager.db_path) as db:
             await db.execute(
                "INSERT INTO giveaways (message_id, guild_id, channel_id, host_id, prize, end_timestamp, winner_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (giveaway_message.id, interaction.guild.id, channel.id, interaction.user.id, prize, end_timestamp, winner_count)
            )
             await db.commit()
        
        await interaction.response.edit_message(content=f"Giveaway started in {channel.mention}!", embed=None, view=None)

    @commands.hybrid_group(name="giveaway", description="Commands for managing giveaways.")
    @app_commands.default_permissions(manage_guild=True)
    async def giveaway(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @giveaway.command(name="start", description="Starts a giveaway.")
    async def gstart(self, ctx: commands.Context):
        view = GiveawaySetupView(ctx)
        embed = view.create_embed()
        await ctx.send(embed=embed, view=view)

    @giveaway.command(name="reroll", description="Rerolls a finished giveaway.")
    async def greroll(self, ctx: commands.Context):
        ended_giveaways = await self.manager.get_ended_giveaways(ctx.guild.id)
        if not ended_giveaways:
            return await ctx.send("No recently ended giveaways found to reroll.", ephemeral=True)
        
        view = discord.ui.View(timeout=60)
        view.add_item(GiveawaySelect(ended_giveaways, "giveaway:reroll_select"))
        await ctx.send("Please select a giveaway to reroll:", view=view, ephemeral=True)

    async def do_reroll(self, interaction: discord.Interaction, message_id: int):
        await interaction.response.defer(ephemeral=True)
        giveaway_data = await self.manager.get_giveaway(message_id)
        if not giveaway_data or not giveaway_data['is_ended']:
            return await interaction.followup.send("This giveaway is not valid or hasn't ended.", ephemeral=True)
        
        participants = await self.manager.get_participants(message_id)
        if not participants:
            return await interaction.followup.send("There are no participants to reroll from.", ephemeral=True)
        
        winner_id = random.choice(participants)
        
        await interaction.followup.send("Rerolling...", ephemeral=True)
        await interaction.channel.send(f"🎉 New winner! Congratulations <@{winner_id}>, you won the **{giveaway_data['prize']}** in a reroll!")

    @giveaway.command(name="end", description="Ends an active giveaway immediately.")
    async def gend(self, ctx: commands.Context):
        active_giveaways = await self.manager.get_all_active_giveaways(ctx.guild.id)
        if not active_giveaways:
            return await ctx.send("There are no active giveaways to end.", ephemeral=True)
        
        view = discord.ui.View(timeout=60)
        view.add_item(GiveawaySelect(active_giveaways, "giveaway:end_select"))
        await ctx.send("Please select a giveaway to end:", view=view, ephemeral=True)

    async def do_end(self, interaction: discord.Interaction, message_id: int):
        giveaway_data = await self.manager.get_giveaway(message_id)
        if not giveaway_data or giveaway_data['is_ended']:
            return await interaction.response.send_message("This giveaway is not active or has already ended.", ephemeral=True)
        
        await self.end_giveaway_logic(giveaway_data, interaction)

    @giveaway.command(name="list", description="Lists all active giveaways in the server.")
    async def glist(self, ctx: commands.Context):
        active_giveaways = await self.manager.get_all_active_giveaways(ctx.guild.id)
        if not active_giveaways:
            return await ctx.send("There are no active giveaways in this server.", ephemeral=True)
        
        embed = discord.Embed(title="Active Giveaways", color=0x977FD7)
        description = ""
        for gw in active_giveaways:
            description += f"🔹 **{gw['prize']}** - [Jump to Giveaway](https://discord.com/channels/{gw['guild_id']}/{gw['channel_id']}/{gw['message_id']}) - Ends <t:{int(gw['end_timestamp'])}:R>\n"
        
        embed.description = description
        await ctx.send(embed=embed, ephemeral=True)

    @giveaway.command(name="clean", description="Cleans up giveaway data older than 30 days.")
    @commands.has_permissions(administrator=True)
    async def gclean(self, ctx: commands.Context):
        count = await self.manager.clean_old_giveaways()
        await ctx.send(f"Successfully cleaned up `{count}` old giveaway records.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
