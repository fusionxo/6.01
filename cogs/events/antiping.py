import os
import discord
from discord.ext import commands
import requests
import sys
from utils.Tools import getConfig, add_user_to_blacklist, getanti
import setuptools
from itertools import cycle
from collections import Counter
import threading
import datetime
import logging
from core import Luka, Cog
import time
import asyncio
import aiohttp
import tasksio
from discord.ui import View, Button
import json
from discord.ext import tasks
import random

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
    datefmt="%H:%M:%S",
)

proxies = open('proxies.txt').read().split('\n')
proxs = cycle(proxies)
proxies = {"http": 'http://' + next(proxs)}


class antipinginv(Cog):
    def __init__(self, client: Luka):
        self.client = client
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)
        print("Cog Loaded: Antipinginv")

    @commands.Cog.listener()
    async def on_message(self, message):
        button = Button(label="Invite", url="https://fusionxo.com/luka/invite")
        button1 = Button(label="Support", url="https://fusionxo.com/luka/support")
        try:
            with open("jsons/blacklist.json", "r") as f:
                data2 = json.load(f)
                Luka = '<@1040194948496109569>'
                try:
                    data = getConfig(message.guild.id)
                    anti = getanti(message.guild.id)
                    prefix = data["prefix"]
                    wled = data["whitelisted"]
                    punishment = data["punishment"]
                except Exception:
                    pass
                guild = message.guild

                if message.mention_everyone or message.mention_here:
                    if str(message.author.id) == str(guild.owner.id):
                        return  # Ignore guild owner mentions
                    elif str(message.author.id) in wled or anti == "off":
                        return
                    else:
                        # Hide the channel
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=False)
                        }
                        original_overwrites = message.channel.overwrites
                        await message.channel.edit(overwrites=overwrites)

                        await message.delete()  # Delete the message

                        # Unhide the channel
                        await message.channel.edit(overwrites=original_overwrites)

                        if punishment == "ban":
                            await message.guild.ban(message.author, reason="Mentioning Everyone/Here | Not Whitelisted")
                        elif punishment == "kick":
                            await message.guild.kick(message.author, reason="Mentioning Everyone/Here | Not Whitelisted")
                        elif punishment == "none":
                            return

                elif message.content == Luka or message.content == "<@!1077336734863466597>":
                    if str(message.author.id) in data2["ids"]:
                        embed = discord.Embed(title="<:wrong:1040661608919220415> Blacklisted",
                                              description="You Are Blacklisted From Using My Commands.\nIf You Think That It Is A Mistake, You Can Appeal In Our Support Server By Clicking [here]( https://bit.ly/luka-support)")
                        await message.reply(embed=embed, mention_author=False)
                    else:
                        embed = discord.Embed(
                            description=f"""Hello there! <a:cutieeheart:1017407063598575646> I'm **Luka**!

    To get help, just type in `{prefix}help`. <:LUKA5:1093892855950491750>

    And if you need additional assistance, feel free to join us on the PaiN ARMY Discord server by clicking on this link:  https://bit.ly/luka-support. We're always happy to help you out with anything you need! <a:dil:1045290487654907944>""",
                            color=0x977FD7)
                        view = View()
                        view.add_item(button)
                        view.add_item(button1)
                        await message.reply(f"Hey..!! {message.author.mention}", embed=embed, mention_author=True,
                                            view=view)
                else:
                    return
        except Exception as error:
            if isinstance(error, discord.Forbidden):
                return
