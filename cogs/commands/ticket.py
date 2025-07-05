import discord
from discord.ext import commands
from discord import ui
import aiosqlite
import asyncio

# --- MODALS FOR TICKET SETUP ---

class EmbedMenuModal(discord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Ticket System Setup", timeout=None)
        self.cog = cog
        
        self.category_id = discord.ui.TextInput(
            label="Main Category ID",
            placeholder="Enter the category ID for tickets...",
            style=discord.TextStyle.short,
            required=True
        )
        self.log_channel_id = discord.ui.TextInput(
            label="Log Channel ID",
            placeholder="Enter the log channel ID...",
            style=discord.TextStyle.short,
            required=True
        )
        self.multiple_menus = discord.ui.TextInput(
            label="Multiple Menus?",
            placeholder="Type 'yes' if you want multiple menus (drop-down), else 'no'",
            style=discord.TextStyle.short,
            required=True
        )
        self.menu_count = discord.ui.TextInput(
            label="Number of Menus",
            placeholder="Enter a number greater than 1 (max 5) if multiple menus are desired",
            style=discord.TextStyle.short,
            required=False
        )
        
        self.add_item(self.category_id)
        self.add_item(self.log_channel_id)
        self.add_item(self.multiple_menus)
        self.add_item(self.menu_count)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            main_category_id = int(self.category_id.value)
            log_channel_id = int(self.log_channel_id.value)
        except ValueError:
            await interaction.followup.send("❌ IDs must be numbers!", ephemeral=True)
            return

        category = interaction.guild.get_channel(main_category_id)
        log_channel = interaction.guild.get_channel(log_channel_id)

        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("❌ Invalid main category ID!", ephemeral=True)
            return
            
        if not log_channel or not isinstance(log_channel, discord.TextChannel):
            await interaction.followup.send("❌ Invalid log channel ID!", ephemeral=True)
            return

        async with aiosqlite.connect('databases/ticket.db') as conn:
            await conn.execute(f"""INSERT OR REPLACE INTO ticket_creation_category(guild_id, category_id)
                                VALUES({interaction.guild_id}, {main_category_id})""")
            await conn.execute(f"""INSERT OR REPLACE INTO ticket_log_channel(guild_id, channel_id)
                                VALUES({interaction.guild_id}, {log_channel.id})""")
            await conn.commit()

        self.cog.main_category_id = main_category_id

        panel_channel, panel_message = await self.cog.create_ticket_panel(interaction, main_category_id)
        self.cog.panel_channel = panel_channel
        self.cog.panel_message = panel_message

        if self.multiple_menus.value.strip().lower() == "yes":
            try:
                count = int(self.menu_count.value.strip())
                if count <= 1 or count > 5:
                    await interaction.followup.send("❌ Menu count must be greater than 1 and at most 5!", ephemeral=True)
                    return
            except Exception:
                await interaction.followup.send("❌ Please provide a valid number of menus!", ephemeral=True)
                return
            self.cog.pending_menu_count = count
            await interaction.followup.send(
                f"Please provide {count} menu names (comma-separated).",
                ephemeral=True
            )
            modal = MenuNamesModal(self.cog)
            await interaction.followup.send_modal(modal)
        else:
            self.cog.pending_menu_count = 0
            await interaction.followup.send(
                f"✅ Ticket setup complete! Panel created in {panel_channel.mention}",
                ephemeral=True
            )

class MenuNamesModal(discord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Menu Names Setup", timeout=None)
        self.cog = cog
        self.menu_names = discord.ui.TextInput(
            label="Menu Names",
            placeholder="Enter menu names separated by commas (e.g., update, help, test)",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.menu_names)

    async def on_submit(self, interaction: discord.Interaction):
        names = [name.strip() for name in self.menu_names.value.split(",") if name.strip()]
        if len(names) != self.cog.pending_menu_count:
            await interaction.response.send_message(
                f"❌ You entered {len(names)} names but expected {self.cog.pending_menu_count}.",
                ephemeral=True
            )
            return
        self.cog.menu_names = names
        view = TicketCreationMenuView(names)
        try:
            await self.cog.panel_message.edit(view=view)
        except Exception as e:
            print("Failed to update panel message with menus:", e)
        await interaction.response.send_message("Ticket panel updated with menus.", ephemeral=True)

# --- VIEWS FOR TICKET PANEL ---

class TicketCreationButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket", emoji="<:ticketalt:1297899425091289089>")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect("databases/ticket.db") as conn:
            ticket_check_query = f"SELECT channel_id FROM user_ticket WHERE user_id = {interaction.user.id};"
            result = await conn.execute(ticket_check_query)
            fetch = await result.fetchone()
            
            if fetch:
                channel = interaction.guild.get_channel(fetch[0])
                if channel:
                    await interaction.response.send_message(
                        f"You already have an active ticket in {channel.mention}!",
                        ephemeral=True
                    )
                    return
                else:
                    await conn.execute(f"DELETE FROM user_ticket WHERE user_id = {interaction.user.id};")
                    await conn.commit()
                    await interaction.response.send_message(
                        "Your previous ticket channel was deleted. Creating a new ticket...",
                        ephemeral=True
                    )

        new_ticket_query = f"SELECT category_id FROM ticket_creation_category WHERE guild_id = {interaction.guild.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(new_ticket_query)
            fetch = await result.fetchone()

        category = interaction.guild.get_channel(fetch[0])
        overwrites = {
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            category=category,
            overwrites=overwrites
        )
        
        await interaction.response.send_message(
            f"Ticket created in {channel.mention}",
            ephemeral=True
        )

        view = TicketManagementButtons()
        welcome_embed = discord.Embed(
            title=f"Welcome {interaction.user.display_name}! Please state your issue",
            description="Use the buttons below to manage this ticket",
            colour=discord.Colour(0x977FD7)
        )
        await channel.send(f"{interaction.user.mention}", embed=welcome_embed, view=view)

        whose_ticket_query = f"""INSERT INTO user_ticket(guild_id,user_id,channel_id)
        VALUES({interaction.guild.id},{interaction.user.id},{channel.id})"""
        async with aiosqlite.connect('databases/ticket.db') as conn:
            await conn.execute(whose_ticket_query)
            await conn.commit()

        ticket_log_query = f"SELECT channel_id FROM ticket_log_channel WHERE guild_id = {interaction.guild.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(ticket_log_query)
            fetch = await result.fetchone()

        log_channel = interaction.guild.get_channel(fetch[0])
        log_embed = discord.Embed(
            title="New Ticket opened",
            colour=discord.Colour(0x977FD7),
            timestamp=interaction.created_at
        )
        log_embed.add_field(name="Created by:", value=f"`{interaction.user.display_name}`", inline=False)
        log_embed.add_field(name="Channel:", value=f"`#{channel.name}`", inline=False)
        log_embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        await log_channel.send(embed=log_embed)

class TicketCreationMenuView(discord.ui.View):
    def __init__(self, menu_names: list):
        super().__init__(timeout=None)
        select_options = []
        for name in menu_names:
            select_options.append(
                discord.SelectOption(
                    label=name,
                    value=name.lower(),
                    description=f"Open ticket with prefix '{name.lower()}-'"
                )
            )
        self.add_item(TicketMenuSelect(select_options))

class TicketMenuSelect(discord.ui.Select):
    def __init__(self, select_options):
        super().__init__(placeholder="Choose a menu option", min_values=1, max_values=1, options=select_options, custom_id="menu_select")

    async def callback(self, interaction: discord.Interaction):
        async with aiosqlite.connect("databases/ticket.db") as conn:
            ticket_check_query = f"SELECT channel_id FROM user_ticket WHERE user_id = {interaction.user.id};"
            result = await conn.execute(ticket_check_query)
            fetch = await result.fetchone()
            if fetch:
                channel = interaction.guild.get_channel(fetch[0])
                if channel:
                    await interaction.response.send_message(
                        f"You already have an active ticket in {channel.mention}!",
                        ephemeral=True
                    )
                    return
                else:
                    await conn.execute(f"DELETE FROM user_ticket WHERE user_id = {interaction.user.id};")
                    await conn.commit()
                    await interaction.response.send_message(
                        "Your previous ticket channel was deleted. Creating a new one...",
                        ephemeral=True
                    )
        selected_prefix = self.values[0]
        main_cat_id = interaction.client.get_cog("TicketCog").main_category_id
        category = interaction.guild.get_channel(main_cat_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("❌ The main category is invalid.", ephemeral=True)
            return

        overwrites = {
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        channel = await interaction.guild.create_text_channel(
            name=f"{selected_prefix}-{interaction.user.id}",
            category=category,
            overwrites=overwrites
        )
        await interaction.response.send_message(
            f"Ticket created in {channel.mention}",
            ephemeral=True
        )
        view = TicketManagementButtons()
        welcome_embed = discord.Embed(
            title=f"Welcome {interaction.user.display_name}! Please state your issue",
            description="Use the buttons below to manage this ticket",
            colour=discord.Colour(0x977FD7)
        )
        await channel.send(f"{interaction.user.mention}", embed=welcome_embed, view=view)

        whose_ticket_query = f"""INSERT INTO user_ticket(guild_id,user_id,channel_id)
        VALUES({interaction.guild.id},{interaction.user.id},{channel.id})"""
        async with aiosqlite.connect('databases/ticket.db') as conn:
            await conn.execute(whose_ticket_query)
            await conn.commit()

        ticket_log_query = f"SELECT channel_id FROM ticket_log_channel WHERE guild_id = {interaction.guild.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(ticket_log_query)
            fetch = await result.fetchone()

        log_channel = interaction.guild.get_channel(fetch[0])
        log_embed = discord.Embed(
            title="New Ticket opened via Menu",
            colour=discord.Colour(0x977FD7),
            timestamp=interaction.created_at
        )
        log_embed.add_field(name="Created by:", value=f"`{interaction.user.display_name}`", inline=False)
        log_embed.add_field(name="Channel:", value=f"`#{channel.name}`", inline=False)
        log_embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        await log_channel.send(embed=log_embed)

# --- TICKET MANAGEMENT COMPONENTS ---

class AddMemberView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60.0)
        self.add_item(AddMemberSelect())

class AddMemberSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(
            placeholder="Select members to add...",
            min_values=1,
            max_values=5,
            custom_id="add_member_select"
        )

    async def callback(self, interaction: discord.Interaction):
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(f"SELECT user_id FROM user_ticket WHERE channel_id = {interaction.channel.id};")
            fetch = await result.fetchone()
        
        if not fetch:
            await interaction.response.send_message("❌ Ticket owner could not be determined.", ephemeral=True)
            return

        ticket_owner_id = fetch[0]
        if interaction.user.id != ticket_owner_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to do this!", ephemeral=True)
            return

        try:
            overwrites = interaction.channel.overwrites.copy()
            added_members = []
            
            for member in self.values:
                if member not in overwrites or not overwrites[member].read_messages:
                    overwrites[member] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True
                    )
                    added_members.append(member.mention)
            
            if not added_members:
                await interaction.response.send_message("❌ No new members to add!", ephemeral=True)
                return

            await interaction.channel.edit(overwrites=overwrites)
            await interaction.response.send_message(
                f"✅ Added {', '.join(added_members)} to the ticket!",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error adding members: {str(e)}",
                ephemeral=True
            )


class TicketManagementButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Add Member", style=discord.ButtonStyle.primary, custom_id="add_member", emoji="<:useradd1:1297900381942054922>")
    async def add_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(f"SELECT user_id FROM user_ticket WHERE channel_id = {interaction.channel.id};")
            fetch = await result.fetchone()

        if not fetch:
            await interaction.response.send_message("❌ Ticket owner not found for this ticket!", ephemeral=True)
            return

        ticket_owner_id = fetch[0]
        if interaction.user.id != ticket_owner_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission to use this!", ephemeral=True)
            return
        
        view = AddMemberView()
        await interaction.response.send_message(
            "Select members to add to the ticket:",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(label="Close", style=discord.ButtonStyle.secondary, custom_id="close_ticket", emoji="<:lock:1297899422625042436>")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        member_get_query = f"SELECT user_id FROM user_ticket WHERE channel_id = {interaction.channel.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(member_get_query)
            fetch = await result.fetchone()

        if not fetch:
            await interaction.response.send_message("No ticket found!", ephemeral=True)
            return

        member = interaction.guild.get_member(fetch[0])
        overwrites = {
            member: discord.PermissionOverwrite(send_messages=False, view_channel=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        await interaction.channel.edit(overwrites=overwrites)
        
        embed = discord.Embed(
            title="Ticket Closed",
            description="Use the buttons below to manage the closed ticket",
            colour=discord.Colour(0x977FD7)
        )
        await interaction.response.send_message(embed=embed, view=ClosedTicketButtons())

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, custom_id="delete_ticket", emoji="<:trash:1297899427675242506>")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this!", ephemeral=True)
            return
            
        confirm_view = ConfirmView()
        await interaction.response.send_message("Are you sure you want to delete this ticket?", view=confirm_view)

class ClosedTicketButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.primary, custom_id="reopen_ticket", emoji="<:unlock:1297899416837160992>")
    async def reopen_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this!", ephemeral=True)
            return

        member_get_query = f"SELECT user_id FROM user_ticket WHERE channel_id = {interaction.channel.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(member_get_query)
            fetch = await result.fetchone()

        member = interaction.guild.get_member(fetch[0])
        overwrites = {
            member: discord.PermissionOverwrite(read_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        await interaction.channel.edit(overwrites=overwrites)
        
        view = TicketManagementButtons()
        embed = discord.Embed(
            description=f"Ticket reopened by {interaction.user.mention}",
            colour=discord.Colour(0x977FD7)
        )
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="Save Transcript", style=discord.ButtonStyle.secondary, custom_id="save_transcript", emoji="<:bookmark:1297899419517059203>")
    async def save_transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this!", ephemeral=True)
            return

        await interaction.response.defer()

        ticket_log_query = f"SELECT channel_id FROM ticket_log_channel WHERE guild_id = {interaction.guild.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            result = await conn.execute(ticket_log_query)
            fetch = await result.fetchone()

        log_channel = interaction.guild.get_channel(fetch[0])

        with open('logs.txt', 'w', encoding='utf-8') as f:
            async for message in interaction.channel.history(limit=500, oldest_first=True):
                f.write(f"{message.created_at} - {message.author.display_name}: {message.content}\n")
                for embed in message.embeds:
                    f.write(f"{message.created_at} - {message.author.display_name}: [Embed] {embed.title}\n")

        await log_channel.send(
            f"Transcript for {interaction.channel.name}",
            file=discord.File('logs.txt')
        )
        await interaction.followup.send("Transcript saved!")

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60.0)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        delete_query = f"DELETE FROM user_ticket WHERE channel_id = {interaction.channel.id};"
        async with aiosqlite.connect('databases/ticket.db') as conn:
            await conn.execute(delete_query)
            await conn.commit()

        await interaction.channel.send("Deleting channel in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Deletion cancelled!", ephemeral=True)

# --- TICKET COG ---

prefix = '$'

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False
        self.pending_menu_count = 0
        self.menu_names = []
        self.main_category_id = None
        self.panel_channel = None
        self.panel_message = None

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(TicketCreationButton())
            self.bot.add_view(TicketManagementButtons())
            self.bot.add_view(ClosedTicketButtons())
            self.persistent_views_added = True
        print("Ticket Cog is online")

    async def create_ticket_panel(self, ctx, main_category_id):
        channel = await ctx.guild.create_text_channel(
            name="ticket",
            category=discord.utils.get(ctx.guild.categories, id=main_category_id)
        )
        embed = discord.Embed(
            title="Create a Ticket",
            description="Click the button below to create a ticket.\n"
                        "Or use the drop-down menu (if available) to choose a ticket category.",
            colour=discord.Colour(0x977FD7)
        )
        view = TicketCreationButton()
        message = await channel.send(embed=embed, view=view)
        
        async with aiosqlite.connect('databases/ticket.db') as conn:
            await conn.execute(query5)
            panel_query = f"""INSERT OR REPLACE INTO ticket_panel(guild_id, channel_id, message_id)
            VALUES({ctx.guild.id}, {channel.id}, {message.id})"""
            await conn.execute(panel_query)
            await conn.commit()
        
        return channel, message

    @commands.hybrid_group(name="ticket", invoke_without_command=True)
    async def ticket(self, ctx):
        guild_icon_url = ctx.guild.icon.url if ctx.guild.icon else "https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png"
        embed = discord.Embed(
            title="**Luka | Ticket Help**",
            description=f"prefix : `{prefix}`",
            colour=discord.Colour(0x977FD7),
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="Setup bot:", value=f"`{prefix}ticket setup`", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=ctx.guild.name, icon_url=guild_icon_url)
        await ctx.send(embed=embed)

    @ticket.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx: commands.Context):
        """Setup ticket system using a modal"""
        if not ctx.interaction:
            await ctx.send("ℹ️ Please use this command as a slash command (`/ticket setup`) to use the modal!")
            return
        modal = EmbedMenuModal(self)
        await ctx.interaction.response.send_modal(modal)

    @ticket.command()
    async def create(self, ctx):
        await TicketCreationButton().create_ticket(ctx.interaction, None)

def setup(bot):
    bot.add_cog(TicketCog(bot))
