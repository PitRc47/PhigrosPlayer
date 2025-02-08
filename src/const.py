import typing
import platform

class NOTE_TYPE:
    TAP = 1
    DRAG = 2
    HOLD = 3
    FLICK = 4

class NOTE_JUDGE_RANGE:
    PERFECT = 0.08
    GOOD = 0.16
    BAD = 0.18
    MISS = 0.2

class CHART_TYPE:
    PHI = 1
    RPE = 2

class NOTE_STATE:
    PERFECT = 1
    GOOD = 2
    BAD = 3
    MISS = 4

class PHIGROS_SETTING_STATE:
    PLAY = 1
    ACCOUNT_AND_COUNT = 2
    OTHER = 3

class OTHER_SETTING_LB_STRINGS:
    TWITTER = "@Phigros PGS"
    BILIBILI = "@Phigros官方"
    QQ = "鸽游网络@Phigros"

class PHIGROS_LINKS:
    TWITTER = "https://twitter.com/Phigros_PGS"
    BILIBILI = "https://space.bilibili.com/414149787"
    QQ = "https://pd.qq.com/s/433r43ehu"
    PRIVACYPOLIC = "https://www.pigeongames.cn/news/2"

class PHI_SORTMETHOD:
    DEFAULT = 1
    SONG_NAME = 2
    DIFFICULTY = 3
    SCORE = 4

class CHART_RENDER_ORDERS:
    LINE = 0
    
    HOLD = 1
    FLICK = 2
    DRAG = 2
    TAP = 2
    
    DEBUG = 3

class LINEWIDTH:
    PHI = 0.0075
    RPE = 1 / 180
    
TYPE_STRING_MAP = {
    NOTE_TYPE.TAP: "Tap",
    NOTE_TYPE.DRAG: "Drag",
    NOTE_TYPE.HOLD: "Hold",
    NOTE_TYPE.FLICK: "Flick"
}

NOTE_RORDER_MAP = {
    NOTE_TYPE.TAP: CHART_RENDER_ORDERS.TAP,
    NOTE_TYPE.DRAG: CHART_RENDER_ORDERS.DRAG,
    NOTE_TYPE.HOLD: CHART_RENDER_ORDERS.HOLD,
    NOTE_TYPE.FLICK: CHART_RENDER_ORDERS.FLICK
}

PHI_SORTMETHOD_STRING_MAP = {
    PHI_SORTMETHOD.DEFAULT: "默认",
    PHI_SORTMETHOD.SONG_NAME: "曲名",
    PHI_SORTMETHOD.DIFFICULTY: "难度",
    PHI_SORTMETHOD.SCORE: "成绩"
}
        
INF = float("inf")
NAN = float("nan")
JUDGELINE_PERFECT_COLOR = "#feffa9"
RENDER_RANGE_MORE_FRAME_LINE_COLOR = "rgba(0, 94, 255, 0.65)"
PHIGROS_VERSION = "NULL"
DEVICE = platform.platform()
OTHERSERTTING_RIGHTDOWN_TEXT = "@2019-2024 Pigeon Games. All right Reserverd."
FINISH_UI_BUTTON_SIZE = 0.10625
JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER = 127 / 975
CHAPTER_DIAGONALRECTANGLEDEG = -75
RPE_WIDTH = 1350
RPE_HEIGHT = 900
PGR_UW = 0.05625
PGR_UH = 0.6
PHIGROS_TAPTAP_CLIENT_ID = "rAK3FfdieFob2Nn8Am"
FLOAT_LESSZERO_MAGIC = -1 / 1024
CSOUND_MANAGER_THREADNUM = 1
INFBEAT = 1e9
ALL_LETTER = "qwertyuiopasdfghjklzxcvbnm"
REPO_URL = "https://github.com/qaqFei/PhigrosPlayer"
BASE_PORT = 16384
MAX_PORT = 65535
ClickEffectType = list[tuple[float, tuple[tuple[float, ...]], typing.Callable[[float|int, float|int], tuple[float, float]]]]
BadEffectType = list[tuple[float, float, tuple[float, float]]]
MissEffectType = list[tuple[float, typing.Any]] # emm, typing.Any is a note typing.Any

DSP_SETTING_TIP = """\
如果你在游戏中遇到游戏中的音乐无法正常播放的情况，请适当的更改这个设置。\n
在游戏中，更小的 Buffer 可以带来更低的音频延时，但同时会导致某些设备出现音频撕裂、音频嘈杂且缓慢，音频卡顿等问题。\n
如果你遇到了上述问题，请将这个值调整至可以让音频正常播放的最小值。可以通过播放下方的示例音频来测试音频能否正常播放。\n
由于技术性原因，此页面可能无法生效。
"""

# 用 phi 的还是本项目的呢..?
PHI_OPENSOURCELICENSE = """\
MIT License

Copyright (c) 2024 qaq_fei

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

PHI_ABOUTUSTEXT = """\
Original Director / 原作
    
Soullies（Liu Wen） 
“
作为《Phigros》的作者，我将在此——

感谢 Pigeon Games 的所有成员，是大家无私的精诚合作造就了《Phigros》这一奇迹。

感谢所有给予过 Pigeon Games 帮助的组织与公司，我们非常荣幸能够得到你们的关心和支持。

感谢一直以来支持着《Phigros》的所有玩家，你们的每一次关注，每一个赞许，以及每一条意见，都深刻地影响了这份企划。

更重要的是，感谢此时此刻正在看着这块屏幕的——

你。

As the author of Phigros, I would like to—

Appreciate all the members of PigeonGames. It is our selflessness, sincerity, and cooperation that  has created this miracle.

Appreciate all the organizations and companies that helped PigeonGames. We are very honored to receive your attention and support.

Appreciate all the players who always have been supporting Phigros. Your attention, compliment, and advice have profoundly influenced our project.

More importantly, appreciate the person who is staring at the screen unblinkingly at the moment—

YOU.
”

Producer / 制作人
CN_115（杜锐）
“愿这款游戏也能被留在你的记忆中。”

Director / 策划
Barbarianerman（李茂昌）
“Phigros从发布之初逐步成长，在这段时间内我们得到了无数玩家的鼓励与支持，我在这里对各位表示诚挚的感谢。希望Phigros能够带给各位欢乐，并成为各位心中一份美好的象征。”

Leaders / 部门负责人

Programming / 程序组
CN_115（杜锐）
月下樱（李天勤）
“我们在Phigros中使用了一些有趣的技术，也在各种细节上做出了大胆的尝试，希望能给各位玩家带来更好的体验。同时我们也会不断优化，让Phigros变得更好！”

Chart Design / 谱师组
阿爽（周锐）
“希望大家可以喜欢我们的脑洞（划掉）！”

Illustration / 美术组
喵n葵（刘贝瑜）
“虽然是鸽游美术组，却是最不咕咕的组。一直感谢各位组员的爆肝（？）付出！我们会继续绘制精美的曲绘的！”

Visual & UI Design / 视觉 & UI 设计组
V17AMax（马煜）
“Phigros一路走来，我们各方面的制作水平一直在不断提升，这一点大家有目共睹。视觉设计组仍会尽力给大家带来更多惊喜！”

Music / 音乐组
姜米條（青杰）
“我是姜米條，是 Pigeon Games 的曲师组长，感谢大家支持 Phigros，同时也希望大家喜欢我们游戏的原创音乐。我们会在之后的更新里添加我们制作的音乐！”

Plots Design / 剧情组
DeathMark（赵芫华）
“只要有你们在，名为phigros的奇迹就是不可磨灭的，未来种种，山河表里，大浪凌空，险阻艰难，锦绣衰隆，我们一起度过。”

Advertising / 宣传组
SparkFred_17（周泓怿）
“愿鸽游给大家创造无限快乐，在未来我们一起努力、共同进步，成为每个人心中多彩的世界！”

Pigeon Animation Team / 动画组
汉堡（覃瀚钰）
“感谢各位和我们一起见证Phigros的成长（磕头），不要的显卡统统可以到我这换不锈钢脸盆。”

External Communications / 外部联络
Ctymax
“主要负责了版权商务相关大大小小的事宜，尽可能为玩家们搜罗来优质的音乐与美术作品。希望大家喜欢！”

（以下所有排名不分先后顺序）

Chart Design / 谱师组
Catcats（王子恒）
Ctymax
Gausbon
JKy
StupiGGy
Uvernight
Snorkel
阿爽（周锐）
Rikko
晨（林晨曦）
鲲
小鹏（周怡鹏）
百九十八
月下樱
CN_115
亜樹見希子
Eaimo
Sillyp
TangScend
Barbarianerman（李茂昌）
NerSAN
Harakuma
Pcat
TimiTini
XMT小咩兔
J.R
Jeitie
BlindForest
Clutter
Su1fuR
VikingNexus
_鉄
Homeee
Likey
M3d1uM
Lumiere
iv
Myna
rN
Latency
陈天宇
钱汉铭
官忠鑫
骆新程
阳鉥

Music / 音乐组
BelieverInYou
Ctymax
Rinth_Live
佑木いずみ(TNiK)
ElousΛ.-FZ
姜米條（青杰）
A-39
NceS
陈天宇

Sound Design / 音效设计
姜米條（青杰）

Illustration / 美术组
CH
Cycats
DoublePian
IvyTowers
Jeffery
Karyon
knife美工刀
KToyo
L-sp4
NEKO
SparkFred_17（周泓怿）
佑木いずみ(TNiK)
xperz
艾是Abby
坂东
笔记RE
赤芽
雏凉
翠冷兮
鸫鸫
诡异童话
海产
何呵
混乱の艾若拉
Ctymax
老张
林语
喵n葵（刘贝瑜）
塔塔
无良灬无惑
昔璃
英英英
御坂果子
冰绘
青鸟
幽灵星
Rallxkurara
天天
犀牛坨动画工坊
NerSAN
Tsuioku
圆规compasses
Nico
子狼
谭清心
高倩茹
陈天宇

Visual & UI Design / 视觉 & UI 设计组
CN_115（杜锐）
EndlessZero（郭旭）
Nico
SparkFred_17（周泓怿）
佑木いずみ(TNiK)
V17AMax（马煜）
汉堡（覃瀚钰）
喵n葵（刘贝瑜）
小鹏（周怡鹏）
Jizici

Plots Design / 剧情组
DeathMark（赵芫华）
关若文
漓染玄柒
关河梦

Localization / 翻译组
312321432（吳安仁）
hwanyeom
jack
Kitty
Nice Player
Saimu桜夢（徐泽城）
Sakuyou
Mai（Tan Chin Wan）
TurretOmega
ViscerΔ
Yurim
はなちゃん/はなまる
徊奏
鲲
亘川锌酸猫
梓澄
漆伊澄
ReFyo

Pigeon Animation Team / 动画组
汉堡（覃瀚钰）
rN
AiLANE
小鹏（周怡鹏）
V17AMax（马煜）

Advertising / 宣传组
Barbarianerman
Ctymax
EndlessZero（郭旭）
Findstr
SparkFred_17（周泓怿）
佑木いずみ(TNiK)
V17AMax（马煜）
东方不buy菌
华莱士
七奏
Sagilio
小菊花
小鹏（周怡鹏）
312321432
陈天宇
Mai（Tan Chin Wan）
阿爽
rN
ReFyo

Customer Service / 客服组
CN_115
Ctymax
joiec
Sparkfred_17（周泓怿）
Jizici
阿爽
喵n葵（刘贝瑜）
月下樱
陈天宇

External Communications / 外部联络
Ctymax

Special Thanks / 特别鸣谢
omegaPi
TigerHix
Soul Notes
Rising Sun Traxx
I-Inferno 《同步音律喵赛克》
A-ZERO Entertainment 《WAVEAT ReLIGHT》
PeroPeroGames 《Muse Dash 喵斯快跑》
QueseraGames 《KALPA》
CEM Records
SUBBASE
Noxy Games 《Lanota》
Beo Meker Studio 《茶鸣拾贰律》
Abyss Idols
Oshiribeat
SoT Records

以及其他所有帮助过我们的人或组织


Beta tester / 测试组
98F
C爆
Likey
Nxnfly
Soul小东东
UraniumW
冰淇淋
打火机D.H.Jack
困锁Lockeder
葉之Leviz
Attack_cat
比我还帅的地球人
Caiyv
赤赤菌
垂星
Excaive
fanIST
FrozenX
晴岚
Hikari
哈拿捏口
坚果
Kirina
切切
Ska
散唳
石皮幼鸟
三色绘本°
Supa7onyz
ThirdQuadrant
VOII
我爱吃肉wacr
汐
晓风竹林
СУМÎС
Y1cat
一游
ZxyD218
温柔的小狮子
Phoenix`palsar
于铠歌
肖斌文

And all participants from Taptap's beta program!
// 此处不展示谱师


--------------------------------
(以下内容与Phigros游戏无关)
关于PhigrosPlayer项目 (https://github.com/qaqFei/PhigrosPlayer),

PhigrosPlayer 是一个项目，使用MIT协议进行开源。

项目的开发贡献者
qaqFei (Owner)
星空孤雁 (Introduction 谱面谱师)
"""

PHIGROS_SETTING_BAR_WIDTH_MAP = {
    PHIGROS_SETTING_STATE.PLAY: 0.465625,
    PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT: 0.8265625,
    PHIGROS_SETTING_STATE.OTHER: 0.8265625
}
PHIGROS_SETTING_LABEL_WIDTH_MAP = {
    PHIGROS_SETTING_STATE.PLAY: 0.1,
    PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT: 0.146875,
    PHIGROS_SETTING_STATE.OTHER: 0.1
}
PHIGROS_SETTING_LABEL_X_MAP = {
    PHIGROS_SETTING_STATE.PLAY: 0.1609375,
    PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT: 0.25625,
    PHIGROS_SETTING_STATE.OTHER: 0.3984375
}
PHIGROS_SETTING_SHADOW_XRECT_MAP = {
    PHIGROS_SETTING_STATE.PLAY: (-0.3328125, 0.615625),
    PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT: (0.0265625, 0.975),
    PHIGROS_SETTING_STATE.OTHER: (0.0265625, 0.975),
}

UAS = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
    "Opera/8.0 (Windows NT 5.1; U; en)",
    "Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
    "MAC：Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
    "Windows：Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)"
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.3.4000 Chrome/30.0.1599.101 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 UBrowser/4.0.3214.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.2.1; zh-cn; HTC_Wildfire_A3333 Build/FRG83D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)"
]

def set_NOTE_DUB_FIXSCALE(scale: float):
    global NOTE_DUB_FIXSCALE
    NOTE_DUB_FIXSCALE = scale

EXTRA_DEFAULTS = {
    "chromatic": {
        "sampleCount": 3,
        "power": 0.01
    },
    "circleBlur": {
        "size": 10.0
    },
    "fisheye": {
        "power": -0.1
    },
    "glitch": {
        "power": 0.3,
        "rate": 0.6,
        "speed": 5.0,
        "blockCount": 30.5,
        "colorRate": 0.01
    },
    "grayscale": {
        "factor": 1.0
    },
    "noise": {
        "seed": 81.0,
        "power": 0.03
    },
    "pixel": {
        "size": 10.0
    },
    "radialBlur": {
        "centerX": 0.5,
        "centerY": 0.5,
        "power": 0.01,
        "sampleCount": 3,
    },
    "shockwave": {
        "progress": 0.2,
        "centerX": 0.5,
        "centerY": 0.5,
        "width": 0.1,
        "distortion": 0.8,
        "expand": 10.0
    },
    "vignette": {
        "color": [0, 0, 0, 1],
        "extend": 0.25,
        "radius": 15.0
    }
}

del typing