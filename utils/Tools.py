import json, sys, os
from discord.ext import commands
from core import Context
import aiohttp
import discord



def DotEnv(query: str):
  return os.getenv(query)

def getConfig(guildID):
    with open("jsons/config.json", "r") as config:
        data = json.load(config)
    if str(guildID) not in data["guilds"]:
        defaultConfig = {
            "antiSpam": False,
            "antiLink": False,
            "whitelisted": [], 
            "punishment": "ban",
            "prefix": "$"
        }
        updateConfig(guildID, defaultConfig)
        return defaultConfig
    return data["guilds"][str(guildID)]


def updateConfig(guildID, data):
    with open("jsons/config.json", "r") as config:
        config = json.load(config)
    config["guilds"][str(guildID)] = data
    newdata = json.dumps(config, indent=4, ensure_ascii=False)
    with open("jsons/config.json", "w") as config:
        config.write(newdata)


def add_user_to_blacklist(user_id: int) -> None:
    with open("jsons/blacklist.json", "r") as file:
        file_data = json.load(file)
        if str(user_id) in file_data["ids"]:
            return

        file_data["ids"].append(str(user_id))
    with open("jsons/blacklist.json", "w") as file:
        json.dump(file_data, file, indent=4)


def remove_user_from_blacklist(user_id: int) -> None:
    with open("jsons/blacklist.json", "r") as file:
        file_data = json.load(file)
        file_data["ids"].remove(str(user_id))
    with open("jsons/blacklist.json", "w") as file:
        json.dump(file_data, file, indent=4)


def update_vanity(guild, code):
    with open('jsons/vanity.json', 'r') as vanity:
        vanity = json.load(vanity)
    vanity[str(guild)] = str(code)
    new = json.dumps(vanity, indent=4, ensure_ascii=False)
    with open('jsons/vanity.json', 'w') as vanity:
        vanity.write(new)


def blacklist_check():
    def predicate(ctx):
        with open("jsons/blacklist.json") as f:
            data = json.load(f)
            if str(ctx.author.id) in data["ids"]:
                return False
            return True

    return commands.check(predicate)


def premium_check():
    def predicate(ctx):
        with open("jsons/premium.json", "r") as f:
            premium_data = json.load(f)
        return ctx.guild.id in premium_data.get("premium_guilds", [])

    return commands.check(predicate)    


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)




def getbadges(userid):
    try:
        with open("jsons/badges.json", "r", encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    except FileNotFoundError:
        data = {}
    if str(userid) not in data:
        default = []
        makebadges(userid, default)
        return default
    return data[str(userid)]

def makebadges(userid, data):
    try:
        with open("jsons/badges.json", "r", encoding='utf-8') as f:
            try:
                badges = json.load(f)
            except json.JSONDecodeError:
                badges = {}
    except FileNotFoundError:
        badges = {}
    badges[str(userid)] = data
    with open("jsons/badges.json", "w", encoding='utf-8') as w:
        json.dump(badges, w, indent=4, ensure_ascii=False)




def getanti(guildid):
    with open("jsons/anti.json", "r") as config:
        data = json.load(config)
    if str(guildid) not in data["guilds"]:
        default = "off"
        updateanti(guildid, default)
        return default
    return data["guilds"][str(guildid)] 

def updateanti(guildid, data):
    with open("jsons/anti.json", "r") as config:
        config = json.load(config)
    config["guilds"][str(guildid)] = data
    newdata = json.dumps(config, indent=4, ensure_ascii=False)
    with open("jsons/anti.json", "w") as config:
        config.write(newdata)


def premium_check():
    async def predicate(ctx):
        with open("jsons/premium.json", "r") as f:
            premium_data = json.load(f)
        if ctx.guild.id in premium_data.get("premium_guilds", []):
            return True
        else:
            embed = discord.Embed(
                title="<a:premiumD:1040661976373788763> Premium Not Activated <a:premiumD:1040661976373788763>",
                description="This server does not have premium features activated.",
                color=0x977FD7
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
            embed.add_field(
                name="Join Support Server",
                value="<:Invitelink:1040661606809473046> [Join the support server](https://fusionxo.com/luka/support) for premium activation or more information. <a:pain_white_heart2:981110605178081302>"
            )
            await ctx.send(embed=embed)
            return False

    return commands.check(predicate)



def getIgnore(guildID):
    with open("jsons/ignore.json", "r") as config:
        data = json.load(config)
    if str(guildID) not in data["guilds"]:
        defaultConfig = {
            "channel": [],
            "role": None,
            "user": [],
            "excluderole": None,
            "excludeuser": [],
            "commands": []
            
            
        }
        updateignore(guildID, defaultConfig)
        return defaultConfig
    return data["guilds"][str(guildID)]


def updateignore(guildID, data):
    with open("jsons/ignore.json", "r") as config:
        config = json.load(config)
    config["guilds"][str(guildID)] = data
    newdata = json.dumps(config, indent=4, ensure_ascii=False)
    with open("jsons/ignore.json", "w") as config:
        config.write(newdata)


def ignore_check():

    def predicate(ctx):
            data = getIgnore(ctx.guild.id)
            ch = data["channel"]
            iuser = data["user"]
            irole = data["role"]
            buser = data["excludeuser"]
            brole = data["excluderole"]
            if str(ctx.author.id) in buser:
                return True            
            elif str(ctx.author.id) in iuser or str(ctx.channel.id) in ch:
                return False
            else:
                return True
            

    return commands.check(predicate)

def get_join_channels():
    con = sqlite3.connect("databases/date.db")
    sql = f"select * from joinchannel;"
    cur = con.cursor()
    cur.execute(sql)
    channels = cur.fetchall()
    con.close()
    return channels