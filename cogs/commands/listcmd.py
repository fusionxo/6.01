import discord
from discord.ext import commands
import reactionmenu
from reactionmenu import ViewMenu, ViewButton
#pencho
async def boost_lis(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(listxd) > 1:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i].id in sent:
          count+=1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description+=f"`[{actualcount}]` | {your_list[i]} [{your_list[i].mention}] - <t:{round(your_list[i].premium_since.timestamp())}:R>\n"
          sent.append(your_list[i].id)
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)


async def boost_liss(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(listxd) > 1:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i].id in sent:
          count+=1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description+=f"`[{actualcount}]` | {your_list} `lnd`\n"
          sent.append(your_list[i].id)
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)

async def rolis(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(listxd) > 1:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i].id in sent:
          count+=1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description+=f"`[{actualcount}]` | {your_list[i].mention} `[{your_list[i].id}]` - {len(your_list[i].members)} members\n"
          sent.append(your_list[i].id)
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)


async def lister_bn(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(listxd) > 1:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i].user.id in sent:
          count+=1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description+=f"`[{actualcount}]` | {your_list[i].user} [{your_list[i].user.id}]\n"
          sent.append(your_list[i].user.id)
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)

        
async def working_lister(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  idkh=True
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if idkh:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i].id in sent:
          count+=1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description+=f"`[{actualcount}]` | {your_list[i]} [<@{your_list[i].id}>]\n"
          sent.append(your_list[i].id)
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)

async def working_listerr(ctx, color, listxd, *, title):
  embed_array = []
  t = title
  clr = color
  sent = []
  your_list = listxd
  count = 0
  idkh=True
  embed = discord.Embed(color=clr, description="", title=t)
  embed.set_footer(icon_url=ctx.bot.user.avatar)
  if idkh:
    for i in range(len(listxd)):
      for i__ in range(10):
        if not your_list[i].id in sent:
          count+=1
          if str(count).endswith("0") or len(str(count)) != 1:
            actualcount = str(count)
          else:
            actualcount = f"0{count}"
          embed.description+=f"`[{actualcount}]` | {your_list[i]} `{your_list[i]}`\n"
          sent.append(your_list[i].id)
      if str(count).endswith("0") or str(count) == str(len(your_list)):
        embed_array.append(embed)
        embed = discord.Embed(color=clr, description="", title=t)
        embed.set_footer(icon_url=ctx.bot.user.avatar)
  
  if len(embed_array) == 0:
    embed_array.append(embed)
  pag = PaginationViewWallah(embed_array, ctx)
  if len(embed_array) == 1:
    await pag.start(ctx, True)
  else:
    await pag.start(ctx)

class PaginationViewWallah:
  def __init__(self, embed_list, ctx):
    self.elist = embed_list
    self.context = ctx

  def disable_button(self, menu):
    tax = str(menu.message.embeds[0].footer.text).replace(" ", "").replace("Page", "")
    num = int(tax[0])
    if num == 1:
      fis=menu.get_button("2", search_by="id")
      bax = menu.get_button("1", search_by="id")
      
      

  def enable_button(self, menu):
    tax = str(menu.message.embeds[0].footer.text).replace(" ", "").replace("Page", "")
    num = int(tax[0])
    if num != 1:
      fis=menu.get_button("2", search_by="id")
      bax = menu.get_button("1", search_by="id")
      print(bax)
      
    
  async def dis_button(self, menu):
    self.disable_button(menu)

  async def ene_button(self, menu):
    self.ene_button(menu)


  
  async def start(self, ctx, disxd=False):
    style = f"{ctx.bot.user.name} • Page $/&"
    menu = ViewMenu(ctx, menu_type=ViewMenu.TypeEmbed, style=style)
    for xem in self.elist:
      menu.add_page(xem)
    lax = ViewButton(style=discord.ButtonStyle.secondary, label=None,emoji='⏪', custom_id=ViewButton.ID_GO_TO_FIRST_PAGE)
    menu.add_button(lax)
    bax = ViewButton(style=discord.ButtonStyle.secondary, label=None,emoji='◀️', custom_id=ViewButton.ID_PREVIOUS_PAGE)
    menu.add_button(bax)
    bax2 = ViewButton(style=discord.ButtonStyle.secondary, label=None,emoji='⏹️', custom_id=ViewButton.ID_END_SESSION)
    menu.add_button(bax2)
    bax3 = ViewButton(style=discord.ButtonStyle.secondary, label=None,emoji='▶️', custom_id=ViewButton.ID_NEXT_PAGE)
    menu.add_button(bax3)
    sax = ViewButton(style=discord.ButtonStyle.secondary, label=None,emoji='⏩', custom_id=ViewButton.ID_GO_TO_LAST_PAGE)
    menu.add_button(sax)
    if disxd:
      menu.disable_all_buttons()
    menu.disable_button(lax)
    menu.disable_button(bax)
    async def all_in_one_xd(payload):
      
      newmsg = await ctx.channel.fetch_message(menu.message.id)
      tax = str(newmsg.embeds[0].footer.text).replace(f"{ctx.bot.user.name}","").replace(" ", "").replace("Page", "").replace("•","")
      saxl = tax.split("/")
      num = int(saxl[0])
      numw = int(saxl[1])
      if num == 1:
        menu.disable_button(lax)
        menu.disable_button(bax)
      else:
        menu.enable_button(lax)
        menu.enable_button(bax)
      if num == numw:
        menu.disable_button(bax3)
        menu.disable_button(sax)
      else:
        menu.enable_button(bax3)
        menu.enable_button(sax)
      await menu.refresh_menu_items()
    menu.set_relay(all_in_one_xd)
    await menu.start()

class List(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = []
      
    @commands.hybrid_group(name="list")
    async def list(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("You need to specify a command.")

    @list.command(name="boost", aliases=["boosters", "booster", "bst", "boosted", "bsted", "bost"],description="See a list of boosters in the server")
    async def boost(self, ctx):
      
      l = []
      ok = {}
      for member in ctx.guild.premium_subscribers:
        wz = sum(m.premium_since < member.premium_since for m in ctx.guild.premium_subscribers if m.premium_since is not None)
        ok[str(wz)] = str(member.id)
      for i in range(len(ctx.guild.premium_subscribers)):
        sure = ok.get(str(i))
        l.append(ctx.guild.get_member(int(sure)))
      if l == []:
        return await ctx.send("No booster found in this server :( .")
      await boost_lis(ctx=ctx, listxd=l, color=0x977FD7, title=f"List of Boosters in {ctx.guild.name} - {int(len(l))}")

    @list.command(description="See join position.", name="joinpos", aliases=["joinposi", "joinposition"])
    async def joinpos(self, ctx):
      
      l = []
      ok = {}
      for member in ctx.guild.members:
        wz = sum(m.joined_at < member.joined_at for m in ctx.guild.members if m.joined_at is not None)
        ok[str(wz)] = str(member.id)
      for i in range(len(ctx.guild.members)):
        sure = ok.get(str(i))
        l.append(ctx.guild.get_member(int(sure)))
      await working_lister(ctx=ctx, listxd=l, color=0x977FD7, title=f"List of Join Position in {ctx.guild.name} - {int(len(l))}")

    @list.command(description="See members without any role.", name="noroles", aliases=["noroless", "norole"])
    async def noroles(self, ctx):
      
      l = []
      for member in ctx.guild.members:
        if len(member.roles) == 0:
          l.append(member)
      if l == []:
        return await ctx.send("Bruh, there are no members without any role.")
      await working_lister(ctx=ctx, listxd=l, color=0x977FD7, title=f"List of users without any role - {int(len(l))}")


    @list.command(description="Get a list of all emojis in server.", name="emojis", aliases=["emo", "emoji"])
    async def emojis(self, ctx):
      a = len(ctx.guild.emojis)
      l = []
      await working_listerr(ctx=ctx, listxd=ctx.guild.emojis, color=0x977FD7, title=f"List of Emojis in {ctx.guild.name} -  {a}")
      
    @list.command(name="bots",aliases=["bot"],description="Get a list of all bots in a server")
    async def bots(self, ctx):
      loda = []
      for member in ctx.guild.members:
        if member.bot:
          loda.append(member)
      if loda == []:
        return await ctx.send("No Bots Found")
      await working_lister(listxd=loda, color=0x977FD7, title=f"Bots in {ctx.guild.name} - {int(len(loda))}", ctx=ctx)

    @list.command(name="admins",aliases=["admin","administrator","administration"],description="Get a list of all admins of a server")
    async def admins(self, ctx):
      loda = []
      for member in ctx.guild.members:
        if member.guild_permissions.administrator:
          loda.append(member)
      if loda == []:
        return await ctx.send("Cannot find any admin in this server.")
      await working_lister(listxd=loda, color=0x977FD7, title=f"Admins in {ctx.guild.name} - {int(len(loda))}", ctx=ctx)

    @list.command(name="mods",aliases=["mod","moderator"],description="Get a list of all mods of a server")
    async def mods(self, ctx):
      loda = []
      for member in ctx.guild.members:
        if member.guild_permissions.manage_guild or member.guild_permissions.manage_messages or member.guild_permissions.manage_channels or member.guild_permissions.manage_nicknames or member.guild_permissions.manage_roles or member.guild_permissions.manage_emojis_and_stickers or member.guild_permissions.manage_emojis or member.guild_permissions.moderate_members:
          if not member.guild_permissions.administrator:
            loda.append(member)
      if loda == []:
        return await ctx.send("Cannot find any mod in this server. (Admins are not included)")
      await working_lister(listxd=loda, color=0x977FD7, title=f"Mods in {ctx.guild.name} - {int(len(loda))}", ctx=ctx)

    @list.command(name="early",aliases=["earlybadge","earlysupporter"],description="Get a list of early id in a server")
    async def early(self, ctx):
      loda = []
      for member in ctx.guild.members:
        if member.public_flags.early_supporter:
          loda.append(member)
      if loda == []:
       return await ctx.send("No Early Supporter Found")
      
      await working_lister(listxd=loda, color=0x977FD7, title=f"Early Id's in {ctx.guild.name} - {int(len(loda))}", ctx=ctx)
      #if ctx.message.content in [None, "", " "]:
        #await ctx.reply("Sucessfully Listed Early Accounts")
      

    @list.command(name="active-dev",aliases=["activedev","activedeveloper"],description="Get a list of early id in a server")
    async def activedev(self, ctx):
      loda = []
      for member in ctx.guild.members:
        if member.public_flags.active_developer:
          loda.append(member)
      if loda == []:
        return await ctx.send("No Active Developers Found")   
      await working_lister(listxd=loda, color=0x977FD7, title=f"Active Developer's in {ctx.guild.name} - {int(len(loda))}", ctx=ctx)
               
    @list.command(name="botdev",aliases=["developer","botdeveloper"],description="Get a list of bot developer in a server")
    async def botdev(self, ctx):
      loda = []
      for member in ctx.guild.members:
        if member.public_flags.early_verified_bot_developer:
          loda.append(member)
      if loda == []:
        return await ctx.send("No Bot Developers Found")
      await working_lister(listxd=loda, color=0x977FD7, title=f"List of developer in {ctx.guild.name} - {int(len(loda))}", ctx=ctx)
   
    @list.command(name="inrole", aliases=["inside-role"],description="See a list of members that are in the seperate role")
    async def list_inrole(self, ctx, role: discord.Role):
      l = list(role.members)
    
      await working_lister(ctx=ctx, listxd=l, color=0x977FD7, title=f"List of members in {role.name} - {int(len(l))}")
      
                          
    @list.command(name="bans", aliases=["ban"],description="See a list of banned user")
    async def bans(self, ctx):
      ok = []
      async for idk in ctx.guild.bans(limit=None):
        ok.append(idk)
      if ok == []:
        return await ctx.send("There aren't any banned users")
      await lister_bn(ctx=ctx, listxd=ok, color=0x977FD7, title=f"List of Banned members in {ctx.guild.name} - {len(ok)}")
           
    
    @list.command(name="roles", aliases=["role"],description="See a list of roles in the server")
    async def roles(self, ctx):
      l = [r for r in ctx.guild.roles if not r.id == ctx.guild.default_role.id]
      l.reverse()
      await rolis(ctx=ctx, listxd=l, color=0x977FD7, title=f"List of Roles in {ctx.guild.name} - {int(len(l))}")

    
    @list.command(name="invc",aliases=["vc","in-vc"],description="See a list of members in a vc")
    async def vclist(self, ctx):
      s = ctx.message.author.voice.channel.name
      if not ctx.message.author.voice:
        await ctx.send(f"<:codez_cross:1022362833834483762> | You are not connected to any voice channels")
      else:
        loda = []
        aa = ctx.message.author.voice.channel.members.mention
        loda.append(aa)
      if loda == []:
        return await ctx.send("There are no members in vc")
        await working_lister(listxd=loda, color=0x977FD7, title=f"List Of Members In {s} - {int(len(loda))}", ctx=ctx)
        
         #   await lister(ctx,your_list=member_list,color=color,title=f"List of members in {ctx.message.author.voice.channel.name}")
                     
async def setup(bot):           
 await bot.add_cog(List(bot))