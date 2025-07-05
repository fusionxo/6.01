import discord
import functools
from typing import Union

class Dropdown(discord.ui.Select):
    def __init__(self, ctx, options):
        super().__init__(placeholder="Select from main module.", min_values=1, max_values=1, options=options)
        self.invoker = ctx.author

    async def callback(self, interaction: discord.Interaction):
        if self.invoker != interaction.user:
            return await interaction.response.send_message("❌ Hey it's not your session!", ephemeral=True)

        index = self.view.find_index_from_select(self.values[0])
        if index is not None:
            # Set the view's active list to the main embeds
            self.view.active_embeds = self.view.embeds
            self.view.index = index
            embed = self.view.active_embeds[self.view.index]
            self.view._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self.view)

class Dropdown2(discord.ui.Select):
    def __init__(self, ctx, options):
        super().__init__(placeholder="Select from extra module.", min_values=1, max_values=1, options=options)
        self.invoker = ctx.author

    async def callback(self, interaction: discord.Interaction):
        if self.invoker != interaction.user:
            return await interaction.response.send_message("❌ Hey it's not your session!", ephemeral=True)

        index = self.view.find_index_from_select2(self.values[0])
        if index is not None:
            self.view.active_embeds = self.view.embeds2
            self.view.index = index
            embed = self.view.active_embeds[self.view.index]
            self.view._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self.view)

class Buttons(discord.ui.Button):
    def __init__(self, command, ctx, emoji, style: discord.ButtonStyle, args=None):
        super().__init__(emoji=emoji, style=style)
        self.command = command
        self.invoker = ctx.author
        self.args = args

    async def callback(self, interaction: discord.Interaction):
        if self.invoker != interaction.user:
            return await interaction.response.send_message("❌ Hey it's not your session!", ephemeral=True)

        if self.args is not None:
            func = functools.partial(self.command, self.args, interaction)
            await func()
        else:
            await self.command(interaction)

class View(discord.ui.View):
    def __init__(self, mapping: dict, ctx: discord.ext.commands.context.Context, homeembed: discord.embeds.Embed, ui: int):
        super().__init__(timeout=180.0)
        self.mapping = mapping
        self.ctx = ctx
        self.home = homeembed
        self.index = 0
        self.buttons = []

        self.options, self.embeds = self.gen_embeds()
        self.options2, self.embeds2 = self.gen_dropdown2_content()
        
        self.active_embeds = self.embeds

        has_buttons = ui in (1, 2)
        has_dropdown1 = ui in (0, 2)
        has_dropdown2 = ui == 2 and self.options2

        if has_buttons:
            self.add_all_buttons()
            self._update_buttons()
        if has_dropdown1:
            self.add_item(Dropdown(ctx=self.ctx, options=self.options))
        if has_dropdown2:
            self.add_item(Dropdown2(ctx=self.ctx, options=self.options2))

    def add_all_buttons(self):
        self.startB = Buttons(emoji="<:bckwrd:1087776725443809290>", style=discord.ButtonStyle.grey, command=self.set_page, args=0, ctx=self.ctx)
        self.backB = Buttons(emoji="<:start:1087776654383919164>", style=discord.ButtonStyle.grey, command=self.to_page, args=-1, ctx=self.ctx)
        self.homeB = Buttons(emoji="<:home:1087776882080096358>", style=discord.ButtonStyle.grey, command=self.show_home, ctx=self.ctx)
        self.nextB = Buttons(emoji="<:eend:1087776923226210455>", style=discord.ButtonStyle.grey, command=self.to_page, args=+1, ctx=self.ctx)
        # Use a string for the 'end' argument to make it dynamic
        self.endB = Buttons(emoji="<:fastfrwrd:1087776918637662249>", style=discord.ButtonStyle.grey, command=self.set_page, args="end", ctx=self.ctx)
        
        self.buttons = [self.startB, self.backB, self.homeB, self.nextB, self.endB]
        for button in self.buttons:
            self.add_item(button)

    def _update_buttons(self):
        if not self.buttons:
            return
        
        max_pages = len(self.active_embeds) - 1
        at_start = self.index == 0
        at_end = self.index >= max_pages

        self.startB.disabled = at_start
        self.backB.disabled = at_start
        self.nextB.disabled = at_end
        self.endB.disabled = at_end

    def find_index_from_select(self, label_value: str):
        return next((i for i, option in enumerate(self.options) if option.label == label_value), None)

    def find_index_from_select2(self, label_value: str):
        return next((i for i, option in enumerate(self.options2) if option.label == label_value), None)

    def get_cogs(self):
        return [cog for cog in self.mapping.keys() if cog and cog.get_commands()]

    def gen_embeds(self):
        options, embeds = [], []
        for cog in self.get_cogs():
            if hasattr(cog, "help_custom"):
                emoji, label, description = cog.help_custom()
                options.append(discord.SelectOption(label=label, emoji=emoji, description=description))
                embed = discord.Embed(title=f"**Luka | {label}**", description="Luka", color=0x977FD7)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
                embed.set_footer(text="Luka |")
                for command in cog.get_commands():
                    params = " ".join(f"<{param}>" for param in command.clean_params)
                    embed.add_field(name=f"/{command.name} {params}", value=command.short_doc or "No description provided.", inline=False)
                embeds.append(embed)
        return options, embeds

    def gen_dropdown2_content(self):
        options, embeds = [], []
        for cog in self.get_cogs():
            if hasattr(cog, "help2_custom"):
                emoji, label, description = cog.help2_custom()
                options.append(discord.SelectOption(label=label, emoji=emoji, description=description))
                embed = discord.Embed(title=f"**Luka | {label}**", description="Luka", color=0x977FD7)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
                embed.set_footer(text="Luka |")
                for command in cog.get_commands():
                    params = " ".join(f"<{param}>" for param in command.clean_params)
                    embed.add_field(name=f"/{command.name} {params}", value=command.short_doc or "No description provided.", inline=False)
                embeds.append(embed)
        return options, embeds

    async def to_page(self, page_offset: int, interaction: discord.Interaction):
        self.index += page_offset
        self._update_buttons()
        embed = self.active_embeds[self.index]
        await interaction.response.edit_message(embed=embed, view=self)

    async def set_page(self, page: Union[int, str], interaction: discord.Interaction):
        if page == "end":
            self.index = len(self.active_embeds) - 1
        else:
            self.index = int(page)
        
        self._update_buttons()
        embed = self.active_embeds[self.index]
        await interaction.response.edit_message(embed=embed, view=self)

    async def show_home(self, interaction: discord.Interaction):
        self.active_embeds = self.embeds
        self.index = 0
        self._update_buttons()
        await interaction.response.edit_message(embed=self.home, view=self)
