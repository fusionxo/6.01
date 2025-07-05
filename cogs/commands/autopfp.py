import asyncio
import json
import random
from utils.Tools import *
import discord
from discord.ext import commands

pfpss = ['https://cdn.discordapp.com/attachments/608711473652563968/1018307916710817842/22EE8237-C6D8-4BDC-8366-596C4D6ED487.gif', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121440714817596/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018051616756219916/5dc823c5bb21cdc63dac7dd86ec93d2f.jpg', 'https://cdn.discordapp.com/attachments/608711476219478045/1019191077506396170/a_fe6fbe3cec2fccbff3c71ccb6d0c9f9a.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019186587180990514/a_4fbe6403d85f03bcd428ac52a04b1731.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018152608860475462/image5.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018152606893346816/Gif6.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151757743923341/a_af347fce39d2a0640e672ffbad797a7a.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151756221394944/a_62550197c4ec87e91770a22dd4f45edb-1.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151755273474110/a_67d61390265cb7294137ab700b327755.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151433671032892/a_44dcbf79100c201d91390c78e23fe39e.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151432437899264/a_9e465caa99b2c136ecc6c98a8185c86f.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151431276081202/a_6ea343b4bf2373d38adbc855877754de.gif', 'https://cdn.discordapp.com/attachments/608711474952798221/1018984869424013333/ugur_askimin_ppsi.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1018949984843997214/e1240bba6622954599804b94eeea22b0.jpg', 'https://cdn.discordapp.com/attachments/608711473652563968/1019152927220301875/ba90d567d37ae57d41c10ece156e2111.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1018636127814570064/9de66e99de86f66cbe3d479ef6756e9b.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1018309211983192184/147367F7-B146-4623-89D7-5E7FD3E633DA.gif', 'https://cdn.discordapp.com/attachments/768864495522283560/1018984139946459196/IMG_20220912_233247.jpg', 'https://cdn.discordapp.com/attachments/768864495522283560/1018983026589450270/2.png', 'https://cdn.discordapp.com/attachments/768864495522283560/1018970085173497946/750f5e44205acea8ed30397cae020fa9.jpg', 'https://cdn.discordapp.com/attachments/768864495522283560/1018955729496969317/a_85480d503d1c0bbe448742f4a2cd83a9.gif', 'https://cdn.discordapp.com/attachments/768864615676903466/1019337978679668786/a_90a2caf6bd7be576a9ba3b4e4ba81810.gif', 'https://cdn.discordapp.com/attachments/768864615676903466/1019336375293706392/menace-santana-menace-santana-gif.gif', 'https://cdn.discordapp.com/attachments/768864615676903466/1019336312739856464/menace-santana-booskap.gif', 'https://cdn.discordapp.com/attachments/768864615676903466/1019336014503874630/menace-santana.gif', 'https://cdn.discordapp.com/attachments/768864615676903466/1019331930384248863/96ebadd862d6eeb5817c28b3472e2dc4.png', 'https://cdn.discordapp.com/attachments/768864495522283560/1019357643141292042/b.gif', 'https://cdn.discordapp.com/attachments/768864495522283560/1019341567066128435/013c579c700043c96583f99a0775ad6b.jpg', 'https://cdn.discordapp.com/attachments/768864495522283560/1019328501154844733/pp_13.jpg', 'https://cdn.discordapp.com/attachments/768864495522283560/1019311556800020500/a0133a1991742ed8e142af3f0c072563.png', 'https://cdn.discordapp.com/attachments/768864495522283560/1019258155298992148/a_5eca60140eccaeec69f2662cbc600400.gif', 'https://cdn.discordapp.com/attachments/768864495522283560/1019726853386272869/edfd38527129a09a90767ae23205ea73.jpg', 'https://cdn.discordapp.com/attachments/768864495522283560/1019686929572315166/c62590c1756680060e7c38011cd704b5.jpg', 'https://cdn.discordapp.com/attachments/768864495522283560/1019686282747719750/a_c2178733158e5e80a0ba80b10d53501a.gif', 'https://cdn.discordapp.com/attachments/608711478496854019/1018153780786774097/images_24.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1018153202975244379/98f0d329ea4452cbc51d45cde2601da2.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1018122035316150342/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121781036466226/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121729211629688/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121698165395566/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121684768788542/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121647074586654/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121647074586654/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121638778241084/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121620247814144/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121602254245908/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121572017508402/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121552568516652/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121536525324288/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121463422787625/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018121448700772382/unknown.png', 'https://cdn.discordapp.com/attachments/608711478496854019/1018051616756219916/5dc823c5bb21cdc63dac7dd86ec93d2f.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1018051616550703124/55f724042e6c9a8cffdf896a75835adf.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1018051616328396810/55981e6682c262aea523fcdada48e07d.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1019502062255484938/fc35beb42bd3d58546765fcbb37e9675.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1019502061802504192/aa623fb85df127a7d0788adb7afad424.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1019501988410572821/9879d6ae061333c7c3345ef01925a610.jpg', 'https://cdn.discordapp.com/attachments/608711478496854019/1019501987877896232/15aeb18b8eb8c568ae465fc79d193de7.jpg', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151755273474110/a_67d61390265cb7294137ab700b327755.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1018151757743923341/a_af347fce39d2a0640e672ffbad797a7a.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019186587180990514/a_4fbe6403d85f03bcd428ac52a04b1731.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019190886602641438/a_440717d1a0682299b382721985e3ab44.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019190951064907847/a_580331609d1dbae6f8a924a5ccd1bc1a.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019191001824366592/a_9216e2285cf4662ec0278926521258e9.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019191048423100456/a_5629581e37281c6098d325673f40a75d.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019191077506396170/a_fe6fbe3cec2fccbff3c71ccb6d0c9f9a.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019191111085998110/a_81aa4b9a7bacd5d3937b7273be9ffbcd.gif', 'https://cdn.discordapp.com/attachments/608711476219478045/1019191143545704528/a_5bc7210b892a6534e8a7c6a5b9a0a0d8.gif', 'https://cdn.discordapp.com/attachments/608711474952798221/1018949918427201628/9345e3b76b5b94b721b76139761717fd.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1018949978225397870/3e2efb2a9b7eb1d50acc80c68e64ae5c.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1018949984843997214/e1240bba6622954599804b94eeea22b0.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1018950006180425888/eac2545c5b7ca1bbad397dbcac43d028.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1018950018184519751/9ebe939f3206417bbb4fe213d562df76.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1018956823283367957/59a2920daca0e3ae08177c04dbebfa55.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019006065653858404/e517461d37748604040875e98ce01672.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019006067201556640/1a9c10217ec2dc1dbeb181990b48feaa.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019006227210059789/7bad07723979d27368b992ff26454e4f.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019006227210059789/7bad07723979d27368b992ff26454e4f.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019025824785113180/bbdca2a3f44cf08cf6b861e5110ddece.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019124254865887293/69a74536ca13732c665ca30be1d52c34.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019124287711498290/6283ad38d48567fdead26f0f9ee196f6.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019129050956042290/112e7c6c55f07c8f9b00d57827814bbd.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019171107259023400/FWfy12hWYAIvYvr.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019183142785007688/f146217a5975656d318f55a048c3d5be.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019411261127135332/48456c2b6d46704eac62b74664f6adc3.webp', 'https://cdn.discordapp.com/attachments/608711474952798221/1019411260628021248/f33b9743d7a51227a163b7d9f9761c2b.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019398015330558012/817d8631e104efe01fc065ab287f7f23.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019342233096433736/89ffa9f53a6ed48a47656c8024fe0ae6.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019342220433817760/907b261b7e4a723fc205556c1e6feafe.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019853188532289546/IMG_20220831_151223.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019853120697815096/IMG_9719.png', 'https://cdn.discordapp.com/attachments/608711474952798221/1019853073620930580/c1a45258e1af98f6677f7b53b7687f5e.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852824110182420/bdaffd216677d77faa74998bb96cb7ab.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852773803696159/unknown-9.png', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852761241755698/unknown-6_1.png', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852730916937788/4177d4499bd998d10a2b65c5acfec0a1.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852715184107540/3f1a8f1db321e3c5aa95d59ffe4a6942.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852686012715058/b436ab48c401575c1ee12e301eadae61.jpg', 'https://cdn.discordapp.com/attachments/608711474952798221/1019852675237543946/8bae29fd38826f8045986a902de54add.jpg', 'https://cdn.discordapp.com/attachments/608711473652563968/1018307916710817842/22EE8237-C6D8-4BDC-8366-596C4D6ED487.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1018547736884293762/o.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1018637183978053672/a_b9d30a968ff1829b0dc347b5c9231c3e.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1018637429634257027/mavi_gif_25.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1018637548886691850/IMG_6542.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019152978474717194/3667bfc33f7f271a59b4ae8ddba5ad61.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019153096804421632/0ba601f55a0bb68a17b5e3ad024b4d1f.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019153145319931944/7c68f7e7ccf6239e3f7aa9c9b9522499.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019153228740427796/2a407ae5981aa0f9a94da00045db00c0.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019181736204193802/1DFBB8CC-9783-42DB-BE8B-8C35027748A7.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019181736678133800/a_f07baf7e3c051e0af90bba08d6c0f574.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019182016568234034/hit_gif_14.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019182016220114944/gif_3_1-1.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019181740473974856/rererr.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019181740473974856/rererr.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019181739651899392/Man_PP_Gif_9.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019181738871754872/image0_17.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019324790747705395/a_5cf769c363a107c4f376484c0323a29b.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019299528668626954/a_f84900a162b4f54fc9bb6756251c80ea.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019299494321475594/a_c7fe0ca9b65247fc7ea4c6a5217a2393.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019299438184910948/a_70e031ccba3e1a91cb3da03c2183e497.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019603950049165343/edc6cbe81fd98982098de93a9253f42d.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019598841407885343/6.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019598840149594313/Rylie.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019598837926613032/2.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019581044804026388/a_cc0d2ae8230ee576c6e330e7f84ef3bb.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019603952561553448/9cc273b9196784a1b2d50eefd21c02c3.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019603951911456848/bbc721e2c8e48d79cd59da6824b1f861.gif', 'https://cdn.discordapp.com/attachments/608711473652563968/1019603951559127111/7502e1ed0b08ff07e6c393e45575e51c.gif', 'https://cdn.discordapp.com/attachments/608711481969868811/1019199430353764412/20220913_125743.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018526535881326633/unknown.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1018414869881557032/c46790afdfa2d8fc21c22368a0261307.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018414869583773776/adcbdda4b721271e9dc01465415bd160.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018414868598112369/7ffbac1b3919b476524f349820e90a39.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018414868262572072/ac2721a2fddb53766bfd3fa0d363a1cc.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018414867910230016/a52d5c65ad6640b0cd15e668d0d4af3c.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018291162374737971/f3b6a974fcd6ea684b7ff85ec69a3707.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018291162156630036/0771d7b1728c11414e3b940bb7d3d792.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018291161904984124/af53f31728b2a2647714fac478bf3a70.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018291161162592286/36f4e7410423a909befba4541acf7f5c.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018291160881569802/4a7b22f5797eb44ada5dc5141e6622f6.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018291160151756800/52e07587c6e4d27fe5ababff7bedca54.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018211053580062820/unknown.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1018211052867043408/unknown.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1018211052443406366/unknown.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1018137854972538991/1662813354402.gif', 'https://cdn.discordapp.com/attachments/608711481969868811/1018137854569889833/1662813354388.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018137854272086056/1662813354381.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1018137854028808212/1662813354372.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1018052114972409957/89b41f16ebf70bf548c8031b476fb191.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019330043454951554/c441a6db77aa8bb4969285b28e505ee6.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019330041009684601/0565c8ce1ff527cd13fc377d0a258bbc.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019739424046727268/d69a75f10c2c99b9be391882eda4b97b.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019739423820230738/e04e4136c895fb11d9bd06efd2be767d.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019739423576948867/e2c15399ae880a8150470f80753f86b3.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019739423346278501/b4848f597885c8d51f0a0477df681844.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019739423044284546/7f5414eb69d0aa08efdbe6469a3461f2.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019739422520000573/a709ba6f4b0049f7e1d6f9f9013e8753.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019676743713435648/SmartSelect_-.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1019676743449182259/SmartSelect_-_Discord.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1019676743205933066/SmartSelect_-_Discord.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1019676742920704020/SmartSelect_-_Discord.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1019676742622912572/SmartSelect_-_Discord.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1019676742379655178/SmartSelect_-_Discord.png', 'https://cdn.discordapp.com/attachments/608711481969868811/1019675515688325191/c3edeaa85140a5ac21469563d0d4afd1.jpg', 'https://cdn.discordapp.com/attachments/608711481969868811/1019675515487014952/bff7bc9e26fa1122c4234bdbd0499415.jpg']

class AutoPFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autopfp_data = {}
        self._load_data()

    def _load_data(self):
        try:
            with open('jsons/autopfp.json', 'r') as f:
                self.autopfp_data = json.load(f)
        except FileNotFoundError:
            pass

    def _save_data(self):
        with open('jsons/autopfp.json', 'w') as f:
            json.dump(self.autopfp_data, f, indent=4)

    async def send_embed(self, ctx, title, description):
        embed = discord.Embed(title=title, description=description, color=0x977FD7)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1046001142057934939/1108093898179493928/LUKA.png")
        await ctx.send(embed=embed)

    @commands.group(name='apfp', invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @premium_check()
    async def _autopfp(self, ctx):
        await ctx.send_help(ctx.command)

    @_autopfp.command(name='channel')
    @blacklist_check()
    @ignore_check()
    @premium_check()
    async def _autopfp_channel(self, ctx, action, channel: discord.TextChannel = None):
        guild_id = str(ctx.guild.id)
        guild_data = self.autopfp_data.setdefault(guild_id, {'autopfp_channels': [], 'autopfp_enabled': False})

        if not ctx.author.guild_permissions.administrator:
            return await self.send_embed(ctx, "❌ Permission Error", "<:info:1087776877898383400> | You do not have permission to use this command.")

        if action == 'add':
            if len(guild_data['autopfp_channels']) == 0:
                guild_data['autopfp_channels'].append(channel.id)
                self._save_data()
                await self.send_embed(ctx, "Luka | AutoPFP", f"<:check:1087776909246607360> | Added {channel.mention} to the AutoPFP channel list.")
            else:
                await self.send_embed(ctx, "Luka | AutoPFP", f"<:info:1087776877898383400> | You can only have one AutoPFP channel. Remove the existing channel before adding a new one.")

        elif action == 'remove':
            if channel.id in guild_data['autopfp_channels']:
                guild_data['autopfp_channels'].remove(channel.id)
                self._save_data()
                await self.send_embed(ctx, "Luka | AutoPFP", f"<:check:1087776909246607360> | Removed {channel.mention} from the AutoPFP channel list.")
            else:
                await self.send_embed(ctx, "Luka | AutoPFP", f"<:check:1087776909246607360> | {channel.mention} is not in the AutoPFP channel list.")

    @_autopfp.command(name='enable')
    @blacklist_check()
    @ignore_check()
    @premium_check()
    async def _autopfp_enable(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_data = self.autopfp_data.setdefault(guild_id, {'autopfp_channels': [], 'autopfp_enabled': False})

        if not ctx.author.guild_permissions.administrator:
            return await self.send_embed(ctx, "❌ Permission Error", "<:info:1087776877898383400> | You do not have permission to use this command.")

        if not guild_data['autopfp_enabled']:
            guild_data['autopfp_enabled'] = True
            self._save_data()
            await self.send_embed(ctx, "Luka | AutoPFP", "<:check:1087776909246607360> | AutoPFP has been enabled.")
            await self._start_autopfp(guild_id)

        else:
            await self.send_embed(ctx, "Luka | AutoPFP", "<:check:1087776909246607360> | AutoPFP is already enabled.")
            await self._start_autopfp(guild_id)

    @_autopfp.command(name='disable')
    @blacklist_check()
    @ignore_check()
    @premium_check()
    async def _autopfp_disable(self, ctx):
        guild_id = str(ctx.guild.id)
        guild_data = self.autopfp_data.setdefault(guild_id, {'autopfp_channels': [], 'autopfp_enabled': False})

        if not ctx.author.guild_permissions.administrator:
            return await self.send_embed(ctx, "❌ Permission Error", "<:info:1087776877898383400> | You do not have permission to use this command.")

        if guild_data['autopfp_enabled']:
            guild_data['autopfp_enabled'] = False
            self._save_data()
            await self.send_embed(ctx, "Luka | AutoPFP", "<:check:1087776909246607360> | AutoPFP has been disabled.")
        else:
            await self.send_embed(ctx, "Luka | AutoPFP", "<:check:1087776909246607360> | AutoPFP is already disabled.")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild_id, guild_data in self.autopfp_data.items():
            if guild_data['autopfp_enabled']:
                await self._start_autopfp(guild_id)

    async def _start_autopfp(self, guild_id):
        while self.autopfp_data.get(guild_id, {}).get('autopfp_enabled', False):
            channel_id = random.choice(self.autopfp_data[guild_id]['autopfp_channels'])
            channel = discord.utils.get(self.bot.get_all_channels(), id=channel_id)
            
            if channel:
                pfp = random.choice(pfpss)
                await channel.send(pfp)
                
            await asyncio.sleep(600)

def setup(bot):
    bot.add_cog(AutoPFP(bot))
