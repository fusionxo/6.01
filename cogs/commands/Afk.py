import discord
from discord.ext import commands
import json
import time
from typing import Optional
import aiofiles
from utils import *
from utils.checks import global_check
import asyncio

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout: Optional[int] = 180):
        super().__init__(timeout=timeout)
        self.ctx = ctx
      
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(f"Only **{self.ctx.author.display_name}** can use these buttons.", ephemeral=True)
            return False
        return True

class OnOrOff(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    @discord.ui.button(label="Yes", emoji="<:check:1087776909246607360>", custom_id='Yes', style=discord.ButtonStyle.green)
    async def on_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="No", emoji="<:error:1088542929158688788>", custom_id='No', style=discord.ButtonStyle.danger)
    async def off_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        self.stop()

class Afk(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.afk_path = "jsons/afk.json"
        self.afk_cache = {}
        self.client.loop.create_task(self._load_data())

    async def cog_check(self, ctx: commands.Context) -> bool:
        """This check runs for every command in this cog."""
        # You can call your global check function here
        return await global_check(ctx)


    async def _load_data(self):
        try:
            async with aiofiles.open(self.afk_path, 'r') as f:
                self.afk_cache = json.loads(await f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            self.afk_cache = {}

    async def _save_data(self):
        async with aiofiles.open(self.afk_path, 'w') as f:
            await f.write(json.dumps(self.afk_cache, indent=4))

    def time_formatter(self, seconds: float):
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = ((str(days) + "d ") if days else "") + \
              ((str(hours) + "h ") if hours else "") + \
              ((str(minutes) + "m ") if minutes else "") + \
              ((str(seconds) + "s ") if seconds else "")
        return tmp.strip()

    async def handle_afk_return(self, message):
        author_id = str(message.author.id)
        afk_data = self.afk_cache.get(author_id)

        if not afk_data or afk_data.get('AFK') != 'True':
            return False

        start_time = afk_data.get('time', time.time())
        mentions = afk_data.get('mentions', 0)
        been_afk_for = self.time_formatter(time.time() - start_time)

        afk_data['AFK'] = 'False'
        afk_data['reason'] = None
        afk_data['mentions'] = 0

        await self._save_data()

        try:
            if message.author.nick and message.author.nick.startswith('[AFK]'):
                new_nick = message.author.nick[5:].strip()
                await message.author.edit(nick=new_nick)
        except discord.Forbidden:
            pass

        embed = discord.Embed(
            description=f"Welcome back {message.author.mention}, I removed your AFK. You were away for `{been_afk_for}` and had `{mentions}` mentions.",
            color=0x977FD7
        )
        await message.channel.send(embed=embed, delete_after=10)
        return True

    async def handle_afk_mentions(self, message):
        if not message.mentions:
            return

        for user in message.mentions:
            if user == message.author:
                continue

            user_id = str(user.id)
            afk_data = self.afk_cache.get(user_id)

            if not afk_data or afk_data.get('AFK') != 'True':
                continue
            
            reason = afk_data.get('reason', 'No reason provided.')
            start_time = afk_data.get('time', int(time.time()))

            embed = discord.Embed(
                description=f"**{user.display_name}** is AFK: {reason} (<t:{start_time}:R>)",
                color=0x977FD7
            )
            await message.channel.send(embed=embed, delete_after=15)

            afk_data['mentions'] = afk_data.get('mentions', 0) + 1

            if afk_data.get('dm') == 'True':
                try:
                    dm_embed = discord.Embed(
                        description=f"You were mentioned in **{message.guild.name}** by **{message.author}**.",
                        color=0x977FD7
                    )
                    dm_embed.add_field(name="Message", value=f"[{message.content or 'View Message'}]({message.jump_url})", inline=False)
                    await user.send(embed=dm_embed)
                except discord.Forbidden:
                    afk_data['dm'] = 'False'
            
            await self._save_data()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        if await self.handle_afk_return(message):
            return 
            
        await self.handle_afk_mentions(message)

    @commands.hybrid_command(name='afk', description="Set or remove your global AFK status.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def afk(self, ctx, *, reason: Optional[str] = "I am AFK."):
        author_id = str(ctx.author.id)
        
        if self.afk_cache.get(author_id, {}).get('AFK') == 'True':
            await self.handle_afk_return(ctx.message)
            return

        if any(invite in reason for invite in ['discord.gg', '.gg/', 'gg/']):
            return await ctx.send("You can't have server invites in your AFK reason.", ephemeral=True)

        view = OnOrOff(ctx)
        prompt_embed = discord.Embed(description="DM you on mentions while AFK?", color=0x977FD7)
        prompt_message = await ctx.send(embed=prompt_embed, view=view, ephemeral=True)
        await view.wait()
        
        if view.value is None:
            await prompt_message.edit(content="Timed out.", embed=None, view=None)
            return

        if author_id not in self.afk_cache:
            self.afk_cache[author_id] = {}
        
        afk_data = self.afk_cache[author_id]
        afk_data.update({
            'AFK': 'True',
            'reason': reason,
            'time': int(time.time()),
            'mentions': 0,
            'dm': 'True' if view.value else 'False'
        })

        await self._save_data()
        
        try:
            current_nick = ctx.author.display_name
            if not current_nick.startswith('[AFK]'):
                await ctx.author.edit(nick=f"[AFK] {current_nick}")
        except discord.Forbidden:
            await ctx.send("I couldn't change your nickname, but your AFK is set.", ephemeral=True)
        
        confirm_embed = discord.Embed(description=f"Your global AFK is set: {reason}", color=0x977FD7)
        await ctx.send(embed=confirm_embed)
        await prompt_message.delete()

async def setup(bot):
    await bot.add_cog(Afk(bot))
