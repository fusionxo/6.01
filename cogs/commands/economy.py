import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import asyncio
import json
import random
import time
from typing import Optional

DB_PATH = "databases/economy.db"
CURRENCY_NAME = "L-Coins"
CURRENCY_EMOJI = "💰"
DAILY_AMOUNT = 500
WORK_RANGE = (50, 250)
BEG_RANGE = (1, 10)
ROB_SUCCESS_CHANCE = 0.5
ROB_FINE_MULTIPLIER = 1.5

class EconomyManager:
    def __init__(self, db_path):
        self.db_path = db_path
        asyncio.create_task(self.setup_database())

    async def setup_database(self):
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    balance INTEGER DEFAULT 0,
                    inventory TEXT DEFAULT '{}',
                    last_daily REAL DEFAULT 0,
                    last_work REAL DEFAULT 0,
                    last_beg REAL DEFAULT 0,
                    last_rob REAL DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS shop (
                    guild_id INTEGER,
                    item_name TEXT,
                    price INTEGER,
                    description TEXT,
                    emoji TEXT,
                    PRIMARY KEY (guild_id, item_name)
                )
            """)
            await db.commit()

    async def get_user(self, user_id, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id)) as cursor:
                user_data = await cursor.fetchone()
                if not user_data:
                    await db.execute("INSERT INTO users (user_id, guild_id) VALUES (?, ?)", (user_id, guild_id))
                    await db.commit()
                    async with db.execute("SELECT * FROM users WHERE user_id = ? AND guild_id = ?", (user_id, guild_id)) as new_cursor:
                        return await new_cursor.fetchone()
                return user_data

    async def update_balance(self, user_id, guild_id, amount):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ? AND guild_id = ?", (amount, user_id, guild_id))
            await db.commit()

    async def update_inventory(self, user_id, guild_id, inventory: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET inventory = ? WHERE user_id = ? AND guild_id = ?", (json.dumps(inventory), user_id, guild_id))
            await db.commit()
            
    async def update_cooldown(self, user_id, guild_id, command_name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"UPDATE users SET last_{command_name} = ? WHERE user_id = ? AND guild_id = ?", (time.time(), user_id, guild_id))
            await db.commit()

    async def get_shop_items(self, guild_id):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM shop WHERE guild_id = ?", (guild_id,)) as cursor:
                return await cursor.fetchall()

    async def get_leaderboard(self, guild_id, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT user_id, balance FROM users WHERE guild_id = ? ORDER BY balance DESC LIMIT ?", (guild_id, limit)) as cursor:
                return await cursor.fetchall()

class ShopView(discord.ui.View):
    def __init__(self, items, cog):
        super().__init__(timeout=180)
        self.items = items
        self.cog = cog
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page >= len(self.items) - 1

    def create_embed(self):
        item = self.items[self.current_page]
        embed = discord.Embed(title=f"{item['emoji']} {item['item_name'].title()}", description=item['description'], color=0x977FD7)
        embed.add_field(name="Price", value=f"{item['price']} {CURRENCY_EMOJI}")
        embed.set_footer(text=f"Item {self.current_page + 1}/{len(self.items)}")
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.grey)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.green)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.buy_item(interaction, self.items[self.current_page]['item_name'])

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = EconomyManager(DB_PATH)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You missed a required argument: `{error.param.name}`", ephemeral=True)
        else:
            await ctx.send(f"An unexpected error occurred: {error}", ephemeral=True)
            raise error

    @commands.hybrid_command(name="balance", aliases=["bal"], description="Check your account balance.")
    async def balance(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        user_data = await self.manager.get_user(target.id, ctx.guild.id)
        embed = discord.Embed(title=f"{target.display_name}'s Balance", description=f"You have **{user_data['balance']}** {CURRENCY_EMOJI} {CURRENCY_NAME}", color=0x977FD7)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="work", description="Work to earn some money.")
    @commands.cooldown(1, 3600, commands.BucketType.user) # 1 hour cooldown
    async def work(self, ctx: commands.Context):
        earnings = random.randint(*WORK_RANGE)
        await self.manager.update_balance(ctx.author.id, ctx.guild.id, earnings)
        await ctx.send(f"You worked hard and earned **{earnings}** {CURRENCY_EMOJI} {CURRENCY_NAME}!")

    @commands.hybrid_command(name="daily", description="Claim your daily reward.")
    @commands.cooldown(1, 86400, commands.BucketType.user) # 24 hour cooldown
    async def daily(self, ctx: commands.Context):
        await self.manager.update_balance(ctx.author.id, ctx.guild.id, DAILY_AMOUNT)
        await ctx.send(f"You claimed your daily reward of **{DAILY_AMOUNT}** {CURRENCY_EMOJI} {CURRENCY_NAME}!")

    @commands.hybrid_command(name="beg", description="Beg for some spare change.")
    @commands.cooldown(1, 300, commands.BucketType.user) # 5 minute cooldown
    async def beg(self, ctx: commands.Context):
        earnings = random.randint(*BEG_RANGE)
        await self.manager.update_balance(ctx.author.id, ctx.guild.id, earnings)
        await ctx.send(f"A kind stranger gave you **{earnings}** {CURRENCY_EMOJI} {CURRENCY_NAME}.")

    @commands.hybrid_command(name="gamble", description="Gamble your money for a chance to win big.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gamble(self, ctx: commands.Context, amount: int):
        user_data = await self.manager.get_user(ctx.author.id, ctx.guild.id)
        if amount <= 0:
            return await ctx.send("You must gamble a positive amount.")
        if amount > user_data['balance']:
            return await ctx.send("You don't have enough money to gamble that much.")
        if amount > 10000: # Max bet limit
            return await ctx.send(f"You can't bet more than **10,000** {CURRENCY_EMOJI} at a time.")

        win = random.choices([True, False], weights=[0.4, 0.6], k=1)[0]
        if win:
            await self.manager.update_balance(ctx.author.id, ctx.guild.id, amount)
            await ctx.send(f"🎉 You won! You doubled your bet and received **{amount*2}** {CURRENCY_EMOJI} {CURRENCY_NAME}!")
        else:
            await self.manager.update_balance(ctx.author.id, ctx.guild.id, -amount)
            await ctx.send(f"😢 You lost... You forfeited **{amount}** {CURRENCY_EMOJI} {CURRENCY_NAME}.")

    @commands.hybrid_command(name="rob", description="Attempt to rob another user.")
    @commands.cooldown(1, 1800, commands.BucketType.user) # 30 minute cooldown
    async def rob(self, ctx: commands.Context, member: discord.Member):
        if member.id == ctx.author.id:
            return await ctx.send("You can't rob yourself.")
        
        author_data = await self.manager.get_user(ctx.author.id, ctx.guild.id)
        target_data = await self.manager.get_user(member.id, ctx.guild.id)

        if target_data['balance'] < 500:
            return await ctx.send(f"{member.display_name} is too poor to be robbed.")

        success = random.random() < ROB_SUCCESS_CHANCE
        if success:
            amount_stolen = int(target_data['balance'] * random.uniform(0.1, 0.3))
            await self.manager.update_balance(ctx.author.id, ctx.guild.id, amount_stolen)
            await self.manager.update_balance(member.id, ctx.guild.id, -amount_stolen)
            await ctx.send(f"You successfully robbed **{amount_stolen}** {CURRENCY_EMOJI} from {member.mention}!")
        else:
            fine = int(author_data['balance'] * ROB_FINE_MULTIPLIER * random.uniform(0.1, 0.2))
            await self.manager.update_balance(ctx.author.id, ctx.guild.id, -fine)
            await ctx.send(f"You were caught! You paid a fine of **{fine}** {CURRENCY_EMOJI}.")

    @commands.hybrid_command(name="shop", description="View items available to purchase.")
    async def shop(self, ctx: commands.Context):
        items = await self.manager.get_shop_items(ctx.guild.id)
        if not items:
            return await ctx.send("The shop is empty! An admin can add items with `/shopadd`.")
        
        view = ShopView(items, self)
        embed = view.create_embed()
        await ctx.send(embed=embed, view=view)

    async def buy_item(self, interaction: discord.Interaction, item_name: str):
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        items = await self.manager.get_shop_items(guild_id)
        item_to_buy = next((item for item in items if item['item_name'].lower() == item_name.lower()), None)
        
        if not item_to_buy:
            return await interaction.response.send_message("This item doesn't exist.", ephemeral=True)
        
        user_data = await self.manager.get_user(user_id, guild_id)
        if user_data['balance'] < item_to_buy['price']:
            return await interaction.response.send_message("You don't have enough money to buy this.", ephemeral=True)
            
        await self.manager.update_balance(user_id, guild_id, -item_to_buy['price'])
        
        inventory = json.loads(user_data['inventory'])
        inventory[item_name.lower()] = inventory.get(item_name.lower(), 0) + 1
        await self.manager.update_inventory(user_id, guild_id, inventory)
        
        await interaction.response.send_message(f"You purchased a **{item_name.title()}**!", ephemeral=True)

    @commands.hybrid_command(name="inventory", aliases=["inve"], description="Check your inventory.")
    async def inventory(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        target = member or ctx.author
        user_data = await self.manager.get_user(target.id, ctx.guild.id)
        inventory = json.loads(user_data['inventory'])
        
        if not inventory:
            return await ctx.send(f"**{target.display_name}**'s inventory is empty.")
            
        embed = discord.Embed(title=f"{target.display_name}'s Inventory", color=0x977FD7)
        description = "\n".join([f"**{item.title()}** `x{quantity}`" for item, quantity in inventory.items()])
        embed.description = description
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", aliases=["lb"], description="View the richest users.")
    async def leaderboard(self, ctx: commands.Context):
        results = await self.manager.get_leaderboard(ctx.guild.id)
        if not results:
            return await ctx.send("No one is on the leaderboard yet.")
            
        embed = discord.Embed(title=f"Leaderboard for {ctx.guild.name}", color=0x977FD7)
        description = ""
        for i, row in enumerate(results):
            user = self.bot.get_user(row['user_id']) or f"Unknown User ({row['user_id']})"
            description += f"`{i+1}.` **{user}** - {row['balance']} {CURRENCY_EMOJI}\n"
        embed.description = description
        await ctx.send(embed=embed)

    # --- Admin Commands ---
    @commands.hybrid_command(name="shopadd", description="[Admin] Add an item to the shop.")
    @commands.has_permissions(manage_guild=True)
    async def shopadd(self, ctx: commands.Context, price: int, name: str, emoji: str, *, description: str):
        async with aiosqlite.connect(self.manager.db_path) as db:
            try:
                await db.execute("INSERT INTO shop (guild_id, item_name, price, description, emoji) VALUES (?, ?, ?, ?, ?)",
                                 (ctx.guild.id, name.lower(), price, description, emoji))
                await db.commit()
                await ctx.send(f"Successfully added **{name.title()}** to the shop for `{price}` {CURRENCY_EMOJI}.")
            except aiosqlite.IntegrityError:
                await ctx.send("An item with this name already exists in the shop.")

    @commands.hybrid_command(name="shopremove", description="[Admin] Remove an item from the shop.")
    @commands.has_permissions(manage_guild=True)
    async def shopremove(self, ctx: commands.Context, *, name: str):
        async with aiosqlite.connect(self.manager.db_path) as db:
            cursor = await db.execute("DELETE FROM shop WHERE guild_id = ? AND item_name = ?", (ctx.guild.id, name.lower()))
            await db.commit()
            if cursor.rowcount > 0:
                await ctx.send(f"Successfully removed **{name.title()}** from the shop.")
            else:
                await ctx.send("Could not find an item with that name in the shop.")

async def setup(bot):
    await bot.add_cog(Economy(bot))
