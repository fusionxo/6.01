from threading import Thread
from flask import Flask
import os
from core.Luka import Luka
import asyncio
import time
import aiohttp
import json
import jishaku
import cogs
import psutil
import discord
from discord.ext import commands
from discord import app_commands
import traceback
from datetime import datetime
import requests
from cogs.commands.chordai import *

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

client = Luka()
tree = client.tree


class Embed(discord.ui.Modal, title='Embed Configuration'):
    tit = discord.ui.TextInput(
        label='Embed Title',
        placeholder='Embed title here',
    )

    description = discord.ui.TextInput(
        label='Embed Description',
        style=discord.TextStyle.long,
        placeholder='Embed description optional',
        required=False,
        max_length=400,
    )

    thumbnail = discord.ui.TextInput(
        label='Embed Thumbnail',
        placeholder='Embed thumbnail here optional',
        required=False,
    )

    img = discord.ui.TextInput(
        label='Embed Image',
        placeholder='Embed image here optional',
        required=False,
    )

    footer = discord.ui.TextInput(
        label='Embed footer',
        placeholder='Embed footer here optional',
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.tit.value,
                              description=self.description.value,
                              color=0x977FD7)
        if not self.thumbnail.value is None:
            embed.set_thumbnail(url=self.thumbnail.value)
        if not self.img.value is None:
            embed.set_image(url=self.img.value)
        if not self.footer.value is None:
            embed.set_footer(text=self.footer.value)
        await interaction.response.send_message(embed=embed)

    async def on_error(self, interaction: discord.Interaction,
                       error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.',
                                                ephemeral=True)

        traceback.print_tb(error.__traceback__)


@tree.command(name="embed", description="Create A Embed Using Luka")
async def _embed(interaction: discord.Interaction) -> None:
    await interaction.response.send_modal(Embed())


async def protect_vanity(guildid):
    start = time.perf_counter()
    with open('jsons/vanity.json') as idk:
        code = json.load(idk)
        if code[str(guildid)] != "":
            header = {
                "Authorization":
                "Bot token",
                "X-Audit-Log-Reason": "Luka | Anti Vanity"
            }
            async with aiohttp.ClientSession(headers=header) as session:
                jsonn = {"code": code[str(guildid)]}
                async with session.patch(
                    f"https://ptb.discord.com/api/v10/guilds/{guildid}/vanity-url",
                        json=jsonn) as response:
                    end = time.perf_counter()
                    print(f"{end - start} | {response.status}")
        else:
            return


WEBHOOK_URL = "https://discord.com/api/webhooks/1130539237255684167/8hRNLKPYwoVPhzw7ihj9O-9kreNb1x9278kLoafmY8ILowEaT0z_JtrQa7rUmHrCeni0"

@client.event
async def on_command_completion(context) -> None:
    full_command_name = context.command.qualified_name
    split = full_command_name.split(",  ")
    executed_command = str(split[0])

    embed = discord.Embed(title="Command Executed", color=0x977FD7)

    if context.guild is not None:
        embed.add_field(
            name="Command", value=f"`{executed_command}`", inline=False)
        embed.add_field(
            name="Server", value=f"`{context.guild.name}`", inline=True)
        embed.add_field(
            name="Channel", value=f"`{context.channel.name}`", inline=True)
        embed.add_field(
            name="User", value=f"`{context.author.name}`", inline=True)
        embed.add_field(name="Server ID",
                        value=f"`{context.guild.id}`", inline=True)
        embed.add_field(name="Channel ID",
                        value=f"`{context.channel.id}`", inline=True)
        embed.add_field(
            name="User ID", value=f"`{context.author.id}`", inline=True)
    else:
        embed.add_field(
            name="Command", value=f"`{executed_command}`", inline=False)
        embed.add_field(
            name="User", value=f"`{context.author.name}`", inline=True)
        embed.add_field(
            name="User ID", value=f"`{context.author.id}`", inline=True)

    embed.set_footer(
        text=f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

    data = {"embeds": [embed.to_dict()]}
    requests.post(WEBHOOK_URL, json=data)




@client.listen("on_guild_update")
async def on_vanity_update(before, after):
    if before.vanity_url_code != after.vanity_url_code:
        await protect_vanity(before.id)
    else:
        return


@client.event
async def on_ready():
    print("This Bot is Speed Of Light!")
    print(f"Logged in as: {client.user}")
    print(f"Monitoring in: {len(client.guilds)} guilds")
    print(f"Total users: {len(client.users)} users")
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)


app = Flask(__name__)


@app.route('/')
def home():
    return "Luka"


def run():
    app.run(host='127.0.0.1', port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


keep_alive()


async def main():
    async with client:
        os.system("clear")
        await client.load_extension("cogs")
        await client.load_extension("jishaku")
        await client.start("") #token
        #dev token : token
        #main token :       


if __name__ == "__main__":
    asyncio.run(main())
