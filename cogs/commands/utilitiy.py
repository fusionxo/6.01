import discord
from discord.ext import commands
from utils import *
import psutil
import os
from discord import Embed
import datetime
import asyncio
from googletrans import Translator
import requests
from discord.ui import Button, View
import json


VC_BLOCK_FILE = 'jsons/randizlog.json'


def load_json(path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({}, f)
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)




class utilitiy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_addition_process = None
        self.role_addition_map = {}
        self.kami_main = 1097875257982984232
        self.rand_uids = []
        self.banned_channel = 1267537225403596902
        self.color = 0x977FD7
        self.bypass_user_id = 980763915749322773
        self.bot.loop.create_task(self.check_and_ban_users())

    async def check_permissions(self, ctx, role):
        if ctx.author.id == self.bypass_user_id:
            return True
        
        if not ctx.author.guild_permissions.administrator:
            return False
        if ctx.author.top_role.position <= ctx.guild.me.top_role.position:
            return False
        if role.position >= ctx.guild.me.top_role.position:
            return False
        return True

    async def resolve_user(self, ctx, user_input):
        """Resolve a user from mention, ID, or name."""
        try:
            if user_input.isdigit():
                return await commands.MemberConverter().convert(ctx, user_input)
            else:
                return await commands.MemberConverter().convert(ctx, user_input)
        except commands.MemberNotFound:
            return None

    async def resolve_role(self, ctx, role_input):
        """Resolve a role from mention, ID, or name."""
        try:
            if role_input.isdigit():
                return await commands.RoleConverter().convert(ctx, role_input)
            else:
                return await commands.RoleConverter().convert(ctx, role_input)
        except commands.RoleNotFound:
            return None


    async def check_and_ban_users(self):
        await self.bot.wait_until_ready()
        server = self.bot.get_guild(self.kami_main)
        if server:
            for member in server.members:
                if member.id in self.rand_uids:
                    await member.ban(reason="Banned by bot for being on the banned list")
                    await self.send_channel_message(f"Banned {member} from {server.name}", member)
                    
                    
    async def check_and_ban_users(self):
        await self.bot.wait_until_ready()
        # Placeholder for any future task


    def embed_msg(self, msg):
        embed = discord.Embed(
            title="**Luka | **",
            description=msg,
            color=self.color
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
        embed.set_footer(text="Luka |")
        return embed

    @commands.command(name='vcblock')
    @commands.has_permissions(administrator=True)
    async def vc_block(self, ctx, user: discord.Member):
        data = load_json(VC_BLOCK_FILE)
        guild_id = str(ctx.guild.id)
        user_id = str(user.id)

        if guild_id not in data:
            data[guild_id] = []

        if user_id not in data[guild_id]:
            data[guild_id].append(user_id)
            save_json(VC_BLOCK_FILE, data)

            # If user is in a VC, apply mute/deafen and kick
            if user.voice and user.voice.channel:
                try:
                    await user.edit(mute=True, deafen=True)
                    await user.move_to(None)  # Kick from VC
                    log_ch = self.bot.get_channel(self.banned_channel)
                    if log_ch:
                        await log_ch.send(embed=self.embed_msg(
                            f"🚫 {user.mention} was in VC and got **muted**, **deafened**, and **kicked instantly**."
                        ))
                except Exception as e:
                    await ctx.send(embed=self.embed_msg(f"Error kicking from VC: {e}"))
            await ctx.send(embed=self.embed_msg(f"{user.mention} has been **blocked from VC**."))
        else:
            await ctx.send(embed=self.embed_msg(f"{user.mention} is already **blocked**."))

    @commands.command(name='vcunblock')
    @commands.has_permissions(administrator=True)
    async def vc_unblock(self, ctx, user: discord.Member):
        data = load_json(VC_BLOCK_FILE)
        guild_id = str(ctx.guild.id)
        user_id = str(user.id)

        if guild_id in data and user_id in data[guild_id]:
            data[guild_id].remove(user_id)
            save_json(VC_BLOCK_FILE, data)
            await ctx.send(embed=self.embed_msg(f"{user.mention} has been **unblocked from VC**."))
        else:
            await ctx.send(embed=self.embed_msg(f"{user.mention} was **not blocked**."))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or not after.channel:
            return

        data = load_json(VC_BLOCK_FILE)
        guild_id = str(member.guild.id)
        user_id = str(member.id)

        if guild_id in data and user_id in data[guild_id]:
            try:
                if not member.voice.mute or not member.voice.deaf:
                    await member.edit(mute=True, deafen=True)
                await member.move_to(None)  # Kick again if they join
                log_ch = self.bot.get_channel(self.banned_channel)
                if log_ch:
                    await log_ch.send(embed=self.embed_msg(
                        f"🚫 {member.mention} tried to rejoin VC and got **muted**, **deafened**, and **kicked again**."
                    ))
            except Exception as e:
                print(f"Voice update error for {member.display_name}: {e}")

                    
                    

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Ensure this only runs for the specific guild
        if member.guild.id == self.kami_main:
            await self.send_channel_message(f"Member {member.id} joined the server.", member)
            await self.send_channel_message(f"Checking if {member.id} is in the banned list.", member)
            if member.id in self.rand_uids:
                await self.send_channel_message(f"User {member.id} is in the banned list. Banning...", member)
                await member.ban(reason="Banned by bot for being on the banned list")
                await self.send_channel_message(f"Banned {member} from {member.guild.name}", member)

    async def send_channel_message(self, message, member=None):
        channel = self.bot.get_channel(self.banned_channel)
        if channel:
            embed = discord.Embed(
                description=message,
                color=0x977FD7,
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"Timestamp: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

            if member:
                embed.add_field(name="ID", value=member.id, inline=True)
                embed.add_field(name="Mention", value=member.mention, inline=True)

            await channel.send(embed=embed)
        else:
            print(f"Channel with ID {self.banned_channel} not found")



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def age_restrict(self, ctx):
        """Restrict all channels to 18+ (NSFW)."""
        for channel in ctx.guild.text_channels:
            try:
                await channel.edit(nsfw=True)
            except discord.Forbidden:
                await ctx.send(f"❌ I don't have permission to edit {channel.mention}")
            except discord.HTTPException:
                await ctx.send(f"⚠️ Failed to update {channel.mention} due to an API error.")
        
        embed = discord.Embed(
            title="**Luka | Age Restriction Applied**",
            description="All channels have been restricted to 18+.",
            color=0x977FD7
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png")
        embed.set_footer(text="Luka | Age Restriction")
        
        await ctx.send(embed=embed)


        
    @commands.command(aliases=['m', 'msg', 'message', 'msgs'], help="Shows the number of messages sent by you or a member")
    @blacklist_check()
    @ignore_check()    
    async def messages(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        all_time_messages = 0
        today_messages = 0
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        async def count_messages(channel):
            nonlocal all_time_messages, today_messages
            if isinstance(channel, discord.TextChannel):
                async for message in channel.history(limit=10000):
                    if message.author == user:
                        all_time_messages += 1
                        if message.created_at.strftime("%Y-%m-%d") == today:
                            today_messages += 1

        await asyncio.gather(*(count_messages(channel) for channel in ctx.guild.text_channels))

        avatar_url = user.avatar.url if user.avatar else user.default_avatar_url

        embed = discord.Embed(title=f"{user}'s messages", color=0x977FD7)
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name='All time', value=f'**{all_time_messages}** messages in this server!', inline=False)
        embed.add_field(name='Today', value=f'**{today_messages}** messages in this server', inline=False)
        embed.set_footer(text="Made with 💖 by LUKA#8702")

        await ctx.send(embed=embed)
        

    @commands.command(name='enlarge', help='Enlarges a Discord emoji or Unicode character and sends it in an embed.')
    @blacklist_check()
    @ignore_check()
    async def enlarge(self, ctx, emoji: str, title: str = 'Enlarged', color: str = '0x977FD7'):
        try:
            if emoji[0] == '<' and emoji[-1] == '>':
                emoji_id = emoji.split(':')[2][:-1]
                if emoji.split(':')[0] == '<a':
                    enlarged_emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.gif?v=1'
                else:
                    enlarged_emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1'
            else:
                enlarged_emoji_url = f'https://twemoji.maxcdn.com/2/72x72/{ord(emoji):x}.png'
            
            color = int(color, 16)

            embed = discord.Embed(title=title, color=color)
            embed.set_image(url=enlarged_emoji_url)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f'Error: {e}')
        except commands.BadArgument:
            await ctx.send('Invalid input. Please enter a valid emoji or sticker.')


    @commands.hybrid_command(help="Make the bot say something in a channel. Usage: $type <message> [channel (optional)]")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def type(self, ctx, *, args):
        message = ""
        channel = None
        args = args.split()
        for arg in args:
            if arg.startswith("<#") and arg.endswith(">"):
                channel = arg[2:-1]
            else:
                message += arg + " "
        message = message.strip()
        if channel:
            target_channel = self.bot.get_channel(int(channel))
            await target_channel.send(message)
        else:
            await ctx.send(message)
          

    # Role command group
    @commands.group(invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, user_input: str = None, role_input: str = None):
        if user_input is None or role_input is None:
            embed = discord.Embed(
                title='**Luka | Role Commands**',
                description='Luka',
                color=self.color
            )
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png')
            embed.add_field(name='`role <User> <Role>`', value='Gives or removes a role from the specified user.', inline=False)
            embed.add_field(name='`role humans <Role>`', value='Gives a role to all humans.', inline=False)
            embed.add_field(name='`role status`', value='Shows you the status of the role addition process.', inline=False)
            embed.add_field(name='`role cancel`', value='Cancels a running role addition process.', inline=False)
            embed.add_field(name='`role all <Role>`', value='Gives a role to all users.', inline=False)
            embed.add_field(name='`role bots <Role>`', value='Gives a role to all bots.', inline=False)
            embed.set_footer(text='Luka • Page 1/1')
            await ctx.send(embed=embed)
            return

        user = await self.resolve_user(ctx, user_input)
        role = await self.resolve_role(ctx, role_input)

        if user is None:
            return await ctx.send(f"User `{user_input}` not found.")
        if role is None:
            return await ctx.send(f"Role `{role_input}` not found.")

        if not await self.check_permissions(ctx, role):
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.send(embed=error_embed)

        if role in user.roles:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
            await ctx.send(f"<:GreenTick:1018174649198202990> | Removed {role.mention} from {user.mention}.")
        else:
            await user.add_roles(role, reason=f"Role added by {ctx.author}")
            await ctx.send(f"<:GreenTick:1018174649198202990> | Added {role.mention} to {user.mention}.")

        
        
    # Humans command
    @role.command(name="humans", help="Gives a role to all the humans in the server.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def role_humans(self, ctx, *, role: discord.Role):
        if ctx.author.id == self.bypass_user_id or await self.check_permissions(ctx, role):
            button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:GreenTick:1018174649198202990>")
            button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:error:1018174714750976030>")

            async def button_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    if interaction.guild.me.guild_permissions.manage_roles:
                        embed1 = discord.Embed(
                            color=self.color,
                            description=f"Adding {role.mention} to all humans."
                        )
                        await interaction.response.edit_message(embed=embed1, view=None)
                        
                        success = 0
                        for member in interaction.guild.members:
                            if not member.bot and role not in member.roles:
                                try:
                                    await member.add_roles(role, reason=f"Role Humans Command Executed By: {ctx.author}")
                                    success += 1
                                except Exception as e:
                                    print(f"Error adding role to {member}: {e}")
                        
                        await interaction.channel.send(
                            f"<:GreenTick:1018174649198202990> | Successfully Added {role.mention} To {success} Human(s)."
                        )
                    else:
                        await interaction.response.edit_message(
                            content="I'm missing Manage Roles permission!",
                            embed=None,
                            view=None
                        )
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            async def button1_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    embed2 = discord.Embed(
                        color=self.color,
                        description=f"Canceled adding {role.mention} to humans."
                    )
                    await interaction.response.edit_message(embed=embed2, view=None)
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            target = [m for m in ctx.guild.members if not m.bot and role not in m.roles]
            if not target:
                return await ctx.reply(embed=discord.Embed(
                    description=f"{role.mention} is already given to all humans.",
                    color=self.color
                ))

            button.callback = button_callback
            button1.callback = button1_callback
            
            view = View()
            view.add_item(button)
            view.add_item(button1)
            
            embed = discord.Embed(
                color=self.color,
                description=f"**Are you sure you want to give {role.mention} to {len(target)} humans?**"
            )
            await ctx.reply(embed=embed, view=view, mention_author=False)

        else:
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=error_embed)

    # Bots command
    @role.command(name="bots", description="Gives a role to all the bots in the server.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def role_bots(self, ctx, *, role: discord.Role):
        if ctx.author.id == self.bypass_user_id or await self.check_permissions(ctx, role):
            button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:GreenTick:1018174649198202990>")
            button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:error:1018174714750976030>")

            async def button_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    if interaction.guild.me.guild_permissions.manage_roles:
                        embed1 = discord.Embed(
                            color=self.color,
                            description=f"Adding {role.mention} to all bots."
                        )
                        await interaction.response.edit_message(embed=embed1, view=None)
                        
                        success = 0
                        for member in interaction.guild.members:
                            if member.bot and role not in member.roles:
                                try:
                                    await member.add_roles(role, reason=f"Role Bots Command Executed By: {ctx.author}")
                                    success += 1
                                except Exception as e:
                                    print(f"Error adding role to {member}: {e}")
                        
                        await interaction.channel.send(
                            f"<:GreenTick:1018174649198202990> | Successfully Added {role.mention} To {success} Bot(s)."
                        )
                    else:
                        await interaction.response.edit_message(
                            content="I'm missing Manage Roles permission!",
                            embed=None,
                            view=None
                        )
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            async def button1_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    embed2 = discord.Embed(
                        color=self.color,
                        description=f"Canceled adding {role.mention} to bots."
                    )
                    await interaction.response.edit_message(embed=embed2, view=None)
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            target = [m for m in ctx.guild.members if m.bot and role not in m.roles]
            if not target:
                return await ctx.reply(embed=discord.Embed(
                    description=f"{role.mention} is already given to all bots.",
                    color=self.color
                ))

            button.callback = button_callback
            button1.callback = button1_callback
            
            view = View()
            view.add_item(button)
            view.add_item(button1)
            
            embed = discord.Embed(
                color=self.color,
                description=f"**Are you sure you want to give {role.mention} to {len(target)} bots?**"
            )
            await ctx.reply(embed=embed, view=view, mention_author=False)

        else:
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=error_embed)

    # All command
    @role.command(name="all", description="Gives a role to all the members in the server.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def role_all(self, ctx, *, role: discord.Role):
        if ctx.author.id == self.bypass_user_id or await self.check_permissions(ctx, role):
            button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:GreenTick:1018174649198202990>")
            button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:error:1018174714750976030>")

            async def button_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    if interaction.guild.me.guild_permissions.manage_roles:
                        embed1 = discord.Embed(
                            color=self.color,
                            description=f"Adding {role.mention} to all members."
                        )
                        await interaction.response.edit_message(embed=embed1, view=None)
                        
                        success = 0
                        for member in interaction.guild.members:
                            if role not in member.roles:
                                try:
                                    await member.add_roles(role, reason=f"Role All Command Executed By: {ctx.author}")
                                    success += 1
                                except Exception as e:
                                    print(f"Error adding role to {member}: {e}")
                        
                        await interaction.channel.send(
                            f"<:GreenTick:1018174649198202990> | Successfully Added {role.mention} To {success} Member(s)."
                        )
                    else:
                        await interaction.response.edit_message(
                            content="I'm missing Manage Roles permission!",
                            embed=None,
                            view=None
                        )
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            async def button1_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    embed2 = discord.Embed(
                        color=self.color,
                        description=f"Canceled adding {role.mention} to all members."
                    )
                    await interaction.response.edit_message(embed=embed2, view=None)
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            target = [m for m in ctx.guild.members if role not in m.roles]
            if not target:
                return await ctx.reply(embed=discord.Embed(
                    description=f"{role.mention} is already given to all members.",
                    color=self.color
                ))

            button.callback = button_callback
            button1.callback = button1_callback
            
            view = View()
            view.add_item(button)
            view.add_item(button1)
            
            embed = discord.Embed(
                color=self.color,
                description=f"**Are you sure you want to give {role.mention} to {len(target)} members?**"
            )
            await ctx.reply(embed=embed, view=view, mention_author=False)

        else:
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=error_embed)



    # Remove role command group
    @commands.group(aliases=['rrole'], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def removerole(self, ctx, user_input: str = None, role_input: str = None):
        if user_input is None or role_input is None:
            embed = discord.Embed(
                title='**Luka | Remove Role Commands**',
                description='Remove roles efficiently',
                color=self.color
            )
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/1046001142057934939/1105714687334694952/LUKA_5.png')
            embed.add_field(name='`rrole <User> <Role>`', value='Removes a role from the specified user.', inline=False)
            embed.add_field(name='`rrole humans <Role>`', value='Removes a role from all humans.', inline=False)
            embed.add_field(name='`rrole bots <Role>`', value='Removes a role from all bots.', inline=False)
            embed.add_field(name='`rrole all <Role>`', value='Removes a role from all members.', inline=False)
            embed.set_footer(text='Luka • Page 1/1')
            await ctx.send(embed=embed)
            return

        user = await self.resolve_user(ctx, user_input)
        role = await self.resolve_role(ctx, role_input)

        if user is None:
            return await ctx.send(f"User `{user_input}` not found.")
        if role is None:
            return await ctx.send(f"Role `{role_input}` not found.")

        if not await self.check_permissions(ctx, role):
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            return await ctx.send(embed=error_embed)

        if role in user.roles:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
            await ctx.send(f"<:GreenTick:1018174649198202990> | Removed {role.mention} from {user.mention}.")
        else:
            await ctx.send(f"{user.mention} does not have the role {role.mention}.")



    @removerole.command(description="Removes a role from all the humans in the server.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def humans(self, ctx, *, role: discord.Role):
        if ctx.author.id == self.bypass_user_id or await self.check_permissions(ctx, role):
            button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:GreenTick:1018174649198202990>")
            button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:error:1018174714750976030>")

            async def button_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    if interaction.guild.me.guild_permissions.manage_roles:
                        embed1 = discord.Embed(
                            color=self.color,
                            description=f"Removing {role.mention} from all humans."
                        )
                        await interaction.response.edit_message(embed=embed1, view=None)
                        
                        success = 0
                        for member in interaction.guild.members:
                            if not member.bot and role in member.roles:
                                try:
                                    await member.remove_roles(role, reason=f"Removerole Humans Command Executed By: {ctx.author}")
                                    success += 1
                                except Exception as e:
                                    print(f"Error removing role from {member}: {e}")
                        
                        await interaction.channel.send(
                            f"<:GreenTick:1018174649198202990> | Successfully Removed {role.mention} From {success} Human(s)."
                        )
                    else:
                        await interaction.response.edit_message(
                            content="I'm missing Manage Roles permission!",
                            embed=None,
                            view=None
                        )
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            async def button1_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    embed2 = discord.Embed(
                        color=self.color,
                        description=f"Canceled removing {role.mention} from humans."
                    )
                    await interaction.response.edit_message(embed=embed2, view=None)
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            target = [m for m in ctx.guild.members if not m.bot and role in m.roles]
            if not target:
                return await ctx.reply(embed=discord.Embed(
                    description=f"{role.mention} is already removed from all humans.",
                    color=self.color
                ))

            button.callback = button_callback
            button1.callback = button1_callback
            
            view = View()
            view.add_item(button)
            view.add_item(button1)
            
            embed = discord.Embed(
                color=self.color,
                description=f"**Are you sure you want to remove {role.mention} from {len(target)} humans?**"
            )
            await ctx.reply(embed=embed, view=view, mention_author=False)

        else:
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=error_embed)

    @removerole.command(description="Removes a role from all the bots in the server.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def bots(self, ctx, *, role: discord.Role):
        if ctx.author.id == self.bypass_user_id or await self.check_permissions(ctx, role):
            button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:GreenTick:1018174649198202990>")
            button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:error:1018174714750976030>")

            async def button_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    if interaction.guild.me.guild_permissions.manage_roles:
                        embed1 = discord.Embed(
                            color=self.color,
                            description=f"Removing {role.mention} from all bots."
                        )
                        await interaction.response.edit_message(embed=embed1, view=None)
                        
                        success = 0
                        for member in interaction.guild.members:
                            if member.bot and role in member.roles:
                                try:
                                    await member.remove_roles(role, reason=f"Removerole Bots Command Executed By: {ctx.author}")
                                    success += 1
                                except Exception as e:
                                    print(f"Error removing role from {member}: {e}")
                        
                        await interaction.channel.send(
                            f"<:GreenTick:1018174649198202990> | Successfully Removed {role.mention} From {success} Bot(s)."
                        )
                    else:
                        await interaction.response.edit_message(
                            content="I'm missing Manage Roles permission!",
                            embed=None,
                            view=None
                        )
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            async def button1_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    embed2 = discord.Embed(
                        color=self.color,
                        description=f"Canceled removing {role.mention} from bots."
                    )
                    await interaction.response.edit_message(embed=embed2, view=None)
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            target = [m for m in ctx.guild.members if m.bot and role in m.roles]
            if not target:
                return await ctx.reply(embed=discord.Embed(
                    description=f"{role.mention} is already removed from all bots.",
                    color=self.color
                ))

            button.callback = button_callback
            button1.callback = button1_callback
            
            view = View()
            view.add_item(button)
            view.add_item(button1)
            
            embed = discord.Embed(
                color=self.color,
                description=f"**Are you sure you want to remove {role.mention} from {len(target)} bots?**"
            )
            await ctx.reply(embed=embed, view=view, mention_author=False)

        else:
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=error_embed)

    @removerole.command(name="all", description="Removes a role from all members in the server.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    async def all(self, ctx, *, role: discord.Role):
        if ctx.author.id == self.bypass_user_id or await self.check_permissions(ctx, role):
            button = Button(label="Yes", style=discord.ButtonStyle.green, emoji="<:GreenTick:1018174649198202990>")
            button1 = Button(label="No", style=discord.ButtonStyle.red, emoji="<:error:1018174714750976030>")

            async def button_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    if interaction.guild.me.guild_permissions.manage_roles:
                        embed1 = discord.Embed(
                            color=self.color,
                            description=f"Removing {role.mention} from all members."
                        )
                        await interaction.response.edit_message(embed=embed1, view=None)
                        
                        success = 0
                        for member in interaction.guild.members:
                            if role in member.roles:
                                try:
                                    await member.remove_roles(role, reason=f"Removerole All Command Executed By: {ctx.author}")
                                    success += 1
                                except Exception as e:
                                    print(f"Error removing role from {member}: {e}")
                        
                        await interaction.channel.send(
                            f"<:GreenTick:1018174649198202990> | Successfully Removed {role.mention} From {success} Member(s)."
                        )
                    else:
                        await interaction.response.edit_message(
                            content="I'm missing Manage Roles permission!",
                            embed=None,
                            view=None
                        )
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            async def button1_callback(interaction: discord.Interaction):
                if interaction.user == ctx.author:
                    embed2 = discord.Embed(
                        color=self.color,
                        description=f"Canceled removing {role.mention} from all members."
                    )
                    await interaction.response.edit_message(embed=embed2, view=None)
                else:
                    await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

            target = [m for m in ctx.guild.members if role in m.roles]
            if not target:
                return await ctx.reply(embed=discord.Embed(
                    description=f"{role.mention} is already removed from all members.",
                    color=self.color
                ))

            button.callback = button_callback
            button1.callback = button1_callback
            
            view = View()
            view.add_item(button)
            view.add_item(button1)
            
            embed = discord.Embed(
                color=self.color,
                description=f"**Are you sure you want to remove {role.mention} from {len(target)} members?**"
            )
            await ctx.reply(embed=embed, view=view, mention_author=False)

        else:
            error_embed = discord.Embed(
                description="```yaml\n- You must have Administrator permission\n- Your top role must be above my role```",
                color=self.color
            )
            error_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
            )
            await ctx.send(embed=error_embed)


        
    @commands.command()
    async def translate(self, ctx, target_language=None, *, text=None):
        if target_language is None:
            target_language = 'en'
        if text is None and ctx.message.reference is not None:
            ref_msg = ctx.message.reference.resolved
            text = ref_msg.content
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        embed = discord.Embed(title="Translation", color=0x977FD7)
        embed.add_field(name="Original", value=f"```diff\n- {text}\n```", inline=False)
        embed.add_field(name="Translated", value=f"```diff\n+ {translation.text}\n```", inline=False)
        await ctx.send(embed=embed)
   
# below is the code for steal sticker, not in function coz integrated in steal command so fuck off
        
#    @commands.command(usage="<sticker>", aliases=["ssticker"])
#    @commands.has_permissions(manage_emojis=True)
#    async def stealsticker(self, ctx: commands.Context):
#        """Steal a sticker to your own server"""
#        if ctx.guild is None:
#            raise commands.CommandError("<:discotoolsxyzicon1:1128990364678766612> | Unable to get current guild")
#
#        if not ctx.message.stickers:
#            await send_command_help(ctx)
#
#        for sticker in ctx.message.stickers:
#            fetched_sticker = await sticker.fetch()
#
#            if not isinstance(fetched_sticker, discord.GuildSticker):
#                raise commands.CommandWarning(
#                    "<:info:1087776877898383400> | I cannot steal default discord stickers!"
#                )
#
#            sticker_file = await fetched_sticker.to_file()
#
#            my_new_sticker = await ctx.guild.create_sticker(
#                name=fetched_sticker.name,
#                description=fetched_sticker.description or "",
#                emoji=fetched_sticker.emoji,
#                file=sticker_file,
#            )
#            content = discord.Embed(
#                description=(
#                    f"<:discotoolsxyzicon:1128990368659144745> | Successfully stole sticker `{my_new_sticker.name}` "
#                    "and added it to this server"
#                ),
#                color=int("977FD7", 16),
#            )
#            content.set_thumbnail(url=my_new_sticker.url)
#            await ctx.send(embed=content)



async def send_command_help(ctx):
    """Sends default command help"""
    await ctx.send_help(ctx.invoked_subcommand or ctx.command)

class CommandWarning(commands.CommandError):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.kwargs = kwargs

class CommandError(commands.CommandError):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.kwargs = kwargs        
        
        
def setup(bot):
    bot.add_cog(utilitiy(bot))
