import discord
from discord.ext import commands
from pymongo import MongoClient
import asyncio
from utils import *
from utils.checks import global_check


# --- MongoDB Connection (as provided) ---
cluster = MongoClient("mongodb+srv://workforkami:DqdgZf7yCSUS9V3c@Luka.qvswi7j.mongodb.net/?retryWrites=true&w=majority")
db = cluster['welcome']
collection = db['welcomedata']

class EmbedMenuModal(discord.ui.Modal, title="Embed Builder"):
    embed_title = discord.ui.TextInput(
        label="Embed Title",
        placeholder="Enter embed title",
        required=False
    )
    embed_description = discord.ui.TextInput(
        label="Embed Description",
        style=discord.TextStyle.long,
        placeholder="Enter embed description",
        required=False
    )
    embed_color = discord.ui.TextInput(
        label="Embed Color (Hex)",
        placeholder="#FF0000",
        required=False
    )
    embed_thumbnail = discord.ui.TextInput(
        label="Thumbnail URL",
        placeholder="https://example.com/thumbnail.png",
        required=False
    )
    embed_footer = discord.ui.TextInput(
        label="Footer Text",
        placeholder="Enter footer text",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Parse the color (default if invalid)
        color_value = 0x977FD7
        if self.embed_color.value:
            try:
                hex_code = self.embed_color.value.lstrip("#")
                color_value = int(hex_code, 16)
            except ValueError:
                pass

        # Build the embed
        embed = discord.Embed(
            title=self.embed_title.value or None,
            description=self.embed_description.value or None,
            color=color_value
        )
        if self.embed_thumbnail.value:
            embed.set_thumbnail(url=self.embed_thumbnail.value)
        if self.embed_footer.value:
            embed.set_footer(text=self.embed_footer.value)

        # Convert embed to a dictionary and save to MongoDB
        embed_dict = embed.to_dict()
        guild_id = interaction.guild.id
        collection.update_one(
            {"_id": guild_id},
            {"$set": {"message": embed_dict}},
            upsert=True
        )

        # Respond with confirmation and preview
        await interaction.response.send_message(
            "Embed settings saved! Here's your preview:",
            embed=embed
        )


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def cog_check(self, ctx: commands.Context) -> bool:
        return await global_check(ctx)
        
    def help_custom(self):
		      emoji = '<:welcome:1088445113417605150>'
		      label = "Welcome"
		      description = "Shows the welcome commands."
		      return emoji, label, description

    @commands.group()
    async def __Welcome__(self, ctx: commands.Context):
        """`welcome` , `welcome enable` , `welcome  disable` , `welcome message` , `welcome emessage` , `welcome channel` , `welcome test `"""

    def get_format_kwargs(self, member):
        return {
            "user_id": member.id,
            "user_name": member.name,
            "user_mention": member.mention,
            "user_tag": str(member),
            "user_discriminator": member.discriminator,
            "user_avatar_url": member.display_avatar.url,
            "server_name": member.guild.name,
            "server_membercount": member.guild.member_count,
            "server_icon_url": member.guild.icon.url if member.guild.icon else ""
        }

    def process_embed(self, embed_data, format_kwargs):
        processed = {}
        for key, value in embed_data.items():
            if isinstance(value, str):
                try:
                    processed[key] = value.format(**format_kwargs)
                except KeyError:
                    processed[key] = value
            elif isinstance(value, dict):
                processed[key] = self.process_embed(value, format_kwargs)
            elif isinstance(value, list):
                processed[key] = [self.process_embed(item, format_kwargs) if isinstance(item, dict) else 
                                  item.format(**format_kwargs) if isinstance(item, str) else item 
                                  for item in value]
            else:
                processed[key] = value
        return processed

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        data = collection.find_one({"_id": guild_id})
    
        if data and data.get('enabled', False):
            welcome_channel = self.bot.get_channel(data['channel_id'])
            welcome_message = data['message']
    
            if not welcome_channel:
                return
    
            format_kwargs = self.get_format_kwargs(member)
    
            if isinstance(welcome_message, dict):
                processed_embed = self.process_embed(welcome_message, format_kwargs)
                embed = discord.Embed.from_dict(processed_embed)
                await welcome_channel.send(f"{member.mention}", embed=embed)
            else:
                try:
                    formatted_message = welcome_message.format(**format_kwargs)
                    await welcome_channel.send(formatted_message)
                except KeyError as e:
                    error_embed = discord.Embed(
                        title="Welcome Error",
                        description=f"Missing variable {e} in welcome message",
                        color=0xFF0000
                    )
                    await welcome_channel.send(embed=error_embed)


    @commands.hybrid_group(invoke_without_command=True,
                    help="Shows welcome commands",
                    usage="welcome",
                    aliases=["wlc"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    
    
    async def welcome(self, ctx):
        embed = discord.Embed(title="Luka | Welcome Commands", color=0x977FD7)
        embed.add_field(
            name="usage",
            value=
            "— welcome message <message>\n— welcome channel <channel>\n— welcome disable\n— welcome enable\n— welcome test",
            inline=False)
        embed.add_field(
            name="description",
            value=
            "— `welcome message` - Sets the welcome to a message\n— `welcome channel` - Sets the welcome channel\n— `welcome disable` - Disables the welcome message\n— `welcome enable` - Enables the welcome message\n— `welcome test` - Test the welcome message",
            inline=False)
        embed.add_field(
            name="permissions",
            value=
            "— `Manage Channels` - Requires you to have manage channels permissions for all commands",
            inline=False)
        embed.add_field(
            name="variables",
            value=
            "```py\n— {user_id}\n— {user_name}\n— {user_mention}\n— {user_tag}\n— {server_name}\n— {server_membercount}\n—{server_icon_url}\n—{user_discriminator}\n—{user_avatar_url}\n```",
            inline=False)
        
        await ctx.send(embed=embed)

    @welcome.command(name="enable",
                     description="Enables the welcome event",
                     usage="welcome enable",
                     aliases=["on"])
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    
    
    async def enable(self, ctx):
        guild_id = ctx.guild.id
        collection.update_one({"_id": guild_id}, {"$set": {"enabled": True}}, upsert=True)
        await ctx.send(embed=discord.Embed(
            title="Luka Welcome | Enabled",
            description="<:check:1087776909246607360> | Successfully enabled the welcome event",
            color=0x977FD7))

    @welcome.command(name="disable",
                     description="Disables the welcome event",
                     usage="welcome disable",
                     aliases=["off"])
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    
    
    async def disable(self, ctx):
        guild_id = ctx.guild.id
        collection.update_one({"_id": guild_id}, {"$set": {"enabled": False}}, upsert=True)
        await ctx.send(embed=discord.Embed(
            title="Luka Welcome | Disabled",
            description="<:check:1087776909246607360> | Successfully disabled the welcome event",
            color=0x977FD7))

    @welcome.command(name="message",
                     description="Sets the welcome message",
                     usage="welcome message <message>",
                     aliases=["msg"])
    
    
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def message(self, ctx, *, message):
        guild_id = ctx.guild.id
        collection.update_one({"_id": guild_id}, {"$set": {"message": message}}, upsert=True)
        await ctx.send(embed=discord.Embed(
            title="Message | Welcome",
            description="<:check:1087776909246607360> | Successfully set the welcome message",
            color=0x977FD7))

    @welcome.command(name="channel",
                     description="Sets the welcome channel",
                     usage="welcome channel <channel>",
                     aliases=["chan"])
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    
    
    async def channel(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        collection.update_one({"_id": guild_id}, {"$set": {"channel_id": channel.id}}, upsert=True)
        await ctx.send(embed=discord.Embed(
            title="Luka Welcome | Channel",
            description=f"<:check:1087776909246607360> | Successfully set the welcome channel to {channel.mention}",
            color=0x977FD7))

    @welcome.command(name="test", description="Tests the welcome event", usage="welcome test", aliases=["try"])
    
    
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def test(self, ctx):
        guild_id = ctx.guild.id
        data = collection.find_one({"_id": guild_id})

        if not data or 'message' not in data:
            await ctx.send("<:error:1088542929158688788> | No welcome message set.")
            return

        welcome_message = data['message']
        format_kwargs = self.get_format_kwargs(ctx.author)

        try:
            if isinstance(welcome_message, dict):
                processed_embed = self.process_embed(welcome_message, format_kwargs)
                embed = discord.Embed.from_dict(processed_embed)
                await ctx.send(ctx.author.mention, embed=embed)
            else:
                formatted = welcome_message.format(**format_kwargs)
                await ctx.send(formatted)
        except KeyError as e:
            await ctx.send(f"<:error:1088542929158688788> | Missing variable {e}")

    @welcome.command(name="emmsg", description="Interactive embed builder", usage="welcome emmsg", aliases=["emsg"])
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    
    
    async def emsg(self, ctx: commands.Context):
        """
        Opens a modal to collect embed details. Best used as a slash command (/emsg).
        """
        # Check if this was invoked as a slash command
        if ctx.interaction is None:
            # If invoked via text prefix, just let them know
            await ctx.send("Please run `/emsg` as a slash command to open the modal.")
            return

        # If slash-based, we have an interaction
        modal = EmbedMenuModal()
        await ctx.interaction.response.send_modal(modal)
        
        
        
async def setup(bot):
    await bot.add_cog(Welcome(bot))