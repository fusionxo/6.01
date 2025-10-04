from __future__ import annotations
from core import Luka



#____________ Commands ___________

#####################3
from .commands.help import Help
from .commands.general import General
from .commands.moderation import Moderation
from .commands.Anti_cmds import Security
from .commands.logging import Logging
from .commands.welcome import Welcome
from .commands.fun import Fun
from .commands.Games import Games
from .commands.extra import Extra
from .commands.owner import Owner
from .commands.Sroles import Sroles
from .commands.Autorespond import Autorespond
from .commands.listcmd import List
from .commands.starboard import Starboard
from .commands.Vcroles import VCroles
from .commands.suggestion import Suggestion
from .commands.autosnipe import AutoSnipe
from .commands.voicecmds import VoiceCmd
from .commands.soundboard import Soundboard
from .commands.blword import blword
from .commands.vanitystatus import VanityRoles
from .commands.ticket import TicketCog
from .commands.developers import Devs
from .commands.texttoemoji import TextToEmoji
from .commands.media import Media
from .commands.utilitiy import utilitiy
from.commands.jtc import Jtc
from.commands.encryption import Encryption
from.commands.autoroles import Autorole
from.commands.genai import GenAI
from.commands.Afk import Afk
from .commands.td import TD
from .commands.giveaway import Giveaway
from .commands.ignore import Ignore
from .commands.pfps import pfps
from .commands.automod import Auto
from .commands.tts import TTS
from .commands.backup import Backup
from .commands.autopfp import AutoPFP
#from .commands.aim import AIMO
from .commands.timer import TimerM
from .commands.economy import Economy
from .commands.music import Music



#____________ Events _____________
from .events.antiban import antiban
from .events.antichannel import antichannel
from .events.antiguild import antiguild
from .events.antirole import antirole
from .events.antibot import antibot
from .events.antikick import antikick
from .events.antiprune import antiprune
from .events.antiwebhook import antiwebhook
from .events.antiping import antipinginv
from .events.antiemostick import antiemostick
from .events.antintegration import antintegration
from .events.antispam import AntiSpam
from .events.autoblacklist import AutoBlacklist
from .events.antiemojid import antiemojid
from .events.antiemojiu import antiemojiu
from .events.Errors import Errors
from .events.on_guild import Guild
from .events.on_member_join import welcome_event
from .events.ready import ready




async def setup(bot: Luka):
  await bot.add_cog(Help(bot))
  await bot.add_cog(General(bot))
  await bot.add_cog(Moderation(bot))
  await bot.add_cog(Security(bot))
  await bot.add_cog(Logging(bot))
  await bot.add_cog(Welcome(bot))
  await bot.add_cog(Fun(bot))
  await bot.add_cog(Games(bot))
  await bot.add_cog(Extra(bot))
  await bot.add_cog(Owner(bot))
  await bot.add_cog(Sroles(bot))
  await bot.add_cog(Autorespond(bot))
  await bot.add_cog(List(bot))
  await bot.add_cog(Starboard(bot))
  await bot.add_cog(VCroles(bot))
  await bot.add_cog(Suggestion(bot))
  await bot.add_cog(AutoSnipe(bot))
  await bot.add_cog(VoiceCmd(bot))
  await bot.add_cog(Soundboard(bot))
  await bot.add_cog(blword(bot))
  await bot.add_cog(VanityRoles(bot))
  await bot.add_cog(TicketCog(bot))
  await bot.add_cog(Devs(bot))
  await bot.add_cog(TextToEmoji(bot))
  await bot.add_cog(Media(bot))
  await bot.add_cog(utilitiy(bot))
  await bot.add_cog(Jtc(bot))
  await bot.add_cog(Encryption(bot))
  await bot.add_cog(Autorole(bot))
  await bot.add_cog(GenAI(bot))
  await bot.add_cog(Afk(bot))
  await bot.add_cog(TD(bot))
  await bot.add_cog(Giveaway(bot))
  await bot.add_cog(Ignore(bot))
  await bot.add_cog(pfps(bot))
  await bot.add_cog(Auto(bot))
  await bot.add_cog(TTS(bot))
  await bot.add_cog(Backup(bot))
  await bot.add_cog(AutoPFP(bot))
  #await bot.add_cog(AIMO(bot))
  await bot.add_cog(TimerM(bot))
  #await bot.add_cog(ChordAI(bot))
  await bot.add_cog(Economy(bot))
  await bot.add_cog(Music(bot))



###########################events################3
  
  await bot.add_cog(antiban(bot))
  await bot.add_cog(antichannel(bot))
  await bot.add_cog(antiguild(bot))
  await bot.add_cog(antirole(bot))
  await bot.add_cog(antibot(bot))
  await bot.add_cog(antikick(bot))
  await bot.add_cog(antiprune(bot))
  await bot.add_cog(antiwebhook(bot))
  await bot.add_cog(antipinginv(bot))
  await bot.add_cog(antiemostick(bot))
  await bot.add_cog(antintegration(bot))  
  await bot.add_cog(AntiSpam(bot))
  await bot.add_cog(AutoBlacklist(bot))
  await bot.add_cog(antiemojid(bot))
  await bot.add_cog(antiemojiu(bot))
  await bot.add_cog(Guild(bot))
  await bot.add_cog(Errors(bot))
  await bot.add_cog(welcome_event(bot))