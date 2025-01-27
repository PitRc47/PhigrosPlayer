import err_processer as _
import init_logging as _
import fix_workpath as _
import check_edgechromium as _

import webbrowser
import typing
import random
import json
import sys
import time
import math
import logging
from io import BytesIO
from threading import Thread
from ctypes import windll
from os import system
from os.path import exists

from PIL import Image, ImageFilter, ImageEnhance

import webcv
import const
import tool_funcs
import phigame_obj
import rpe_easing
import phicore
import chartobj_phi
import chartobj_rpe
import chartfuncs_phi
import chartfuncs_rpe
import dxsound
import phira_resource_pack
import tempdir
from dxsmixer import mixer
from graplib_webview import *

    
if not exists("./phigros_assets") or not all([
    exists(tool_funcs.gtpresp(i)) for i in [
        "config.json",
        "chapters.json"
    ]
]):
    logging.error("phigros_assets not found or corrupted, you can download it from https://github.com/qaqFei/PhigrosPlayer_PhigrosAssets")
    system("pause")
    raise SystemExit

tempdir.clearTempDir()
temp_dir = tempdir.createTempDir()

assetConfig = json.loads(open(tool_funcs.gtpresp("config.json"), "r", encoding="utf-8").read())
userData_default = {
    "userdata-userName": "GUEST",
    "userdata-userAvatar": assetConfig["default-avatar"],
    "userdata-userBackground": assetConfig["default-background"],
    "userdata-rankingScore": 0.0,
    "userdata-selfIntroduction": "There is a self-introduction, write something just like:\nTwitter: @Phigros_PGS\nYouTube: Pigeon Games\n\nHope you have fun in Phigros.\nBest regards,\nPigeon Games",
    "setting-chartOffset": 0,
    "setting-noteScale": 1.0,
    "setting-backgroundDim": 0.4,
    "setting-enableClickSound": True,
    "setting-musicVolume": 1.0,
    "setting-uiVolume": 1.0,
    "setting-clickSoundVolume": 1.0,
    "setting-enableMorebetsAuxiliary": True,
    "setting-enableFCAPIndicator": True,
    "setting-enableLowQuality": False,
    "internal-lowQualityScale": 1.0,
    "internal-dspBufferExponential": 8,
    "internal-lowQualityScale-JSLayer": 2.5
}

def saveUserData(data: dict):
    try:
        with open("./phigros_userdata.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=4, ensure_ascii=False))
    except Exception as e:
        logging.error(f"phigros_userdata.json save failed: {e}")

def loadUserData():
    global userData
    userData = userData_default.copy()
    try:
        userData.update(json.loads(open("./phigros_userdata.json", "r", encoding="utf-8").read()))
    except Exception as e:
        logging.error(f"phigros_userdata.json load failed, using default data, {e}")

def getUserData(key: str):
    return userData.get(key, userData_default[key])

def setUserData(key: str, value: typing.Any):
    userData[key] = value

if not exists("./phigros_userdata.json"):
    saveUserData(userData_default)
    loadUserData()

loadUserData()
saveUserData(userData)

mixer.init(buffer = 2 ** getUserData("internal-dspBufferExponential"))
chaptersDx = 0.0
inMainUI = False
inSettingUI = False
settingState = None
lastMainUI_ChaptersClickX = 0.0
lastLastMainUI_ChaptersClickX = 0.0
settingPlayWidgetsDy = 0.0
mainUI_ChaptersMouseDown = False
changeChapterMouseDownX = float("nan")
lastChangeChapterTime = float("-inf")
setting = phigame_obj.Setting()
PlaySettingWidgets: dict[str, phigame_obj.PhiBaseWidget] = {}
dspSettingWidgets: dict[str, phigame_obj.PhiBaseWidget] = {}

def Load_Chapters():
    global Chapters, ChaptersMaxDx
    jsonData = json.loads(open(tool_funcs.gtpresp("chapters.json"), "r", encoding="utf-8").read())
    Chapters = phigame_obj.Chapters(
        [
            phigame_obj.Chapter(
                name = chapter["name"],
                cn_name = chapter["cn-name"],
                o_name = chapter["o-name"],
                image = chapter["image"],
                songs = [
                    phigame_obj.Song(
                        name = song["name"],
                        composer = song["composer"],
                        image = song["image"],
                        preview = song["preview"],
                        difficlty = [
                            phigame_obj.SongDifficlty(
                                name = diff["name"],
                                level = diff["level"],
                                chart_audio = diff["chart_audio"],
                                chart_image = diff["chart_image"],
                                chart_file = diff["chart_file"],
                                charter = diff["charter"],
                                iller = diff["iller"]
                            )
                            for diff in song["difficlty"]
                        ]
                    )
                    for song in chapter["songs"]
                ]
            )
            for chapter in jsonData["chapters"]
        ]
    )
    
    ChaptersMaxDx = w * (len(Chapters.items) - 1) * (295 / 1920) + w * 0.5 - w * 0.875

def putColor(color: tuple|str, im: Image.Image):
    return Image.merge("RGBA", (
        *Image.new("RGB", im.size, color).split(),
        im.split()[-1]
    ))

def updateUserAvatar():
    udAvatar = getUserData("userdata-userAvatar")
    if udAvatar not in assetConfig["avatars"]:
        setUserData("userdata-userAvatar", userData_default["userdata-userAvatar"])
        if udAvatar not in assetConfig["avatars"]:
            udAvatar = assetConfig["avatars"][0]
        saveUserData()
        logging.warning("User avatar not found, reset to default")
    root.run_js_code(f"""{root.get_img_jsvarname("userAvatar")} = {root.get_img_jsvarname(f'avatar_{assetConfig["avatars"].index(getUserData("userdata-userAvatar"))}')};""")

def Load_Resource():
    global note_max_width, note_max_height
    global note_max_size_half
    global ButtonWidth, ButtonHeight
    global ClickEffectFrameCount
    global MainUIIconWidth, MainUIIconHeight
    global SettingUIOtherIconWidth, SettingUIOtherIconHeight
    global MessageButtonSize
    global JoinQQGuildBannerWidth, JoinQQGuildBannerHeight
    global JoinQQGuildPromoWidth, JoinQQGuildPromoHeight
    global SettingUIOtherDownIconWidth
    global SettingUIOtherDownIconHeight_Twitter, SettingUIOtherDownIconHeight_QQ, SettingUIOtherDownIconHeight_Bilibili
    global TapTapIconWidth, TapTapIconHeight
    global CheckedIconWidth, CheckedIconHeight
    global SortIconWidth, SortIconHeight
    global LoadSuccess
    
    logging.info("Loading Resource...")
    LoadSuccess = mixer.Sound(("./resources/LoadSuccess.wav"))
    
    phi_rpack = phira_resource_pack.PhiraResourcePack("./resources/resource_packs/default")
    phi_rpack.setToGlobal()
    ClickEffectFrameCount = phi_rpack.effectFrameCount
    
    Resource = {
        "levels":{
            "AP": Image.open("./resources/levels/AP.png"),
            "FC": Image.open("./resources/levels/FC.png"),
            "V": Image.open("./resources/levels/V.png"),
            "S": Image.open("./resources/levels/S.png"),
            "A": Image.open("./resources/levels/A.png"),
            "B": Image.open("./resources/levels/B.png"),
            "C": Image.open("./resources/levels/C.png"),
            "F": Image.open("./resources/levels/F.png")
        },
        "logoipt": Image.open("./resources/logoipt.png"),
        "warning": Image.open("./resources/le_warn.png"),
        "phigros": Image.open("./resources/phigros.png"),
        "AllSongBlur": Image.open("./resources/AllSongBlur.png"),
        "facula": Image.open("./resources/facula.png"),
        "collectibles": Image.open("./resources/collectibles.png"),
        "setting": Image.open("./resources/setting.png"),
        "ButtonLeftBlack": Image.open("./resources/Button_Left_Black.png"),
        "ButtonRightBlack": None,
        "message": Image.open("./resources/message.png"),
        "JoinQQGuildBanner": Image.open("./resources/JoinQQGuildBanner.png"),
        "UISound_1": mixer.Sound("./resources/UISound_1.wav"),
        "UISound_2": mixer.Sound("./resources/UISound_2.wav"),
        "UISound_3": mixer.Sound("./resources/UISound_3.wav"),
        "UISound_4": mixer.Sound("./resources/UISound_4.wav"),
        "JoinQQGuildPromo": Image.open("./resources/JoinQQGuildPromo.png"),
        "Arrow_Left": Image.open("./resources/Arrow_Left.png"),
        "Arrow_Right": Image.open("./resources/Arrow_Right.png"),
        "Arrow_Right_Black": Image.open("./resources/Arrow_Right_Black.png"),
        "twitter": Image.open("./resources/twitter.png"),
        "qq": Image.open("./resources/qq.png"),
        "bilibili": Image.open("./resources/bilibili.png"),
        "taptap": Image.open("./resources/taptap.png"),
        "checked": Image.open("./resources/checked.png"),
        "CalibrationHit": dxsound.directSound("./resources/CalibrationHit.wav"),
        "Retry": Image.open("./resources/Retry.png"),
        "Pause": mixer.Sound("./resources/Pause.wav"),
        "PauseImg": Image.open("./resources/Pause.png"),
        "PUIBack": Image.open("./resources/PUIBack.png"),
        "PUIRetry": Image.open("./resources/PUIRetry.png"),
        "PUIResume": Image.open("./resources/PUIResume.png"),
        "edit": Image.open("./resources/edit.png"),
        "close": Image.open("./resources/close.png"),
        "sort": Image.open("./resources/sort.png"),
    }
    
    Resource.update(phi_rpack.createResourceDict())
    
    Resource["ButtonRightBlack"] = Resource["ButtonLeftBlack"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    Resource["Notes"]["Bad"] = putColor((90, 60, 70), Resource["Notes"]["Tap"])
    const.set_NOTE_DUB_FIXSCALE(Resource["Notes"]["Hold_Body_dub"].width / Resource["Notes"]["Hold_Body"].width)
    
    imageBlackMaskHeight = 12
    imageBlackMask = Image.new("RGBA", (1, imageBlackMaskHeight), (0, 0, 0, 0))
    imageBlackMask.putpixel((0, 0), (0, 0, 0, 64))
    imageBlackMask.putpixel((0, 1), (0, 0, 0, 32))
    imageBlackMask.putpixel((0, 2), (0, 0, 0, 16))
    imageBlackMask.putpixel((0, imageBlackMaskHeight - 3), (0, 0, 0, 16))
    imageBlackMask.putpixel((0, imageBlackMaskHeight - 2), (0, 0, 0, 32))
    imageBlackMask.putpixel((0, imageBlackMaskHeight - 1), (0, 0, 0, 64))
    
    respacker = webcv.PILResourcePacker(root)
    respacker.reg_img(imageBlackMask.resize((1, 500)), "imageBlackMask")
    respacker.reg_img(Resource["Retry"], "Retry")
    respacker.reg_img(Resource["PauseImg"], "PauseImg")
    respacker.reg_img(Resource["logoipt"], "logoipt")
    respacker.reg_img(Resource["warning"], "warning")
    respacker.reg_img(Resource["phigros"], "phigros")
    respacker.reg_img(Resource["AllSongBlur"], "AllSongBlur")
    respacker.reg_img(Resource["facula"], "facula")
    respacker.reg_img(Resource["collectibles"], "collectibles")
    respacker.reg_img(Resource["setting"], "setting")
    respacker.reg_img(Resource["ButtonLeftBlack"], "ButtonLeftBlack")
    respacker.reg_img(Resource["ButtonRightBlack"], "ButtonRightBlack")
    respacker.reg_img(Resource["message"], "message")
    respacker.reg_img(Resource["JoinQQGuildBanner"], "JoinQQGuildBanner")
    respacker.reg_img(Resource["JoinQQGuildPromo"], "JoinQQGuildPromo")
    respacker.reg_img(Resource["Arrow_Left"], "Arrow_Left")
    respacker.reg_img(Resource["Arrow_Right"], "Arrow_Right")
    respacker.reg_img(Resource["Arrow_Right_Black"], "Arrow_Right_Black")
    respacker.reg_img(Resource["twitter"], "twitter")
    respacker.reg_img(Resource["qq"], "qq")
    respacker.reg_img(Resource["bilibili"], "bilibili")
    respacker.reg_img(Resource["taptap"], "taptap")
    respacker.reg_img(Resource["checked"], "checked")
    respacker.reg_img(Resource["PUIBack"], "PUIBack")
    respacker.reg_img(Resource["PUIRetry"], "PUIRetry")
    respacker.reg_img(Resource["PUIResume"], "PUIResume")
    respacker.reg_img(Resource["edit"], "edit")
    respacker.reg_img(Resource["close"], "close")
    respacker.reg_img(Resource["sort"], "sort")

    ButtonWidth = w * 0.10875
    ButtonHeight = ButtonWidth / Resource["ButtonLeftBlack"].width * Resource["ButtonLeftBlack"].height # bleft and bright size is the same.
    MainUIIconWidth = w * 0.0265
    MainUIIconHeight = MainUIIconWidth / Resource["collectibles"].width * Resource["collectibles"].height # or arr or oth w/h same ratio
    SettingUIOtherIconWidth = w * 0.01325
    SettingUIOtherIconHeight = SettingUIOtherIconWidth / Resource["Arrow_Right_Black"].width * Resource["Arrow_Right_Black"].height
    MessageButtonSize = w * 0.025
    JoinQQGuildBannerWidth = w * 0.2
    JoinQQGuildBannerHeight = JoinQQGuildBannerWidth / Resource["JoinQQGuildBanner"].width * Resource["JoinQQGuildBanner"].height
    JoinQQGuildPromoWidth = w * 0.721875
    JoinQQGuildPromoHeight = JoinQQGuildPromoWidth / Resource["JoinQQGuildPromo"].width * Resource["JoinQQGuildPromo"].height
    SettingUIOtherDownIconWidth = w * 0.01725
    SettingUIOtherDownIconHeight_Twitter = SettingUIOtherDownIconWidth / Resource["twitter"].width * Resource["twitter"].height
    SettingUIOtherDownIconHeight_QQ = SettingUIOtherDownIconWidth / Resource["qq"].width * Resource["qq"].height
    SettingUIOtherDownIconHeight_Bilibili = SettingUIOtherDownIconWidth / Resource["bilibili"].width * Resource["bilibili"].height
    TapTapIconWidth = w * 0.05
    TapTapIconHeight = TapTapIconWidth / Resource["taptap"].width * Resource["taptap"].height
    CheckedIconWidth = w * 0.0140625
    CheckedIconHeight = CheckedIconWidth / Resource["checked"].width * Resource["checked"].height
    SortIconWidth = w * 0.0171875
    SortIconHeight = SortIconWidth / Resource["sort"].width * Resource["sort"].height
    
    for k,v in Resource["levels"].items():
        respacker.reg_img(v, f"Level_{k}")
        
    for k, v in Resource["Notes"].items():
        respacker.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(ClickEffectFrameCount):
        respacker.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
        respacker.reg_img(Resource["Note_Click_Effect"]["Good"][i], f"Note_Click_Effect_Good_{i + 1}")

    for chapter in Chapters.items:
        chapterimbytes = open(tool_funcs.gtpresp(chapter.image), "rb").read()
        im = Image.open(BytesIO(chapterimbytes))
        chapter.im = im
        respacker.reg_img(chapterimbytes, f"chapter_{chapter.chapterId}_raw")
        respacker.reg_img(im.filter(ImageFilter.GaussianBlur(radius = (im.width + im.height) / 100)), f"chapter_{chapter.chapterId}_blur")
    
    for index, avatar in enumerate(assetConfig["avatars"]):
        respacker.reg_img(open(tool_funcs.gtpresp(avatar), "rb").read(), f"avatar_{index}")
    
    with open("./resources/font.ttf", "rb") as f:
        root.reg_res(f.read(), "PhigrosFont.ttf")
    respacker.load(*respacker.pack())
    
    root.wait_jspromise(f"""loadFont('PhigrosFont', \"{root.get_resource_path("PhigrosFont.ttf")}\");""")
    root.unreg_res("PhigrosFont.ttf")
    
    updateUserAvatar()
    root._regims.clear()
    root.run_js_code(f"createChapterBlackGrd({h * (140 / 1080)}, {h * (1.0 - 140 / 1080)});")
    
    logging.info("Load Resource Successfully")
    return Resource

def bindEvents():
    global mainUISlideControler, settingUIPlaySlideControler
    global settingUIOpenSourceLicenseSlideControler
    global SettingPlayWidgetEventManager, dspSettingWidgetEventManager
    global settingUIChooseAvatarAndBackgroundSlideControler
    
    root.jsapi.set_attr("click", eventManager.click)
    root.run_js_code("_click = (e) => pywebview.api.call_attr('click', e.x * dpr, e.y * dpr);")
    root.run_js_code("document.addEventListener('mousedown', _click);")
    
    root.jsapi.set_attr("mousemove", eventManager.move)
    root.run_js_code("_mousemove = (e) => pywebview.api.call_attr('mousemove', e.x * dpr, e.y * dpr);")
    root.run_js_code("document.addEventListener('mousemove', _mousemove);")
    
    root.jsapi.set_attr("mouseup", eventManager.release)
    root.run_js_code("_mouseup = (e) => pywebview.api.call_attr('mouseup', e.x * dpr, e.y * dpr);")
    root.run_js_code("document.addEventListener('mouseup', _mouseup);")
    
    mainUISlideControler = phigame_obj.SlideControler(
        mainUI_slideControlerMouseDown_valid,
        mainUI_slideControler_setValue,
        0.0, ChaptersMaxDx,
        0.0, 0.0, w, h
    )
    eventManager.regClickEventFs(mainUISlideControler.mouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(mainUISlideControler.mouseUp))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(mainUISlideControler.mouseMove))
    
    settingUIPlaySlideControler = phigame_obj.SlideControler(
        settingUI_slideControlerMouseDown_valid,
        settingUI_slideControler_setValue,
        0.0, 0.0,
        0.0, 0.0, w, h
    )
    eventManager.regClickEventFs(settingUIPlaySlideControler.mouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(settingUIPlaySlideControler.mouseUp))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(settingUIPlaySlideControler.mouseMove))
    
    settingUIOpenSourceLicenseSlideControler = phigame_obj.SlideControler(
        lambda x, y: w * 0.2 <= x <= w * 0.8,
        lambda x, y: None,
        0.0, 0.0,
        0.0, 0.0, w, h
    )
    eventManager.regClickEventFs(settingUIOpenSourceLicenseSlideControler.mouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(settingUIOpenSourceLicenseSlideControler.mouseUp))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(settingUIOpenSourceLicenseSlideControler.mouseMove))
    
    settingUIChooseAvatarAndBackgroundSlideControler = phigame_obj.SlideControler(
        lambda x, y: True,
        lambda x, y: None,
        0.0, 0.0,
        0.0, 0.0, w, h
    )
    eventManager.regClickEventFs(settingUIChooseAvatarAndBackgroundSlideControler.mouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(settingUIChooseAvatarAndBackgroundSlideControler.mouseUp))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(settingUIChooseAvatarAndBackgroundSlideControler.mouseMove))
    
    SettingPlayWidgetEventManager = phigame_obj.WidgetEventManager([], settingPlayWidgetEvent_valid)
    eventManager.regClickEventFs(SettingPlayWidgetEventManager.MouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(SettingPlayWidgetEventManager.MouseUp))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(SettingPlayWidgetEventManager.MouseMove))
    
    dspSettingWidgetEventManager = phigame_obj.WidgetEventManager([], lambda x, y: True)
    eventManager.regClickEventFs(dspSettingWidgetEventManager.MouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(dspSettingWidgetEventManager.MouseUp))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(dspSettingWidgetEventManager.MouseMove))

    eventManager.regClickEventFs(changeChapterMouseDown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(changeChapterMouseUp))

def drawBackground():
    f, t = Chapters.aFrom, Chapters.aTo
    if f == -1: f = t # 最开始的, 没有之前的选择
    imfc, imtc = Chapters.items[f], Chapters.items[t]
    p = getChapterP(imtc)
    
    drawAlphaImage(f"chapter_{imfc.chapterId}_blur", 0, 0, w, h, 1.0 - p, wait_execute=True)
    drawAlphaImage(f"chapter_{imtc.chapterId}_blur", 0, 0, w, h, p, wait_execute=True)

def drawFaculas():
    for facula in faManager.faculas:
        if facula["startTime"] <= time.time() <= facula["endTime"]:
            state = faManager.getFaculaState(facula)
            sizePx = facula["size"] * (w + h) / 40
            drawAlphaImage(
                "facula",
                facula["x"] * w - sizePx / 2, state["y"] * h - sizePx / 2,
                sizePx, sizePx,
                state["alpha"] * 0.4,
                wait_execute = True
            )

def getChapterP(chapter: phigame_obj.Chapter):
    chapterIndex = Chapters.items.index(chapter)
    ef = rpe_easing.ease_funcs[0]
    atime = 1.0
    
    if chapterIndex == Chapters.aFrom:
        p = 1.0 - (time.time() - Chapters.aSTime) / atime
        ef = rpe_easing.ease_funcs[16]
    elif chapterIndex == Chapters.aTo:
        p = (time.time() - Chapters.aSTime) / atime
        ef = rpe_easing.ease_funcs[15]
    else:
        p = 0.0
    
    return ef(tool_funcs.fixorp(p))

def getChapterWidth(p: float):
    return w * (0.221875 + (0.5640625 - 0.221875) * p)

def getChapterToNextWidth(p: float):
    return w * (295 / 1920) + (w * 0.5 - w * (295 / 1920)) * p

def getChapterRect(dx: float, chapterWidth: float):
    return (
        dx, h * (140 / 1080),
        dx + chapterWidth, h * (1.0 - 140 / 1080)
    )

def drawChapterItem(item: phigame_obj.Chapter, dx: float, rectmap: dict):
    p = getChapterP(item)
    if dx > w: return getChapterToNextWidth(p)
    chapterWidth = getChapterWidth(p)
    if dx + chapterWidth < 0: return getChapterToNextWidth(p)
    chapterImWidth = h * (1.0 - 140 / 1080 * 2) / item.im.height * item.im.width
    dPower = tool_funcs.getDPower(chapterWidth, h * (1.0 - 140 / 1080 * 2), 75)
    
    chapterRect = getChapterRect(dx, chapterWidth)
    
    if p != 1.0:
        root.run_js_code(
            f"""ctx.drawDiagonalRectangleClipImage(\
                {",".join(map(str, chapterRect))},\
                {root.get_img_jsvarname(f'chapter_{item.chapterId}_blur')},\
                {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
                {dPower}, 1.0\
            );""",
            add_code_array = True
        )
    
    root.run_js_code(
        f"""ctx.drawDiagonalRectangleClipImage(\
            {",".join(map(str, chapterRect))},\
            {root.get_img_jsvarname(f'chapter_{item.chapterId}_raw')},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, {p}\
        );""",
        add_code_array = True
    )
    
    root.run_js_code(
        f"""ctx.drawDiagonalRectangleClipImage(\
            {",".join(map(str, chapterRect))},\
            {root.get_img_jsvarname("imageBlackMask")},\
            {- (chapterImWidth - chapterWidth) / 2}, 0, {chapterImWidth}, {h * (1.0 - 140 / 1080 * 2)},\
            {dPower}, 1.0\
        );""",
        add_code_array = True
    )
    
    root.run_js_code(
        f"""ctx.drawRotateText2(\
            '{processStringToLiteral(item.name)}',\
            {chapterRect[2] - dPower * chapterWidth - (w + h) / 150}, {chapterRect[3] - (w + h) / 150},\
            -75, 'rgba(255, 255, 255, {0.95 * (1.0 - tool_funcs.PhigrosChapterNameAlphaValueTransfrom(p))})', '{(w + h) / 50}px PhigrosFont',\
            'left', 'bottom'\
        );""",
        add_code_array = True
    )
    
    if p != 0.0:
        drawText(
            chapterRect[2] - (w + h) / 50,
            chapterRect[1] + (w + h) / 90,
            item.cn_name,
            font = f"{(w + h) / 75}px PhigrosFont",
            textAlign = "right",
            textBaseline = "top",
            fillStyle = f"rgba(255, 255, 255, {p ** 2})", # ease again
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + dPower * chapterWidth + (w + h) / 125,
            chapterRect[1] + (w + h) / 90,
            item.o_name,
            font = f"{(w + h) / 115}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = f"rgba(255, 255, 255, {p ** 2})", # ease again
            wait_execute = True
        )
    
    PlayButtonWidth = w * 0.1453125
    PlayButtonHeight = h * (5 / 54)
    PlayButtonDPower = tool_funcs.getDPower(PlayButtonWidth, PlayButtonHeight, 75)

    playButtonRect = (
        chapterRect[2] - dPower * chapterWidth + PlayButtonDPower * PlayButtonWidth - PlayButtonWidth, chapterRect[3] - PlayButtonHeight,
        chapterRect[2] - dPower * chapterWidth + PlayButtonDPower * PlayButtonWidth, chapterRect[3]
    )
    
    playButtonTriangle = (
        playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.17, playButtonRect[1] + (playButtonRect[3] - playButtonRect[1]) * (4 / 11),
        playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.17, playButtonRect[3] - (playButtonRect[3] - playButtonRect[1]) * (4 / 11),
        playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.25, playButtonRect[1] + (playButtonRect[3] - playButtonRect[1]) * 0.5
    )
    
    playButtonAlpha = tool_funcs.PhigrosChapterPlayButtonAlphaValueTransfrom(p)
    rectmap[item.chapterId] = playButtonRect
    
    if playButtonAlpha != 0.0:
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, playButtonRect))},\
                {PlayButtonDPower}, 'rgba(255, 255, 255, {playButtonAlpha})'\
            );""",
            add_code_array = True
        )
        
        root.run_js_code(
            f"""ctx.drawTriangleFrame(\
                {",".join(map(str, playButtonTriangle))},\
                'rgba(0, 0, 0, {playButtonAlpha})',\
                {(w + h) / 800}\
            );""",
            add_code_array = True
        )
        
        drawText(
            playButtonRect[0] + (playButtonRect[2] - playButtonRect[0]) * 0.35,
            playButtonRect[1] + (playButtonRect[3] - playButtonRect[1]) * 0.5,
            "P L A Y",
            font = f"{(w + h) / 65}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = f"rgba(49, 49, 49, {playButtonAlpha})",
            wait_execute = True
        )
    
    dataAlpha = tool_funcs.PhigrosChapterDataAlphaValueTransfrom(p)
    
    if dataAlpha != 0.0:
        drawText(
            chapterRect[0] + chapterWidth * 0.075,
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "All",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * 0.075,
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            f"{len(item.songs)}",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * (0.075 + 0.095),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "Clear",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * (0.075 + 0.095),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            "-",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 2),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "Full Combo",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 2),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            "-",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 3),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * 0.04375,
            "Phi",
            font = f"{(w + h) / 175}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
        
        drawText(
            chapterRect[0] + chapterWidth * (0.075 + 0.095 * 3),
            chapterRect[3] - h * (1.0 - 140 / 1080 * 2) * (0.04375 + 0.0275),
            "-",
            font = f"{(w + h) / 95}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = f"rgba(255, 255, 255, {0.95 * dataAlpha})",
            wait_execute = True
        )
    
    return getChapterToNextWidth(p)

def drawChapters(rectmap: dict):
    chapterX = w * 0.034375 + chaptersDx
    for chapter in Chapters.items:
        chapterX += drawChapterItem(chapter, chapterX, rectmap)

def drawButton(buttonName: typing.Literal["ButtonLeftBlack", "ButtonRightBlack"], iconName: str, buttonPos: tuple[float, float]):
    drawImage(buttonName, *buttonPos, ButtonWidth, ButtonHeight, wait_execute=True)
    
    centerPoint = (0.35, 0.395) if buttonName == "ButtonLeftBlack" else (0.65, 0.605)
    
    drawImage(
        iconName,
        buttonPos[0] + ButtonWidth * centerPoint[0] - MainUIIconWidth / 2,
        buttonPos[1] + ButtonHeight * centerPoint[1] - MainUIIconHeight / 2,
        MainUIIconWidth,
        MainUIIconHeight,
        wait_execute = True
    )

def drawDialog(
    p: float,
    dialogImageName: str, diagonalPower: float,
    dialogImageSize: tuple[float, float],
    noText: str, yesText: str
):
            
    root.run_js_code(
        "dialog_canvas_ctx.clear();",
        add_code_array = True
    )
            
    p = 1.0 - (1.0 - p) ** 3
    tempWidth = dialogImageSize[0] * (0.65 + p * 0.35)
    tempHeight = dialogImageSize[1] * (0.65 + p * 0.35)
    diagonalRectanglePowerPx = diagonalPower * tempWidth
    dialogCenterY = h * 0.5 - tempHeight * 0.2 / 2
    
    dialogRect = (
        w / 2 - tempWidth / 2,
        dialogCenterY - tempHeight / 2,
        w / 2 + tempWidth / 2,
        dialogCenterY + tempHeight / 2 + tempHeight * 0.2
    )
    dialogDPower = tool_funcs.getDPower(*tool_funcs.getSizeByRect(dialogRect), 75)
    
    root.run_js_code(
        f"""dialog_canvas_ctx.save();\
        dialog_canvas_ctx.clipDiagonalRectangle(\
            {",".join(map(str, dialogRect))},\
            {tool_funcs.getDPower(*tool_funcs.getSizeByRect(dialogRect), 75)}\
        );""",
        add_code_array = True
    )
    
    
    setCtx("dialog_canvas_ctx")
    drawAlphaImage(
        dialogImageName,
        w / 2 - tempWidth / 2 + tempWidth * dialogDPower * (0.2 / 1.2),
        dialogCenterY - tempHeight / 2,
        tempWidth, tempHeight,
        p,
        wait_execute = True
    )
    setCtx("ctx")
    
    diagonalRectangle = (
        w / 2 - tempWidth / 2 - diagonalRectanglePowerPx * 0.2,
        dialogCenterY + tempHeight / 2,
        w / 2 + tempWidth / 2 - diagonalRectanglePowerPx,
        dialogCenterY + tempHeight / 2 + tempHeight * 0.2
    )
    
    root.run_js_code(
        f"""dialog_canvas_ctx.fillRectExByRect(\
            {",".join(map(str, diagonalRectangle))},\
            'rgba(0, 0, 0, {0.85 * p})'\
        );""",
        add_code_array = True
    )
    
    root.run_js_code(
        f"""dialog_canvas_ctx.drawDiagonalDialogRectangleText(\
            {",".join(map(str, diagonalRectangle))},\
            {diagonalPower * 0.2},\
            '{processStringToLiteral(noText)}',\
            '{processStringToLiteral(yesText)}',\
            'rgba(255, 255, 255, {p})',\
            '{(w + h) / 95 * (0.65 + p * 0.35)}px PhigrosFont'\
        );""",
        add_code_array = True
    )
    
    root.run_js_code(f"""dialog_canvas_ctx.restore();""", add_code_array=True)
    
    return (
        diagonalRectangle[0] + diagonalRectanglePowerPx * 0.2, diagonalRectangle[1],
        diagonalRectangle[0] + (diagonalRectangle[2] - diagonalRectangle[0]) / 2, diagonalRectangle[3]
    ), (
        diagonalRectangle[0] + (diagonalRectangle[2] - diagonalRectangle[0]) / 2, diagonalRectangle[1],
        diagonalRectangle[2] - diagonalRectanglePowerPx * 0.2, diagonalRectangle[3]
    )

def showStartAnimation():
    global faManager
    
    start_animation_clicked = False
    def start_animation_click_cb(*args): nonlocal start_animation_clicked; start_animation_clicked = True
    
    a1_t = 5.0
    a1_st = time.time()
    mixer.music.load("./resources/NewSplashSceneBGM.mp3")
    played_NewSplashSceneBGM = False
    while True:
        p = (time.time() - a1_st) / a1_t
        if p > 1.0: break
                
        if p > 0.4 and not played_NewSplashSceneBGM:
            played_NewSplashSceneBGM = True
            mixer.music.play(-1)
            Thread(target=soundEffect_From0To1, daemon=True).start()
        
        if p > 0.4:
            eventManager.regClickEventFs(start_animation_click_cb, True)
            if start_animation_clicked:
                break
            
        clearCanvas(wait_execute = True)
        
        drawAlphaImage(
            "logoipt",
            0, 0, w, h,
            tool_funcs.easeAlpha(p),
            wait_execute = True
        )
        
        root.run_js_wait_code()
    
    a2_t = 5.0
    a2_st = time.time()
    while True:
        p = (time.time() - a2_st) / a2_t
        if p > 1.0: break
        if start_animation_clicked: break
        
        clearCanvas(wait_execute = True)
        
        drawAlphaImage(
            "warning",
            0, 0, w, h,
            tool_funcs.easeAlpha(p),
            wait_execute = True
        )
        
        root.run_js_wait_code()
    
    for e in eventManager.clickEvents:
        if e.callback is start_animation_click_cb:
            eventManager.clickEvents.remove(e)
            break
    
    faManager = phigame_obj.FaculaAnimationManager()
    Thread(target=faManager.main, daemon=True).start()
    a3_st = time.time()
    a3_clicked = False
    a3_clicked_time = float("nan")
    a3_sound_fadeout = False
    def a3_click_cb(*args):
        nonlocal a3_clicked_time, a3_clicked
        a3_clicked_time = time.time()
        a3_clicked = True
    eventManager.regClickEventFs(a3_click_cb, True)
    phigros_logo_width = 0.25
    phigros_logo_rect = (
        w / 2 - w * phigros_logo_width / 2,
        h * (100 / 230) - h * phigros_logo_width / Resource["phigros"].width * Resource["phigros"].height / 2,
        w * phigros_logo_width, w * phigros_logo_width / Resource["phigros"].width * Resource["phigros"].height
    )
    if not abs(mixer.music.get_pos() - 8.0) <= 0.05:
        mixer.music.set_pos(8.0)
    while True:
        atime = time.time() - a3_st
        
        if a3_clicked and time.time() - a3_clicked_time > 1.0:
            clearCanvas() # no wait
            break
        
        clearCanvas(wait_execute = True)
        
        drawBackground()
        
        root.run_js_code(
            f"""ctx.fillRectEx(\
                0, 0, {w}, {h},\
                'rgba(0, 0, 0, {(math.sin(atime / 1.5) + 1.0) / 5 + 0.15})'\
            );""",
            add_code_array = True
        )
        
        for i in range(50):
            drawLine(
                0, h * (i / 50), w, h * (i / 50),
                strokeStyle = "rgba(162, 206, 223, 0.03)",
                lineWidth = 0.25, wait_execute = True
            )
    
        drawFaculas()
        
        drawImage("phigros", *phigros_logo_rect, wait_execute = True)
        
        textBlurTime = atime % 5.5
        if textBlurTime > 3.0:
            textBlur = math.sin(math.pi * (textBlurTime - 3.0) / 2.5) * 10
        else:
            textBlur = 0.0
        
        root.run_js_code(
            f"""ctx.shadowColor = '#FFFFFF'; ctx.shadowBlur = {textBlur};""",
            add_code_array = True
        )
        
        drawText(
            w / 2,
            h * (155 / 230),
            text = "点  击  屏  幕  开  始",
            font = f"{(w + h) / 125}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = "#FFFFFF",
            wait_execute = True
        )
        
        root.run_js_code(
            "ctx.shaderColor = 'rgba(0, 0, 0, 0)'; ctx.shadowBlur = 0;",
            add_code_array = True
        )
        
        drawText(
            w / 2,
            h * 0.98,
            text = f"Version: {const.PHIGROS_VERSION}",
            font = f"{(w + h) / 250}px PhigrosFont",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = "#888888",
            wait_execute = True
        )
        
        if atime <= 2.0:
            blurP = 1.0 - (1.0 - atime / 2.0) ** 3
            root.run_js_code(f"""mask.style.backdropFilter = 'blur({(w + h) / 60 * (1 - blurP)}px)';""", add_code_array = True)
        else:
            root.run_js_code(f"""mask.style.backdropFilter = '';""", add_code_array = True)
        
        if a3_clicked and time.time() - a3_clicked_time <= 1.0:
            if not a3_sound_fadeout:
                a3_sound_fadeout = True
                mixer.music.fadeout(500)
            
            root.run_js_code(
                f"""ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {1.0 - (1.0 - (time.time() - a3_clicked_time)) ** 2})'\
                );""",
                add_code_array = True
            )
        
        root.run_js_wait_code()
    
    root.run_js_code(f"mask.style.backdropFilter = '';", add_code_array = True)
    
    mainRender()

def soundEffect_From0To1():
    v = 0.0
    for _ in range(100):
        v += 0.01
        if mixer.music.get_pos() <= 3.0:
            mixer.music.set_volume(v)
            time.sleep(0.02)
        else:
            mixer.music.set_volume(1.0)
            return

def processStringToLiteral(string: str):
    return string.replace("\\","\\\\").replace("'","\\'").replace("\"","\\\"").replace("`","\\`").replace("\n", "\\n")

def mainUI_slideControlerMouseDown_valid(x, y):
    if not inMainUI:
        return False
    
    for e in eventManager.clickEvents:
        if e.tag == "mainUI" and tool_funcs.inrect(x, y, e.rect):
            return False
    
    return True

def mainUI_slideControler_setValue(x, y):
    global chaptersDx
    chaptersDx = x

def settingUI_slideControlerMouseDown_valid(x, y):
    if not inSettingUI or settingState is None or SettingPlayWidgetEventManager.InRect(x, y):
        return False
    
    return (
        settingState.aTo == const.PHIGROS_SETTING_STATE.PLAY and
        w * 0.0921875 <= x <= w * 0.534375 and
        h * (180 / 1080) <= y <= h * (1015 / 1080)
    )

def settingUI_slideControler_setValue(x, y):
    global settingPlayWidgetsDy
    settingPlayWidgetsDy = y

def settingPlayWidgetEvent_valid(x, y):
    if settingState is None:
        return False
    
    return settingState.aTo == const.PHIGROS_SETTING_STATE.PLAY and inSettingUI
    
def changeChapterMouseDown(x, y):
    global changeChapterMouseDownX
    
    if y < h * (140 / 1080) or y > h * (1.0 - 140 / 1080):
        return
    elif not inMainUI:
        return
    
    changeChapterMouseDownX = x

def changeChapterMouseUp(x, y):
    global lastChangeChapterTime
    
    if y < h * (140 / 1080) or y > h * (1.0 - 140 / 1080):
        return
    elif abs(x - changeChapterMouseDownX) > w * 0.005:
        return
    elif not inMainUI:
        return
    elif time.time() - lastChangeChapterTime < 0.85: # 1.0s 动画时间, 由于是ease out, 所以可以提前一点
        return
    
    chapterX = w * 0.034375 + chaptersDx
    for index, i in enumerate(Chapters.items):
        p = getChapterP(i)
        width = getChapterWidth(p)
        dPower = tool_funcs.getDPower(width, h * (1.0 - 140 / 1080 * 2), 75)
        if tool_funcs.inDiagonalRectangle(*getChapterRect(chapterX, width), dPower, x, y):
            if Chapters.aTo != index:
                Chapters.aFrom, Chapters.aTo, Chapters.aSTime = Chapters.aTo, index, time.time()
                lastChangeChapterTime = time.time()
                Resource["UISound_3"].play()
            break
        chapterX += getChapterToNextWidth(p)
        
def checkOffset(now_t: float):
    global show_start_time
    
    dt = tool_funcs.checkOffset(now_t, raw_audio_length, mixer)
    if dt != 0.0:
        show_start_time += dt
        coreConfig.show_start_time = show_start_time
        phicore.CoreConfigure(coreConfig)
        
def mainRender():
    global inMainUI
    inMainUI = True
    
    faManager.faculas.clear()
    mainRenderSt = time.time()
    mixer.music.load("./resources/ChapterSelect.mp3")
    mixer.music.play(-1)
    
    messageRect = (w * 0.015, h * 0.985 - MessageButtonSize, MessageButtonSize, MessageButtonSize)
    JoinQQGuildBannerRect = (0.0, h - JoinQQGuildBannerHeight, JoinQQGuildBannerWidth, JoinQQGuildBannerHeight)
    events = []
    
    clickedMessage = False
    clickMessageTime = float("nan")
    canClickMessage = True
    messageBackTime = 7.0
    messageBacking = False
    messageBackSt = float("nan")
    def clickMessage(*args):
        nonlocal clickedMessage, clickMessageTime, canClickJoinQQGuildBanner
        if canClickMessage:
            clickMessageTime = time.time()
            clickedMessage = True
            canClickJoinQQGuildBanner = True
            Resource["UISound_1"].play()
    events.append(phigame_obj.ClickEvent(
        rect = (messageRect[0], messageRect[1], messageRect[0] + messageRect[2], messageRect[1] + messageRect[3]),
        callback = clickMessage,
        once = False,
        tag = "mainUI"
    ))
    eventManager.regClickEvent(events[-1])
    
    clickedJoinQQGuildBanner = False
    clickedJoinQQGuildBannerTime = float("nan")
    canClickJoinQQGuildBanner = False
    def clickJoinQQGuildBanner(*args):
        global inMainUI
        nonlocal clickedJoinQQGuildBanner, clickedJoinQQGuildBannerTime, messageBackTime
        
        if canClickJoinQQGuildBanner and (time.time() - clickMessageTime) > 0.1:
            clickedJoinQQGuildBannerTime = time.time()
            clickedJoinQQGuildBanner = True
            messageBackTime = float("inf")
            inMainUI = False
            Resource["UISound_2"].play()
    events.append(phigame_obj.ClickEvent(
        rect = (JoinQQGuildBannerRect[0], JoinQQGuildBannerRect[1], JoinQQGuildBannerRect[0] + JoinQQGuildBannerRect[2], JoinQQGuildBannerRect[1] + JoinQQGuildBannerRect[3]),
        callback = clickJoinQQGuildBanner,
        once = False
    ))
    eventManager.regClickEvent(events[-1])
    
    JoinQQGuildPromoNoEvent = None
    JoinQQGuildPromoYesEvent = None
    JoinQQGuildBacking = False
    JoinQQGuildBackingSt = float("nan")
    
    chapterPlayButtonRectMap = {}
    
    def JoinQQGuildPromoNoCallback(*args):
        global inMainUI
        nonlocal JoinQQGuildBacking, JoinQQGuildBackingSt, clickedJoinQQGuildBanner
        nonlocal JoinQQGuildPromoNoEvent, JoinQQGuildPromoYesEvent
        
        JoinQQGuildBacking = True
        JoinQQGuildBackingSt = time.time()
        clickedJoinQQGuildBanner = False
        
        eventManager.unregEvent(JoinQQGuildPromoNoEvent)
        eventManager.unregEvent(JoinQQGuildPromoYesEvent)
        events.remove(JoinQQGuildPromoNoEvent)
        events.remove(JoinQQGuildPromoYesEvent)
        
        JoinQQGuildPromoNoEvent = None
        JoinQQGuildPromoYesEvent = None
        inMainUI = True
    
    def JoinQQGuildPromoYesCallback(*args):
        webbrowser.open_new("https://qun.qq.com/qqweb/qunpro/share?inviteCode=21JzOLUd6J0")
        JoinQQGuildPromoNoCallback(*args)
    
    nextUI, tonextUI, tonextUISt = None, False, float("nan")
    
    def SettingCallback(*args):
        nonlocal nextUI, tonextUI, tonextUISt
        
        if not tonextUI:
            for e in events: eventManager.unregEvent(e)
            
            nextUI, tonextUI, tonextUISt = settingRender, True, time.time()
            mixer.music.fadeout(500)
            Resource["UISound_2"].play()
    
    events.append(phigame_obj.ClickEvent(
        rect = (w - ButtonWidth, h - ButtonHeight, w, h),
        callback = SettingCallback,
        once = False,
        tag = "mainUI"
    ))
    eventManager.regClickEvent(events[-1])
    
    def chaptertChooseCallback(x, y):
        nonlocal nextUI, tonextUI, tonextUISt
        
        if clickedMessage: return
        
        for cid, rect in chapterPlayButtonRectMap.items():
            if tool_funcs.inrect(x, y, rect) and Chapters.items[Chapters.aTo].chapterId == cid:
                if not tonextUI:
                    for e in events: eventManager.unregEvent(e)

                nextUI, tonextUI, tonextUISt = lambda: chooseChartRender(Chapters.items[Chapters.aTo]), True, time.time()
                mixer.music.fadeout(500)
                Resource["UISound_2"].play()
    
    events.append(phigame_obj.ClickEvent(
        rect = (0, 0, w, h),
        callback = chaptertChooseCallback,
        once = False
    ))
    eventManager.regClickEvent(events[-1])
    
    while True:
        clearCanvas(wait_execute = True)
        
        drawBackground()
        
        root.run_js_code(
            f"ctx.fillRectEx(\
                0, 0, {w}, {h},\
                'rgba(0, 0, 0, 0.7)'\
            );",
            add_code_array = True
        )
        
        drawFaculas()
        
        drawButton("ButtonLeftBlack", "collectibles", (0, 0))
        drawButton("ButtonRightBlack", "setting", (w - ButtonWidth, h - ButtonHeight))
        drawChapters(chapterPlayButtonRectMap)
        
        drawAlphaImage(
            "message",
            *messageRect, 0.7,
            wait_execute = True
        )
        
        if clickedMessage and time.time() - clickMessageTime >= messageBackTime:
            clickedMessage = False
            messageBacking = True
            messageBackSt = time.time()
            canClickJoinQQGuildBanner = False
            
            if messageBackTime == 0.0:
                messageBackTime = 2.0 # back JoinQQGuild
            elif messageBackTime == 2.0:
                messageBackTime = 7.0
        
        if clickedMessage and time.time() - clickMessageTime <= 1.5:
            drawImage(
                "JoinQQGuildBanner",
                JoinQQGuildBannerRect[0] - JoinQQGuildBannerWidth + (1.0 - (1.0 - ((time.time() - clickMessageTime) / 1.5)) ** 6) * JoinQQGuildBannerWidth,
                *JoinQQGuildBannerRect[1:],
                wait_execute = True
            )
        elif not clickedMessage and messageBacking:
            if time.time() - messageBackSt > 1.5:
                messageBacking = False
                messageBackSt = time.time() - 1.5 # 防止回弹
                canClickMessage = True
            drawImage(
                "JoinQQGuildBanner",
                JoinQQGuildBannerRect[0] - (1.0 - (1.0 - ((time.time() - messageBackSt) / 1.5)) ** 6) * JoinQQGuildBannerWidth,
                *JoinQQGuildBannerRect[1:],
                wait_execute = True
            )
        elif clickedMessage:
            drawImage(
                "JoinQQGuildBanner",
                *JoinQQGuildBannerRect,
                wait_execute = True
            )
        
        if clickedMessage and canClickMessage:
            canClickMessage = False
        
        if clickedJoinQQGuildBanner:
            canClickJoinQQGuildBanner = False
            p = (time.time() - clickedJoinQQGuildBannerTime) / 0.35
            p = p if p <= 1.0 else 1.0
            ep = 1.0 - (1.0 - p) ** 2
            
            root.run_js_code(
                f"""ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {ep * 0.5})'\
                );""",
                add_code_array = True
            )
            
            root.run_js_code(
                f"""mask.style.backdropFilter = 'blur({(w + h) / 120 * ep}px)';""",
                add_code_array = True
            )
            
            noRect, yesRect = drawDialog(
                p, "JoinQQGuildPromo",
                const.JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER,
                (JoinQQGuildPromoWidth, JoinQQGuildPromoHeight),
                "关闭", "跳转到外部应用"
            )
            
            if JoinQQGuildPromoNoEvent is None and JoinQQGuildPromoYesEvent is None:
                JoinQQGuildPromoNoEvent = phigame_obj.ClickEvent( # once is false, remove event in callback
                    noRect, JoinQQGuildPromoNoCallback, False
                )
                JoinQQGuildPromoYesEvent = phigame_obj.ClickEvent(
                    yesRect, JoinQQGuildPromoYesCallback, False
                )
                events.append(JoinQQGuildPromoNoEvent)
                events.append(JoinQQGuildPromoYesEvent)
                eventManager.regClickEvent(JoinQQGuildPromoNoEvent)
                eventManager.regClickEvent(JoinQQGuildPromoYesEvent)
            else:
                JoinQQGuildPromoNoEvent.rect = noRect
                JoinQQGuildPromoYesEvent.rect = yesRect
        elif JoinQQGuildBacking and time.time() - JoinQQGuildBackingSt < 0.35:
            p = 1.0 - (time.time() - JoinQQGuildBackingSt) / 0.35
            ep = 1.0 - (1.0 - p) ** 2
            
            root.run_js_code(
                f"""ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {ep * 0.5})'\
                );""",
                add_code_array = True
            )
            
            root.run_js_code(
                f"mask.style.backdropFilter = 'blur({(w + h) / 120 * ep}px)';",
                add_code_array = True
            )
            
            drawDialog(
                p, "JoinQQGuildPromo",
                const.JOINQQGUILDPROMO_DIAGONALRECTANGLEPOWER,
                (JoinQQGuildPromoWidth, JoinQQGuildPromoHeight),
                "关闭", "跳转到外部应用"
            )
        elif JoinQQGuildBacking:
            root.run_js_code(
                "mask.style.backdropFilter = 'blur(0px)';",
                add_code_array = True
            )
            
            root.run_js_code(
                "dialog_canvas_ctx.clear();",
                add_code_array = True
            )
            
            JoinQQGuildBacking = False
            JoinQQGuildBackingSt = float("nan")
            messageBackTime = 0.0
        
        if time.time() - mainRenderSt < 2.0:
            p = (time.time() - mainRenderSt) / 2.0
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {(1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        
        if tonextUI and time.time() - tonextUISt < 0.75:
            p = (time.time() - tonextUISt) / 0.75
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        elif tonextUI:
            inMainUI = False
            clearCanvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=nextUI, daemon=True).start()
            break
        
        root.run_js_wait_code()

def renderPhigrosWidgets(
    widgets,
    sx: float,
    sy: float,
    dy: float,
    dx_f: typing.Callable[[float], float],
    max_width: float,
    minY: float, maxY: float
):
    root.run_js_code(
        f"ctx.save(); ctx.clipRect(0.0, {minY}, {w}, {maxY});",
        add_code_array = True
    )
    widgets_height = 0.0
    
    for widget in widgets:
        x, y = sx - dx_f(sy + (dy + widgets_height)), sy + (dy + widgets_height)
        
        if isinstance(widget, phigame_obj.PhiLabel):
            _temp = lambda text, align: drawText(
                x + (max_width if align == "right" else 0.0), y, text, 
                font = f"{widget.fontsize}px PhigrosFont",
                textAlign = align,
                textBaseline = "top",
                fillStyle = widget.color,
                wait_execute = True
            ) if text else None
            _temp(widget.left_text, "left")
            _temp(widget.right_text, "right")
            
            widgets_height += widget.fontsize
            widgets_height += widget.tonext
            widgets_height += h * (27 / 1080)
        elif isinstance(widget, phigame_obj.PhiSlider):
            sliderShadowRect = (
                x, y + h * (6 / 1080),
                x + max_width, y + h * ((41 + 6) / 1080)
            )
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, sliderShadowRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(sliderShadowRect), 75)},\
                    'rgba(0, 0, 0, 0.25)'\
                );""",
                add_code_array = True
            )
            
            conButtonHeight = h * (52 / 1080)
            conWidth = w * 0.0359375 if widget.lr_button else w * 0.0046875
            lConRect = (
                x, y,
                x + conWidth, y + conButtonHeight
            )
            rConRect = (
                lConRect[0] + max_width - conWidth, lConRect[1],
                lConRect[2] + max_width - conWidth, lConRect[3]
            )
            
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, lConRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(lConRect), 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, rConRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(rConRect), 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            if widget.lr_button:
                ctp_l, ctp_r = tool_funcs.getCenterPointByRect(lConRect), tool_funcs.getCenterPointByRect(rConRect)
                coniw_l, coniw_r = (w + h) * 0.003, (w + h) * 0.005 # 控制按钮图标线长度
                root.run_js_code(
                    f"""ctx.drawLineEx(\
                        {ctp_l[0] - coniw_l / 2}, {ctp_l[1]},\
                        {ctp_l[0] + coniw_l / 2}, {ctp_l[1]},\
                        {(w + h) * (1 / 1500)}, 'rgb(63, 63, 63)'\
                    );""",
                    add_code_array = True
                )
                root.run_js_code(
                    f"""ctx.drawLineEx(\
                        {ctp_r[0] - coniw_r / 2}, {ctp_r[1]},\
                        {ctp_r[0] + coniw_r / 2}, {ctp_r[1]},\
                        {(w + h) * (1 / 1500)}, 'rgb(63, 63, 63)'\
                    );""",
                    add_code_array = True
                )
                root.run_js_code(
                    f"""ctx.drawLineEx(\
                        {ctp_r[0]}, {ctp_r[1] - coniw_r / 2},\
                        {ctp_r[0]}, {ctp_r[1] + coniw_r / 2},\
                        {(w + h) * (1 / 1500)}, 'rgb(63, 63, 63)'\
                    );""",
                    add_code_array = True
                )
            
            slider_p = tool_funcs.sliderValueP(widget.value, widget.number_points)
            sliderBlockWidth = w * 0.0359375
            sliderFrameWidth = conWidth - conWidth * tool_funcs.getDPower(*tool_funcs.getSizeByRect(lConRect), 75) + sliderBlockWidth / 2 + w * 0.0046875
            sliderBlockHeight = conButtonHeight
            sliderBlock_x = x + sliderFrameWidth - sliderBlockWidth / 2 + slider_p * (max_width - sliderFrameWidth * 2)
            sliderBlockRect = (
                sliderBlock_x, y,
                sliderBlock_x + sliderBlockWidth, y + sliderBlockHeight
            )
            
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, sliderBlockRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(sliderBlockRect), 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            widget.sliderRect = (
                x + sliderFrameWidth, y,
                x + max_width - sliderFrameWidth, y + sliderBlockHeight
            )
            
            widget.lconButtonRect, widget.rconButtonRect = lConRect, rConRect
            
            widgets_height += widget.tonext
        elif isinstance(widget, phigame_obj.PhiCheckbox):
            drawText(
                x, y, widget.text,
                font = f"{widget.fontsize}px PhigrosFont",
                textAlign = "left",
                textBaseline = "top",
                fillStyle = "rgb(255, 255, 255)",
                wait_execute = True
            )
            
            checkboxShadowRect = (
                x + w * 0.321875, y + h * (6 / 1080),
                x + w * 0.321875 + w * 0.06875, y + h * ((41 + 6) / 1080)
            )
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, checkboxShadowRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(checkboxShadowRect), 75)},\
                    'rgba(0, 0, 0, 0.25)'\
                );""",
                add_code_array = True
            )
            
            checkAnimationP = (time.time() - widget.check_animation_st) / 0.2
            checkAnimationP = tool_funcs.fixorp(checkAnimationP)
            if not widget.checked:
                checkAnimationP = 1.0 - checkAnimationP
            checkAnimationP = 1.0 - (1.0 - checkAnimationP) ** 2
            
            checkButtonDx = (w * 0.06875 - w * 0.0375) * checkAnimationP
            checkButtonRect = (
                x + w * 0.321875 + checkButtonDx, y,
                x + w * 0.321875 + w * 0.0375 + checkButtonDx, y + h * (52 / 1080)
            )
            
            drawImage(
                "checked",
                x + w * 0.340625 - CheckedIconWidth / 2,
                y + tool_funcs.getSizeByRect(checkButtonRect)[1] / 2 - CheckedIconHeight / 2,
                CheckedIconWidth, CheckedIconHeight,
                wait_execute = True
            )
            
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, checkButtonRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(checkButtonRect), 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            widget.checkboxRect = checkboxShadowRect
            
            widgets_height += widget.tonext
        elif isinstance(widget, phigame_obj.PhiButton):
            buttonRect = (
                x + max_width / 2 - widget.width / 2, y,
                x + max_width / 2 + widget.width / 2, y + h * (80 / 1080)
            )
            
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, buttonRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(buttonRect), 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            drawText(
                buttonRect[0] + (buttonRect[2] - buttonRect[0]) / 2, buttonRect[1] + (buttonRect[3] - buttonRect[1]) / 2,
                widget.text,
                font = f"{widget.fontsize}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "rgb(0, 0, 0)",
                wait_execute = True
            )
            
            widget.buttonRect = buttonRect
        
        if not isinstance(widget, phigame_obj.PhiLabel):
            widgets_height += h * (150 / 1080)
            
    root.run_js_code(
        "ctx.restore();",
        add_code_array = True
    )
    
    return widgets_height
        
def settingRender():
    global inSettingUI, settingState
    global settingPlayWidgetsDy
    global PlaySettingWidgets
    
    inSettingUI = True
    
    bgrespacker = webcv.PILResourcePacker(root)
    for i, bg in enumerate(assetConfig["backgrounds"]):
        bgrespacker.reg_img(open(tool_funcs.gtpresp(bg), "rb").read(), f"background_{i}")
    bgrespacker.load(*bgrespacker.pack())
    
    settingState = phigame_obj.SettingState()
    clickedBackButton = False
    settingPlayWidgetsDy = 0.0
    CalibrationClickSoundPlayed = False
    editingUserData = False
    CalibrationClickEffects = []
    CalibrationClickEffectLines = []
    editUserNameRect, editIntroductionRect = (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)
    editAvatarRect, editBackgroundRect = (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)
    nextUI, tonextUI, tonextUISt = None, False, float("nan")
    ShowOpenSource, ShowOpenSourceSt = False, float("nan")
    CloseOpenSource, CloseOpenSourceSt = False, float("nan")
    showAvatars, showAvatarsSt = False, float("nan")
    showBackgrounds, showBackgroundsSt = False, float("nan")
    chooseRects = {"avatars": {}, "backgrounds": {}}
    lastClickChooseAvatarOrBackgroundPos = (0.0, 0.0)
    settingUIOpenSourceLicenseSlideControler.maxValueY = root.run_js_code(
        f"""ctx.drawRectMultilineText(\
            -{w}, -{h}, 0, 0,\
            {root.string2sctring_hqm(const.PHI_OPENSOURCELICENSE)},\
            'rgb(255, 255, 255)', '{(w + h) / 145}px PhigrosFont', {(w + h) / 145}, 1.25\
        );"""
    ) + h * (143 / 1080) * 2 - h
    
    mixer.music.load("./resources/Calibration.wav")
    mixer.music.play(-1)
    
    def updatebg():
        ubgjsname = root.get_img_jsvarname("userBackground")
        bgimname = f"""background_{assetConfig["backgrounds"].index(getUserData("userdata-userBackground"))}"""
        root.run_js_code(f"""{ubgjsname} = blurImg({root.get_img_jsvarname(bgimname)}, {(w + h) / 125});""")
    
    def unregEvents():
        eventManager.unregEvent(clickBackButtonEvent)
        eventManager.unregEvent(settingMainClickEvent)
        eventManager.unregEvent(settingMainReleaseEvent)
    
    def clickBackButtonCallback(*args):
        nonlocal clickedBackButton
        nonlocal nextUI, tonextUI, tonextUISt
        
        if not clickedBackButton and inSettingUI:
            unregEvents()
            nextUI, tonextUI, tonextUISt = mainRender, True, time.time()
            Resource["UISound_4"].play()
    
    clickBackButtonEvent = phigame_obj.ClickEvent(
        rect = (0, 0, ButtonWidth, ButtonHeight),
        callback = clickBackButtonCallback,
        once = False
    )
    eventManager.regClickEvent(clickBackButtonEvent)
    
    lastChangeSettingStateTime = float("-inf")
    
    def _setSettingState(t: int):
        nonlocal lastChangeSettingStateTime
        
        if time.time() - lastChangeSettingStateTime < 0.6:
            return
        elif t == settingState.aTo:
            return
        lastChangeSettingStateTime = time.time()
        settingState.changeState(t)
    
    def settingMainClickCallback(x, y):
        global inSettingUI
        nonlocal nextUI, tonextUI, tonextUISt
        nonlocal ShowOpenSource, ShowOpenSourceSt
        nonlocal CloseOpenSource, CloseOpenSourceSt
        nonlocal editingUserData
        nonlocal showAvatars, showAvatarsSt
        nonlocal showBackgrounds, showBackgroundsSt
        nonlocal lastClickChooseAvatarOrBackgroundPos
        
        # 游玩
        if tool_funcs.inrect(x, y, (
            w * 346 / 1920, h * 35 / 1080,
            w * 458 / 1920, h * 97 / 1080
        )) and inSettingUI and not editingUserData:
            if settingState.aTo == const.PHIGROS_SETTING_STATE.PLAY:
                return
            
            Thread(target=lambda: (time.sleep(settingState.atime / 2), mixer.music.stop(), mixer.music.play(-1)), daemon=True).start()
            _setSettingState(const.PHIGROS_SETTING_STATE.PLAY)
        
        # 账号与统计
        if tool_funcs.inrect(x, y, (
            w * 540 / 1920, h * 35 / 1080,
            w * 723 / 1920, h * 97 / 1080
        )) and inSettingUI and not editingUserData:
            if settingState.aTo == const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT:
                return
            
            mixer.music.fadeout(500)
            _setSettingState(const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        
        # 其他
        if tool_funcs.inrect(x, y, (
            w * 807 / 1920, h * 35 / 1080,
            w * 915 / 1920, h * 97 / 1080
        )) and inSettingUI and not editingUserData:
            if settingState.aTo == const.PHIGROS_SETTING_STATE.OTHER:
                return
            
            mixer.music.fadeout(500)
            _setSettingState(const.PHIGROS_SETTING_STATE.OTHER)
        
        # 校准延迟点击扩散的线条
        if settingState.atis_p and tool_funcs.inrect(x, y, (
            w * 0.6015625, 0.0,
            w, h
        )) and inSettingUI:
            if mixer.music.get_busy():
                mixer_pos = mixer.music.get_pos()
                CalibrationClickEffectLines.append((time.time(), mixer_pos))
        
        # 账号与统计 - 编辑
        if settingState.atis_a and tool_funcs.inrect(x, y, (
            w * 0.85625, h * (181 / 1080),
            w * 0.921875, h * (220 / 1080)
        )) and not (showAvatars or showBackgrounds):
            editingUserData = not editingUserData
        
        # 编辑用户名字
        if settingState.atis_a and tool_funcs.inrect(x, y, editUserNameRect) and editingUserData and not (showAvatars or showBackgrounds):
            newName = root.run_js_code(f"""prompt('请输入新名字', {root.string2sctring_hqm(getUserData("userdata-userName"))});""")
            if newName is not None:
                setUserData("userdata-userName", newName)
                updateFontSizes()
                saveUserData(userData)
        
        # 编辑用户介绍
        if settingState.atis_a and tool_funcs.inrect(x, y, editIntroductionRect) and editingUserData and not (showAvatars or showBackgrounds):
            newName = root.run_js_code("prompt('请输入新介绍 (输入\"\\n\"可换行)', '%s')" % root.string2string_hqm(getUserData("userdata-selfIntroduction").replace("\n", "\\n")))
            if newName is not None:
                setUserData("userdata-selfIntroduction", newName.replace("\\n", "\n"))
                updateFontSizes()
                saveUserData(userData)
        
        # 编辑用户头像
        if settingState.atis_a and tool_funcs.inrect(x, y, editAvatarRect) and editingUserData and not (showAvatars or showBackgrounds):
            showAvatars, showAvatarsSt = True, time.time()
            settingUIChooseAvatarAndBackgroundSlideControler.setDy(0.0)
        
        # 编辑用户背景
        if settingState.atis_a and tool_funcs.inrect(x, y, editBackgroundRect) and editingUserData and not (showAvatars or showBackgrounds):
            showBackgrounds, showBackgroundsSt = True, time.time()
            settingUIChooseAvatarAndBackgroundSlideControler.setDy(0.0)

        # 编辑用户头像/背景 - 关闭
        if settingState.atis_a and tool_funcs.inrect(x, y, (
            w * 0.9078125 - (w + h) * 0.014 / 2, h * (225 / 1080) - (w + h) * 0.014 / 2,
            w * 0.9078125 + (w + h) * 0.014 / 2, h * (225 / 1080) + (w + h) * 0.014 / 2
        )) and (showAvatars or showBackgrounds):
            if showAvatars: showAvatars, showAvatarsSt = False, time.time()
            if showBackgrounds: showBackgrounds, showBackgroundsSt = False, time.time()
        
        # 编辑用户头像 - 选择
        if settingState.atis_a and showAvatars and (time.time() - showAvatarsSt) > 0.15:
            lastClickChooseAvatarOrBackgroundPos = (x, y)
        
        # 编辑用户背景 - 选择
        if settingState.atis_a and showBackgrounds and (time.time() - showBackgroundsSt) > 0.15:
            lastClickChooseAvatarOrBackgroundPos = (x, y)
        
        # 音频问题疑难解答
        if settingState.atis_o and tool_funcs.inrect(x, y, otherSettingButtonRects[0]) and inSettingUI:
            Resource["UISound_4"].play()
            unregEvents()
            nextUI, tonextUI, tonextUISt = audioQARender, True, time.time()
        
        # 观看教学
        if settingState.atis_o and tool_funcs.inrect(x, y, otherSettingButtonRects[1]) and inSettingUI:
            unregEvents()
            nextUI, tonextUI, tonextUISt = lambda: chartPlayerRender(
                chartAudio = "./resources/introduction_chart/audio.mp3",
                chartImage = "./resources/introduction_chart/image.png",
                chartFile = "./resources/introduction_chart/chart.json",
                startAnimation = False,
                chart_information = {
                    "Name": "Introduction",
                    "Artist": "姜米條",
                    "Level": "IN Lv.13",
                    "Illustrator": "L-sp4",
                    "Charter": "星空孤雁",
                    "BackgroundDim": None
                },
                blackIn = True,
                foregroundFrameRender = lambda: None,
                nextUI = mainRender
            ), True, time.time()
        
        # 关于我们
        if settingState.atis_o and tool_funcs.inrect(x, y, otherSettingButtonRects[2]) and inSettingUI:
            unregEvents()
            nextUI, tonextUI, tonextUISt = aboutUsRender, True, time.time()
        
        # 开源许可证
        if settingState.atis_o and tool_funcs.inrect(x, y, otherSettingButtonRects[3]) and inSettingUI:
            inSettingUI = False
            ShowOpenSource, ShowOpenSourceSt = True, time.time()
            settingUIOpenSourceLicenseSlideControler.setDy(settingUIOpenSourceLicenseSlideControler.minValueY)
        
        # 隐私政策
        if settingState.atis_o and tool_funcs.inrect(x, y, otherSettingButtonRects[4]) and inSettingUI:
            webbrowser.open(const.PHIGROS_LINKS.PRIVACYPOLIC)
        
        # 推特链接
        if settingState.atis_o and tool_funcs.inrect(x, y, (
            w * 128 / 1920, h * 1015 / 1080,
            w * 315 / 1920, h * 1042 / 1080
        )) and inSettingUI:
            webbrowser.open(const.PHIGROS_LINKS.TWITTER)
        
        # B站链接
        if settingState.atis_o and tool_funcs.inrect(x, y, (
            w * 376 / 1920, h * 1015 / 1080,
            w * 561 / 1920, h * 1042 / 1080
        )) and inSettingUI:
            webbrowser.open(const.PHIGROS_LINKS.BILIBILI)
        
        # QQ链接
        if settingState.atis_o and tool_funcs.inrect(x, y, (
            w * 626 / 1920, h * 1015 / 1080,
            w * 856 / 1920, h * 1042 / 1080
        )) and inSettingUI:
            webbrowser.open(const.PHIGROS_LINKS.QQ)
        
        # 开源许可证的关闭按钮
        if tool_funcs.inrect(x, y, (0, 0, ButtonWidth, ButtonHeight)) and ShowOpenSource and time.time() - ShowOpenSourceSt > 0.15:
            ShowOpenSource, ShowOpenSourceSt = False, float("nan")
            CloseOpenSource, CloseOpenSourceSt = True, time.time()
    
    def settingMainReleaseCallback(x, y):
        nonlocal showAvatars, showAvatarsSt
        nonlocal showBackgrounds, showBackgroundsSt
        
        if settingState.atis_a and showAvatars and tool_funcs.getLineLength(x, y, *lastClickChooseAvatarOrBackgroundPos) <= (w + h) / 400:
            for v, r in chooseRects["avatars"].items():
                if tool_funcs.inrect(x, y, r):
                    showAvatars, showAvatarsSt = False, time.time()
                    setUserData("userdata-userAvatar", assetConfig["avatars"][v])
                    saveUserData(userData)
                    updateUserAvatar()
        
        if settingState.atis_a and showBackgrounds and tool_funcs.getLineLength(x, y, *lastClickChooseAvatarOrBackgroundPos) <= (w + h) / 400:
            for v, r in chooseRects["backgrounds"].items():
                if tool_funcs.inrect(x, y, r):
                    showBackgrounds, showBackgroundsSt = False, time.time()
                    setUserData("userdata-userBackground", assetConfig["backgrounds"][v])
                    saveUserData(userData)
                    updatebg()
    
    settingMainClickEvent = phigame_obj.ClickEvent(
        rect = (0, 0, w, h),
        callback = settingMainClickCallback,
        once = False
    )
    eventManager.regClickEvent(settingMainClickEvent)
    settingMainReleaseEvent = phigame_obj.ReleaseEvent(
        callback = settingMainReleaseCallback
    )
    eventManager.regReleaseEvent(settingMainReleaseEvent)

    settingDx = [0.0, 0.0, 0.0]
    
    def getShadowDiagonalXByY(y: float):
        return w * tool_funcs.getDPower(w, h, 75) * ((h - y) / h)
    
    def drawOtherSettingButton(x0: float, y0: float, x1: float, y1: float, dpower: float):
        root.run_js_code(
            f"ctx.drawDiagonalRectangle(\
                {x0}, {y0},\
                {x1}, {y1},\
                {dpower}, '#FFFFFF'\
            );",
            add_code_array = True
        )
        
        drawImage(
            "Arrow_Right_Black",
            x0 + (x1 - x0) / 2 - SettingUIOtherIconWidth / 2,
            y0 + (y1 - y0) / 2 - SettingUIOtherIconHeight / 2,
            SettingUIOtherIconWidth,
            SettingUIOtherIconHeight,
            wait_execute = True
        )
    
    otherSettingButtonRects = [
        (
            w * (0.0515625 + 0.0265625 + 0.25) + getShadowDiagonalXByY(h * 0.575), h * 0.575,
            w * (0.0515625 + 0.0265625 + 0.25 + 0.046875) + getShadowDiagonalXByY(h * 0.575), h * (0.575 + 0.05)
        ),
        (
            w * (0.0515625 + 0.0265625 + 0.25) + getShadowDiagonalXByY(h * 0.675), h * 0.675,
            w * (0.0515625 + 0.0265625 + 0.25 + 0.046875) + getShadowDiagonalXByY(h * 0.675), h * (0.675 + 0.05)
        ),
        (
            w * (0.0515625 + 0.0265625 + 0.25) + getShadowDiagonalXByY(h * 0.775), h * 0.775,
            w * (0.0515625 + 0.0265625 + 0.25 + 0.046875) + getShadowDiagonalXByY(h * 0.775), h * (0.775 + 0.05)
        ),
        (
            w * (0.0515625 + 0.0265625 + 0.4015625 + 0.25) + getShadowDiagonalXByY(h * 0.575), h * 0.575,
            w * (0.0515625 + 0.0265625 + 0.4015625 + 0.25 + 0.046875) + getShadowDiagonalXByY(h * 0.575), h * (0.575 + 0.05)
        ),
        (
            w * (0.0515625 + 0.0265625 + 0.4015625 + 0.25) + getShadowDiagonalXByY(h * 0.675), h * 0.675,
            w * (0.0515625 + 0.0265625 + 0.4015625 + 0.25 + 0.046875) + getShadowDiagonalXByY(h * 0.675), h * (0.675 + 0.05)
        )
    ]
    
    def drawPlaySetting(dx: float, alpha: float):
        nonlocal CalibrationClickSoundPlayed, CalibrationClickEffectLines
        nonlocal CalibrationClickEffects
        
        if alpha == 0.0: return
        
        root.run_js_code(
            f"""ctx.save(); ctx.translate({- dx}, 0); ctx.globalAlpha = {alpha};""",
            add_code_array = True
        )
        
        settingUIPlaySlideControler.maxValueY = renderPhigrosWidgets(
            list(PlaySettingWidgets.values()),
            w * 0.175, h * 0.175,
            settingPlayWidgetsDy,
            lambda x: getShadowDiagonalXByY(h - x),
            w * 0.3953125,
            h * (180 / 1080), h * (1015 / 1080)
        ) - h * (835 / 1080) # 这里为什么要减, ???
        
        lineColor = "255, 255, 170" if getUserData("setting-enableFCAPIndicator") else "255, 255, 255"
        root.run_js_code( # 2 layers alpha
            f"""ctx.drawLineEx(\
                {w * 0.49375}, {h * 0.8},\
                {w}, {h * 0.8},\
                {h * const.LINEWIDTH.PHI}, 'rgba({lineColor}, {alpha})'\
            );""",
            add_code_array = True
        )
        
        CalibrationMusicPosition = mixer.music.get_pos()
        if CalibrationMusicPosition > 0.0:
            CalibrationMusicPosition += getUserData("setting-chartOffset") / 1000
            CalibrationMusicPosition %= 2.0
            noteWidth = w * 0.1234375 * getUserData("setting-noteScale")
            noteHeight = noteWidth * Resource["Notes"]["Tap"].height / Resource["Notes"]["Tap"].width
            if CalibrationMusicPosition < 1.0:
                noteY = h * 0.85 * CalibrationMusicPosition - h * 0.05
                drawImage(
                    "Note_Tap",
                    w * 0.75 - noteWidth / 2, noteY - noteHeight / 2,
                    noteWidth, noteHeight,
                    wait_execute = True
                )
                if CalibrationClickSoundPlayed:
                    CalibrationClickSoundPlayed = False
            else:
                if not CalibrationClickSoundPlayed:
                    CalibrationClickSoundPlayed = True
                    if getUserData("setting-enableClickSound"):
                        Resource["CalibrationHit"].play()
                    CalibrationClickEffects.append((time.time(), getUserData("setting-noteScale")))
            
            for st, size in CalibrationClickEffects:
                p = (time.time() - st) / 0.5
                if p > 1.0: continue
                    
                random.seed(st)
                random.seed(random.uniform(-st, st))
                phicore.processClickEffectBase(
                    x = w * 0.75,
                    y = h * 0.8,
                    p = p, rblocks = None,
                    perfect = True,
                    noteWidth = w * 0.1234375 * size,
                    root = root,
                    framecount = ClickEffectFrameCount
                )
        
        for t, p in CalibrationClickEffectLines: # vn, ? (time, mixer_pos)
            ap = (time.time() - t) / 1.1
            if ap > 1.0: continue
            
            y = h * 0.85 * ((p + getUserData("setting-chartOffset")) % 2.0) - h * 0.05
            lw = w * ap * 3.0
            root.run_js_code( # 这里alpha值化简了
                f"""ctx.drawLineEx(\
                    {w * 0.75 - lw / 2}, {y},\
                    {w * 0.75 + lw / 2}, {y},\
                    {h * const.LINEWIDTH.PHI * 0.75}, 'rgba(255, 255, 255, {(ap - 1.0) ** 2})'\
                );""",
                add_code_array = True
            )
        
        CalibrationClickEffectLines = list(filter(lambda x: time.time() - x[0] <= 1.1, CalibrationClickEffectLines))
        CalibrationClickEffects = list(filter(lambda x: time.time() - x[0] <= 0.5, CalibrationClickEffects))
        
        root.run_js_code(
            f"""ctx.restore();""",
            add_code_array = True
        )
    
    def drawAccountAndCountSetting(dx: float, alpha: float):
        nonlocal editUserNameRect, editIntroductionRect
        nonlocal editAvatarRect, editBackgroundRect
        
        if alpha == 0.0: return
        
        root.run_js_code(
            f"""ctx.save(); ctx.translate({- dx}, 0); ctx.globalAlpha = {alpha};""",
            add_code_array = True
        )
        
        drawText(
            w * 0.1765625, h * 0.2,
            "玩家信息",
            font = f"{(w + h) / 75}px PhigrosFont",
            textAlign = "left",
            textBaseline = "bottom",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangleClipImage(\
                {w * 0.0796875}, {h * 0.225},\
                {w * 0.940625}, {h * 0.65},\
                {root.get_img_jsvarname("userBackground")},\
                0, {(h * 0.425 - w * 0.8609375 / 16 * 9) / 2},\
                {w * 0.8609375}, {w * 0.8609375 / 16 * 9},\
                {tool_funcs.getDPower(w * 0.8609375, h * 0.425, 75)}, 1.0\
            );""",
            add_code_array = True
        )
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {w * 0.0796875}, {h * 0.225},\
                {w * 0.940625}, {h * 0.65},\
                {tool_funcs.getDPower(w * 0.8609375, h * 0.425, 75)},\
                'rgba(0, 0, 0, 0.375)'\
            );""",
            add_code_array = True
        )
        
        if editingUserData:
            editBackgroundIconSize = (w + h) * 0.007
            editBackgroundRect = (
                w * 0.8796875, h * (257 / 1080),
                w * 0.93125, h * (301 / 1080)
            )
            editBackgroundRectSize = tool_funcs.getSizeByRect(editBackgroundRect)
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, editBackgroundRect))},\
                    {tool_funcs.getDPower(*editBackgroundRectSize, 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            drawImage(
                "edit",
                editBackgroundRect[0] + editBackgroundRectSize[0] / 2 - editBackgroundIconSize / 2,
                editBackgroundRect[1] + editBackgroundRectSize[1] / 2 - editBackgroundIconSize / 2,
                editBackgroundIconSize, editBackgroundIconSize,
                wait_execute = True
            )
        
        leftBlackDiagonalX = 0.538
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {w * 0.0796875}, {h * 0.225},\
                {w * ((0.940625 - 0.0796875) * leftBlackDiagonalX + 0.0796875)}, {h * 0.65},\
                {tool_funcs.getDPower(w * ((0.940625 - 0.0796875) * leftBlackDiagonalX), h * 0.425, 75)},\
                'rgba(0, 0, 0, 0.25)'\
            );""",
            add_code_array = True
        )
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {w * 0.121875}, {h * (283 / 1080)},\
                {w * 0.465625}, {h * (397 / 1080)},\
                {tool_funcs.getDPower(w * 0.34375, h * (114 / 1080), 75)},\
                'rgba(0, 0, 0, 0.9)'\
            );""",
            add_code_array = True
        )
        
        avatarSize = max(w * 0.096875, h * (120 / 1080))
        avatarRect = (
            w * 0.128125, h * (280 / 1080),
            w * 0.225, h * (400 / 1080)
        )
        avatarWidth, avatarHeight = tool_funcs.getSizeByRect(avatarRect)
        root.run_js_code(
            f"""ctx.drawDiagonalRectangleClipImage(\
                {",".join(map(str, avatarRect))},\
                {root.get_img_jsvarname("userAvatar")},\
                {(avatarWidth - avatarSize) / 2},\
                {(avatarHeight - avatarSize) / 2},\
                {avatarSize}, {avatarSize},\
                {tool_funcs.getDPower(avatarWidth, avatarHeight, 75)}, 1.0\
            );""",
            add_code_array = True
        )
        
        if editingUserData:
            editAvatarIconSize = (w + h) * 0.007
            editAvatarRect = (
                avatarRect[0] + avatarWidth * (105 / 185),
                avatarRect[1],
                avatarRect[2],
                avatarRect[1] + avatarHeight * (1 / 3)
            )
            editAvatarRectSize = tool_funcs.getSizeByRect(editAvatarRect)
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, editAvatarRect))},\
                    {tool_funcs.getDPower(*editAvatarRectSize, 75)},\
                    'rgb(255, 255, 255)'\
                );""",
                add_code_array = True
            )
            
            drawImage(
                "edit",
                editAvatarRect[0] + editAvatarRectSize[0] / 2 - editAvatarIconSize / 2,
                editAvatarRect[1] + editAvatarRectSize[1] / 2 - editAvatarIconSize / 2,
                editAvatarIconSize, editAvatarIconSize,
                wait_execute = True
            )
        
        drawText(
            w * 0.234375, h * (340 / 1080),
            getUserData("userdata-userName"),
            font = f"{userName_FontSize}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        rankingScoreRect = (
            w * 0.465625 - (w * 0.34375) * tool_funcs.getDPower(w * 0.34375, h * (114 / 1080), 75),
            h * (357 / 1080),
            w * 0.5140625,
            h * (397 / 1080)
        )
        root.run_js_code( # 这个矩形真头疼...
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, rankingScoreRect))},\
                {tool_funcs.getDPower(rankingScoreRect[2] - rankingScoreRect[0], rankingScoreRect[3] - rankingScoreRect[1], 75)},\
                'rgb(255, 255, 255)'\
            );""",
            add_code_array = True
        )
        
        drawText(
            (rankingScoreRect[0] + rankingScoreRect[2]) / 2, (rankingScoreRect[1] + rankingScoreRect[3]) / 2,
            f"""{getUserData("userdata-rankingScore"):.2f}""",
            font = f"{(rankingScoreRect[3] - rankingScoreRect[1]) * 0.8}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = "rgb(83, 83, 83)",
            wait_execute = True
        )
        
        selfIntroduction_fontSize = (w + h) / 135
        root.run_js_code(
            f"""ctx.drawRectMultilineText(\
                {w * 0.1484375}, {h * (447 / 1080)},\
                {w * 0.4546875}, {h * (660 / 1080)},\
                {root.string2sctring_hqm(getUserData("userdata-selfIntroduction"))},\
                'rgb(255, 255, 255)', '{selfIntroduction_fontSize}px PhigrosFont',\
                {selfIntroduction_fontSize}, 1.15\
            );""",
            add_code_array = True
        )
        
        editButtonRect = (
            w * 0.85625, h * (181 / 1080),
            w * 0.921875, h * (220 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, editButtonRect))},\
                {tool_funcs.getDPower(editButtonRect[2] - editButtonRect[0], editButtonRect[3] - editButtonRect[1], 75)},\
                'rgb(255, 255, 255)'\
            );""",
            add_code_array = True
        )
        
        drawText(
            (editButtonRect[0] + editButtonRect[2]) / 2, (editButtonRect[1] + editButtonRect[3]) / 2,
            "编辑" if not editingUserData else "完成",
            font = f"""{(editButtonRect[3] - editButtonRect[1]) * 0.7}px PhigrosFont""",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = "rgb(83, 83, 83)",
            wait_execute = True
        )
        
        drawText(
            w * 0.46875, h * (805 / 1080),
            "登录以使用云存档功能",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgba(255, 255, 255, {1.0 if not editingUserData else 0.75})",
            wait_execute = True
        )
        
        loginButtonRect = (
            w * 0.4171875, h * (860 / 1080),
            w * 0.5109375, h * (910 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, loginButtonRect))},\
                {tool_funcs.getDPower(loginButtonRect[2] - loginButtonRect[0], loginButtonRect[3] - loginButtonRect[1], 75)},\
                'rgba(255, 255, 255, {1.0 if not editingUserData else 0.75})'\
            );""",
            add_code_array = True
        )
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangleClipImage(\
                {",".join(map(str, loginButtonRect))},\
                {root.get_img_jsvarname("taptap")},\
                {((loginButtonRect[2] - loginButtonRect[0]) - TapTapIconWidth) / 2},\
                {((loginButtonRect[3] - loginButtonRect[1]) - TapTapIconHeight) / 2},\
                {TapTapIconWidth}, {TapTapIconHeight},\
                {tool_funcs.getDPower(loginButtonRect[2] - loginButtonRect[0], loginButtonRect[3] - loginButtonRect[1], 75)},\
                {1.0 if not editingUserData else 0.75}\
            );""",
            add_code_array = True
        )
        
        chartDataDifRect = (
            w * 0.5015625, h * (589 / 1080),
            w * 0.5765625, h * (672 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, chartDataDifRect))},\
                {tool_funcs.getDPower(chartDataDifRect[2] - chartDataDifRect[0], chartDataDifRect[3] - chartDataDifRect[1], 75)},\
                'rgb(255, 255, 255)'\
            );""",
            add_code_array = True
        )
        
        drawText(
            (chartDataDifRect[0] + chartDataDifRect[2]) / 2, (chartDataDifRect[1] + chartDataDifRect[3]) / 2,
            "IN",
            font = f"""{(chartDataDifRect[3] - chartDataDifRect[1]) * 0.55}px PhigrosFont""",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = "rgb(50, 50, 50)",
            wait_execute = True
        )
        
        chartDataRect = (
            chartDataDifRect[2] - tool_funcs.getDPower(chartDataDifRect[2] - chartDataDifRect[0], chartDataDifRect[3] - chartDataDifRect[1], 75) * (chartDataDifRect[2] - chartDataDifRect[0]) * (77 / 85),
            chartDataDifRect[1] + (chartDataDifRect[3] - chartDataDifRect[1]) * (9 / 85),
            w * 0.871875,
            chartDataDifRect[1] + (chartDataDifRect[3] - chartDataDifRect[1]) * (77 / 85),
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, chartDataRect))},\
                {tool_funcs.getDPower(chartDataRect[2] - chartDataRect[0], chartDataRect[3] - chartDataRect[1], 75)},\
                'rgb(0, 0, 0, 0.45)'\
            );""",
            add_code_array = True
        )
        
        def _drawChartDataItem(x: float, text: str):
            root.run_js_code(
                f"""ctx.save(); ctx.font = '{(w + h) / 125}px PhigrosFont'; SlashWidth = ctx.measureText('/').width; ctx.restore();""",
                add_code_array = True
            )
            
            textHeight = h * (635 / 1080)
            
            root.run_js_code(
                f"""ctx.drawTextEx(\
                    '/',\
                    {x}, {textHeight}, '{(w + h) / 125}px PhigrosFont',\
                    'rgb(255, 255, 255)', 'center', 'bottom'\
                );""",
                add_code_array = True
            )
            
            root.run_js_code(
                f"""ctx.drawTextEx(\
                    '-',\
                    {x} + SlashWidth, {textHeight}, '{(w + h) / 125}px PhigrosFont',\
                    'rgb(255, 255, 255)', 'left', 'bottom'\
                );""",
                add_code_array = True
            )
            
            root.run_js_code(
                f"""ctx.drawTextEx(\
                    '0',\
                    {x} - SlashWidth, {textHeight}, '{(w + h) / 85}px PhigrosFont',\
                    'rgb(255, 255, 255)', 'right', 'bottom'\
                );""",
                add_code_array = True
            )
            
            drawText(
                x, h * (648 / 1080),
                text,
                font = f"{(w + h) / 180}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "rgb(255, 255, 255)",
                wait_execute = True
            )
        
        _drawChartDataItem(w * 0.621875, "Cleared")
        _drawChartDataItem(w * 0.71875, "Full Combo")
        _drawChartDataItem(w * 0.8140625, "Phi")
        
        if editingUserData:
            def _strokeRect(rect):
                root.run_js_code(
                    f"""ctx.strokeRectEx(\
                        {rect[0]}, {rect[1]},\
                        {rect[2] - rect[0]}, {rect[3] - rect[1]},\
                        'rgb(255, 255, 255)', {(w + h) / 711.45141919810}\
                    );""",
                    add_code_array = True
                )
                
            editUserNameRect = (
                w * 0.2328125, h * (303 / 1080),
                w * 0.44375, h * (376 / 1080)
            )
            
            editIntroductionRect = (
                w * 0.14375, h * (440 / 1080),
                w * 0.45625, h * (660 / 1080)
            )
            
            _strokeRect(editUserNameRect)
            _strokeRect(editIntroductionRect)
        
        def _drawChooseDialog(
            p: float, text: str, imgs: list[str],
            imgwidth: float, imgheight: float,
            imgx_padding: float, imgy_padding: float,
            imgsx: float, imgsy: float,
            linemax: int, dialogrectname: str
        ):
            top = h - (905 / 1080) * h * p
            
            settingShadowRect = const.PHIGROS_SETTING_SHADOW_XRECT_MAP[const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT]
            settingShadowDPower = tool_funcs.getDPower((settingShadowRect[1] - settingShadowRect[0]) * w, h, 75)
            settingShadowDWidth = (settingShadowRect[1] - settingShadowRect[0]) * w * settingShadowDPower
            chooseDialogLeftX = settingShadowRect[0] * w
            chooseDialogRightX = settingShadowRect[1] * w - settingShadowDWidth + settingShadowDWidth * (h - top) / h
            chooseDialogRect = tuple(map(int, (
                chooseDialogLeftX, top,
                chooseDialogRightX, h,
            )))
            
            root.run_js_code(
                f"""ctx.save(); ctx.clipDiagonalRectangle(\
                    {",".join(map(str, chooseDialogRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(chooseDialogRect), 75)},\
                );""",
                add_code_array = True
            )
            drawBackground()
            root.run_js_code("ctx.restore();", add_code_array=True)
            
            root.run_js_code(
                f"""ctx.drawDiagonalRectangle(\
                    {",".join(map(str, chooseDialogRect))},\
                    {tool_funcs.getDPower(*tool_funcs.getSizeByRect(chooseDialogRect), 75)},\
                    'rgba(0, 0, 0, 0.65)'\
                );""",
                add_code_array = True
            )
            
            textX = chooseDialogLeftX + settingShadowDWidth * (h - top) / h + w * 0.015625
            textY = top + h * (53 / 1080)
            drawText(
                textX, textY,
                text,
                font = f"{(w + h) / 75}px PhigrosFont",
                textAlign = "left",
                textBaseline = "middle",
                fillStyle = "rgb(255, 255, 255)",
                wait_execute = True
            )
            
            closeButtonCenterPoint = (
                chooseDialogRightX - w * 0.0421875,
                top + h * (50 / 1080)
            )
            closeButtonSize = (w + h) * 0.014
            drawImage(
                "close",
                closeButtonCenterPoint[0] - closeButtonSize / 2,
                closeButtonCenterPoint[1] - closeButtonSize / 2,
                closeButtonSize, closeButtonSize,
                wait_execute = True
            )
            
            scdy = settingUIChooseAvatarAndBackgroundSlideControler.getDy()
            imgsy += scdy
            imgsx -= (ShadowXRect[1] - ShadowXRect[0]) * w * ShadowDPower * scdy / h
            imgsx = imgsx + settingShadowDWidth * (h - top) / h + w * 0.015625
            imgx, imgy = imgsx, imgsy + top
            imgdp = tool_funcs.getDPower(imgwidth, imgheight, 75)
            lcount = 0
            
            clipy0, clipy1 = top + h * (100 / 1080), h
            root.run_js_code(f"""ctx.save(); ctx.clipRect(0.0, {min(clipy0, clipy1)}, {w}, {max(clipy0, clipy1)});""", add_code_array = True)
            
            for imgindex, img in enumerate(imgs):
                root.run_js_code(
                    f"""ctx.drawDiagonalRectangleClipImageOnlyHeight(\
                        {imgx}, {imgy},\
                        {imgx + imgwidth}, {imgy + imgheight},\
                        {root.get_img_jsvarname(img)},\
                        {imgheight}, {imgdp}, 1.0\
                    );""",
                    add_code_array = True
                )
                chooseRects[dialogrectname][imgindex] = (
                    imgx, imgy,
                    imgx + imgwidth, imgy + imgheight
                )
                
                imgx += imgwidth + imgx_padding
                lcount += 1
                if lcount >= linemax:
                    imgsx -= (ShadowXRect[1] - ShadowXRect[0]) * w * ShadowDPower * (imgheight + imgy_padding) / h
                    imgx = imgsx
                    imgy += imgheight + imgy_padding
                    lcount = 0
                
                if imgy >= h:
                    break
            
            settingUIChooseAvatarAndBackgroundSlideControler.setDx(0.0)
            settingUIChooseAvatarAndBackgroundSlideControler.maxValueY = (
                math.ceil(len(imgs) / linemax) * (imgheight + imgy_padding)
                - imgy_padding
                - (h - top)
                + (imgsy - scdy)
                + h * (91 / 1080)
            )
            
            root.run_js_code(f"""ctx.restore();""", add_code_array = True)
        
        avatar_imnames = [f"""avatar_{i}""" for i in range(len(assetConfig["avatars"]))]
        background_imnames = [f"background_{i}" for i in range(len(assetConfig["backgrounds"]))]
        
        if showAvatars:
            sa_p = tool_funcs.fixorp((time.time() - showAvatarsSt) / 1.25)
            sa_p = 1.0 - (1.0 - sa_p) ** 12
        elif not showAvatars and time.time() - showAvatarsSt <= 1.25:
            sa_p = (time.time() - showAvatarsSt) / 1.25
            sa_p = (sa_p - 1.0) ** 12
        else: sa_p = None
        
        if showBackgrounds:
            sb_p = tool_funcs.fixorp((time.time() - showBackgroundsSt) / 1.25)
            sb_p = 1.0 - (1.0 - sb_p) ** 12
        elif not showBackgrounds and time.time() - showBackgroundsSt <= 1.25:
            sb_p = (time.time() - showBackgroundsSt) / 1.25
            sb_p = (sb_p - 1.0) ** 12
        else: sb_p = None
        
        if sa_p is not None:
            _drawChooseDialog(
                sa_p, "选择头像", avatar_imnames,
                w * 0.14375, h * (185 / 1080),
                0.0, h * (38 / 1080),
                w * (32 / 1920), h * (120 / 1080),
                5, "avatars"
            )
        if sb_p is not None:
            _drawChooseDialog(
                sb_p, "选择背景", background_imnames,
                w * 0.3765625, h * (200 / 1080),
                w * -0.0078125, h * (23 / 1080),
                w * (10 / 1920), h * (120 / 1080),
                2, "backgrounds"
            )
        
        root.run_js_code(
            f"ctx.restore();",
            add_code_array = True
        )

    def drawOtherSetting(dx: float, alpha: float):
        if alpha == 0.0: return
        
        root.run_js_code(
            f"ctx.save(); ctx.translate({- dx}, 0); ctx.globalAlpha = {alpha};",
            add_code_array = True
        )

        phiIconWidth = w * 0.215625
        phiIconHeight = phiIconWidth / Resource["phigros"].width * Resource["phigros"].height
        drawImage(
            "phigros",
            w * 0.3890625 - phiIconWidth / 2,
            h * ((0.275 + 371 / 1080) / 2) - phiIconHeight / 2,
            phiIconWidth, phiIconHeight,
            wait_execute = True
        )
        
        root.run_js_code(
            f"""ctx.drawLineEx(\
                {w * 0.5296875}, {h * 0.275},\
                {w * 0.5296875}, {h * (371 / 1080)},\
                {(w + h) / 2000}, 'rgb(138, 138, 138, 0.95)'\
            );""",
            add_code_array = True
        )
        
        drawText(
            w * 0.5703125, h * (308 / 1080),
            f"Version: {const.PHIGROS_VERSION}",
            font = f"{(w + h) /125}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgb(138, 138, 138, 0.95)",
            wait_execute = True
        )
        
        drawText(
            w * 0.5703125, h * (361 / 1080),
            f"Device: {const.DEVICE}",
            font = f"{(w + h) /125}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgb(138, 138, 138, 0.95)",
            wait_execute = True
        )
        
        settingOtherButtonDPower = tool_funcs.getDPower(90, 50, 75)
        
        drawText(
            w * (0.0515625 + 0.0265625) + getShadowDiagonalXByY(h * 0.575),
            h * 0.575,
            "音频问题疑难解答",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawText(
            w * (0.0515625 + 0.0265625 + 0.4015625) + getShadowDiagonalXByY(h * 0.575),
            h * 0.575,
            "开源许可证",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawText(
            w * (0.0515625 + 0.0265625) + getShadowDiagonalXByY(h * 0.675),
            h * 0.675,
            "观看教学",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawText(
            w * (0.0515625 + 0.0265625 + 0.4015625) + getShadowDiagonalXByY(h * 0.675),
            h * 0.675,
            "隐私政策",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawText(
            w * (0.0515625 + 0.0265625) + getShadowDiagonalXByY(h * 0.775),
            h * 0.775,
            "关于我们",
            font = f"{(w + h) / 90}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        for i in otherSettingButtonRects:
            drawOtherSettingButton(*i, settingOtherButtonDPower)
        
        drawText(
            w * 0.5453125,
            h * (1031 / 1080),
            const.OTHERSERTTING_RIGHTDOWN_TEXT,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        drawImage(
            "twitter",
            w * 0.0734375 - SettingUIOtherIconWidth / 2,
            h * (1031 / 1080) - SettingUIOtherDownIconHeight_Twitter / 2,
            SettingUIOtherDownIconWidth,
            SettingUIOtherDownIconHeight_Twitter,
            wait_execute = True
        )
        
        drawText(
            w * 0.0875, h * (1031 / 1080),
            const.OTHER_SETTING_LB_STRINGS.TWITTER,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        drawImage(
            "bilibili",
            w * 0.203125 - SettingUIOtherIconWidth / 2,
            h * (1031 / 1080) - SettingUIOtherDownIconHeight_Bilibili / 2,
            SettingUIOtherDownIconWidth,
            SettingUIOtherDownIconHeight_Bilibili,
            wait_execute = True
        )
        
        drawText(
            w * 0.2171875, h * (1031 / 1080),
            const.OTHER_SETTING_LB_STRINGS.BILIBILI,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        drawImage(
            "qq",
            w * 0.3328125 - SettingUIOtherIconWidth / 2 * 0.85,
            h * (1031 / 1080) - SettingUIOtherDownIconHeight_QQ / 2 * 0.85,
            SettingUIOtherDownIconWidth * 0.85,
            SettingUIOtherDownIconHeight_QQ * 0.85,
            wait_execute = True
        )
        
        drawText(
            w * 0.346875, h * (1031 / 1080),
            const.OTHER_SETTING_LB_STRINGS.QQ,
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "middle",
            fillStyle = "rgba(255, 255, 255, 0.5)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"ctx.restore();",
            add_code_array = True
        )
    
    SettingPlayWidgetEventManager.widgets.clear()
    PlaySettingWidgets.clear()
    PlaySettingWidgets.update({
        "OffsetLabel": phigame_obj.PhiLabel(
            left_text = "谱面延时",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "OffsetSlider": phigame_obj.PhiSlider(
            tonext = h * (-67 / 1080),
            value = getUserData("setting-chartOffset"),
            number_points = (
                (0.0, -400.0),
                (0.4, 0.0),
                (1.0, 600.0)
            ),
            lr_button = True,
            sliderUnit = 5.0,
            conUnit = 5.0,
            numberType = int,
            command = updateConfig
        ),
        "OffsetTip": phigame_obj.PhiLabel(
            left_text = "",
            right_text = "",
            fontsize = (w + h) / 150,
            color = "rgba(255, 255, 255, 0.6)"
        ),
        "NoteScaleLabel": phigame_obj.PhiLabel(
            left_text = "按键缩放",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "NoteScaleSlider": phigame_obj.PhiSlider(
            value = getUserData("setting-noteScale"),
            number_points = ((0.0, 1.0), (1.0, 1.29)),
            lr_button = False,
            command = updateConfig
        ),
        "BackgroundDimLabel": phigame_obj.PhiLabel(
            left_text = "背景亮度",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "BackgroundDimSlider": phigame_obj.PhiSlider(
            value = getUserData("setting-backgroundDim"),
            number_points = ((0.0, 0.05), (1.0, 0.4)),
            lr_button = False,
            command = updateConfig
        ),
        "ClickSoundCheckbox": phigame_obj.PhiCheckbox(
            text = "打开打击音效",
            fontsize = (w + h) / 75,
            checked = getUserData("setting-enableClickSound"),
            command = updateConfig
        ),
        "MusicVolumeLabel": phigame_obj.PhiLabel(
            left_text = "音乐音量",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "MusicVolumeSlider": phigame_obj.PhiSlider(
            value = getUserData("setting-musicVolume"),
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False,
            command = updateConfig
        ),
        "UISoundVolumeLabel": phigame_obj.PhiLabel(
            left_text = "界面音效音量",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "UISoundVolumeSlider": phigame_obj.PhiSlider(
            value = getUserData("setting-uiVolume"),
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False,
            command = updateConfig
        ),
        "ClickSoundVolumeLabel": phigame_obj.PhiLabel(
            left_text = "打击音效音量",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "ClickSoundVolumeSlider": phigame_obj.PhiSlider(
            value = getUserData("setting-clickSoundVolume"),
            number_points = ((0.0, 0.0), (1.0, 1.0)),
            lr_button = False,
            command = updateConfig
        ),
        "MorebetsAuxiliaryCheckbox": phigame_obj.PhiCheckbox(
            text = "开启多押辅助",
            fontsize = (w + h) / 75,
            checked = getUserData("setting-enableMorebetsAuxiliary"),
            command = updateConfig
        ),
        "FCAPIndicatorCheckbox": phigame_obj.PhiCheckbox(
            text = "开启FC/AP指示器",
            fontsize = (w + h) / 75,
            checked = getUserData("setting-enableFCAPIndicator"),
            command = updateConfig
        ),
        "LowQualityCheckbox": phigame_obj.PhiCheckbox(
            text = "低分辨率模式",
            fontsize = (w + h) / 75,
            checked = getUserData("setting-enableLowQuality"),
            command = updateConfig
        )
    })
    
    SettingPlayWidgetEventManager.widgets.clear()
    SettingPlayWidgetEventManager.widgets.extend(PlaySettingWidgets.values())
    updateConfig()
    updatebg()
    settingRenderSt = time.time()
    
    while True:
        clearCanvas(wait_execute = True)
        
        drawBackground()
        
        root.run_js_code(
            f"ctx.fillRectEx(\
                0, 0, {w}, {h},\
                'rgba(0, 0, 0, 0.5)'\
            );",
            add_code_array = True
        )
        
        ShadowXRect = settingState.getShadowRect()
        ShadowRect = (
            ShadowXRect[0] * w, 0.0,
            ShadowXRect[1] * w, h
        )
        ShadowDPower = tool_funcs.getDPower(ShadowRect[2] - ShadowRect[0], h, 75)
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, ShadowRect))},\
                {ShadowDPower}, 'rgba(0, 0, 0, 0.2)'\
            );""",
            add_code_array = True
        )
        
        BarWidth = settingState.getBarWidth() * w
        BarHeight = h * (2 / 27)
        BarDPower = tool_funcs.getDPower(BarWidth, BarHeight, 75)
        BarRect = (
            w * 0.153125, h * 0.025,
            w * 0.153125 + BarWidth, h * 0.025 + BarHeight
        )
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, BarRect))},\
                {BarDPower}, 'rgba(0, 0, 0, 0.45)'\
            );""",
            add_code_array = True
        )
        
        BarAlpha = 1.0 if not editingUserData else 0.5
        
        LabelWidth = settingState.getLabelWidth() * w
        LabelHeight = h * (113 / 1080)
        LabelDPower = tool_funcs.getDPower(LabelWidth, LabelHeight, 75)
        LabelX = settingState.getLabelX() * w
        LabelRect = (
            LabelX, h * 1 / 108,
            LabelX + LabelWidth, h * 1 / 108 + LabelHeight
        )
        
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, LabelRect))},\
                {LabelDPower}, '{"rgb(255, 255, 255)" if not editingUserData else "rgb(192, 192, 192)"}'\
            );""",
            add_code_array = True
        )
        
        PlayTextColor = settingState.getTextColor(const.PHIGROS_SETTING_STATE.PLAY) + (BarAlpha, )
        AccountAndCountTextColor = settingState.getTextColor(const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT) + (BarAlpha, )
        OtherTextColor = settingState.getTextColor(const.PHIGROS_SETTING_STATE.OTHER) + (BarAlpha, )
        PlayTextFontScale = settingState.getTextScale(const.PHIGROS_SETTING_STATE.PLAY)
        AccountAndCountTextFontScale = settingState.getTextScale(const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        OtherTextFontScale = settingState.getTextScale(const.PHIGROS_SETTING_STATE.OTHER)
        settingTextY = h * 0.025 + BarHeight / 2
                
        drawText(
            w * 0.209375, settingTextY,
            "游玩",
            font = f"{(w + h) / 100 * PlayTextFontScale}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgba{PlayTextColor}",
            wait_execute = True
        )
        
        drawText(
            w * 0.3296875, settingTextY,
            "账号与统计",
            font = f"{(w + h) / 100 * AccountAndCountTextFontScale}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgba{AccountAndCountTextColor}",
            wait_execute = True
        )
        
        drawText(
            w * 0.4484375, settingTextY,
            "其他",
            font = f"{(w + h) / 100 * OtherTextFontScale}px PhigrosFont",
            textAlign = "center",
            textBaseline = "middle",
            fillStyle = f"rgba{OtherTextColor}",
            wait_execute = True
        )
        
        settingState.render(drawPlaySetting, drawAccountAndCountSetting, drawOtherSetting, ShadowXRect[0], w, settingDx)
        
        drawButton("ButtonLeftBlack", "Arrow_Left", (0, 0))
        
        if ShowOpenSource or CloseOpenSource:
            if CloseOpenSource:
                if time.time() - CloseOpenSourceSt >= 0.35:
                    CloseOpenSource, CloseOpenSourceSt = False, float("nan")
                    inSettingUI = True
                    root.run_js_code(f"mask.style.backdropFilter = 'blur(0px)';", add_code_array = True)
                    root.run_js_code("dialog_canvas_ctx.clear()", add_code_array = True)
            
            if ShowOpenSource:
                p = tool_funcs.fixorp((time.time() - ShowOpenSourceSt) / 0.15)
                p = 1.0 - (1.0 - p) ** 3
            else: # CloseOpenSource
                p = tool_funcs.fixorp((time.time() - CloseOpenSourceSt) / 0.35)
                p = abs(p - 1.0) ** 3
            
            if ShowOpenSource or CloseOpenSource:
                root.run_js_code("_ctxBak = ctx; ctx = dialog_canvas_ctx; dialog_canvas_ctx.clear();", add_code_array = True)
                
                root.run_js_code(f"mask.style.backdropFilter = 'blur({(w + h) / 75 * p}px)';", add_code_array = True)
                root.run_js_code(f"ctx.save(); ctx.globalAlpha = {p};", add_code_array = True)
                
                root.run_js_code(f"ctx.fillRectEx(0, 0, {w}, {h}, 'rgba(0, 0, 0, 0.5)');", add_code_array = True)
                root.run_js_code(
                    f"""ctx.drawRectMultilineText(\
                        {w * 0.2}, {settingUIOpenSourceLicenseSlideControler.getDy() + h * (143 / 1080)}, {w * 0.8}, {h},\
                        {root.string2sctring_hqm(const.PHI_OPENSOURCELICENSE)},\
                        'rgb(255, 255, 255)', '{(w + h) / 145}px PhigrosFont', {(w + h) / 145}, 1.25\
                    );""",
                    add_code_array = True
                )
                drawButton("ButtonLeftBlack", "Arrow_Left", (0, 0))
                
                root.run_js_code("ctx.restore();", add_code_array = True)
                
                root.run_js_code("ctx = _ctxBak; _ctxBak = null;", add_code_array = True)
                
        if time.time() - settingRenderSt < 1.25:
            p = (time.time() - settingRenderSt) / 1.25
            root.run_js_code(
                f"""ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {(1.0 - p) ** 2})'\
                );""",
                add_code_array = True
            )
        
        if tonextUI and time.time() - tonextUISt < 0.75:
            p = (time.time() - tonextUISt) / 0.75
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        elif tonextUI:
            clearCanvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=nextUI, daemon=True).start()
            break
        
        root.run_js_wait_code()
    
    inSettingUI = False
    settingState = None
    SettingPlayWidgetEventManager.widgets.clear()
    PlaySettingWidgets.clear()
    bgrespacker.unload(bgrespacker.getnames())
    
def audioQARender():
    global dspSettingWidgets
    
    audioQARenderSt = time.time()
    nextUI, tonextUI, tonextUISt = None, False, float("nan")
    clickedBackButton = False
    
    def clickBackButtonCallback(*args):
        nonlocal clickedBackButton
        nonlocal nextUI, tonextUI, tonextUISt
        
        if not clickedBackButton:
            eventManager.unregEvent(clickBackButtonEvent)
            nextUI, tonextUI, tonextUISt = settingRender, True, time.time()
            mixer.music.fadeout(500)
            Resource["UISound_4"].play()
    
    clickBackButtonEvent = phigame_obj.ClickEvent(
        rect = (0, 0, ButtonWidth, ButtonHeight),
        callback = clickBackButtonCallback,
        once = False
    )
    eventManager.regClickEvent(clickBackButtonEvent)
    
    dspSettingWidgetEventManager.widgets.clear()
    dspSettingWidgets.clear()
    dspSettingWidgets.update({
        "ValueLabel": phigame_obj.PhiLabel(
            left_text = "Audio Mixer Buffer",
            right_text = "",
            fontsize = (w + h) / 75,
            color = "#FFFFFF"
        ),
        "ValueSlider": phigame_obj.PhiSlider(
            value = getUserData("internal-dspBufferExponential"),
            number_points = [(0.0, 7.0), (1.0, 12.0)],
            lr_button = False,
            sliderUnit = 1.0,
            numberType = int,
            command = updateConfig
        ),
        "PlayButton": phigame_obj.PhiButton(
            text = "播放音频",
            fontsize = (w + h) / 75,
            width = w * 0.19375,
            command = lambda: (mixer.music.load("./resources/TouchToStart.mp3"), mixer.music.play())
        )
    })
    
    dspSettingWidgetEventManager.widgets.clear()
    dspSettingWidgetEventManager.widgets.extend(dspSettingWidgets.values())
    updateConfig()
    
    while True:
        clearCanvas(wait_execute = True)
        
        drawBackground()
        
        root.run_js_code(
            f"ctx.fillRectEx(\
                0, 0, {w}, {h},\
                'rgba(0, 0, 0, 0.5)'\
            );",
            add_code_array = True
        )
        
        shadowRect = (
            w * 0.1015625, 0.0,
            w * 0.9, h
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, shadowRect))},\
                {tool_funcs.getDPower(*tool_funcs.getSizeByRect(shadowRect), 75)}, 'rgba(0, 0, 0, 0.25)'\
            );""",
            add_code_array = True
        )
    
        renderPhigrosWidgets(
            dspSettingWidgets.values(), w * 0.275, h * (665 / 1080), 0.0,
            lambda y: ((y - h * (665 / 1080)) / h) * (tool_funcs.getSizeByRect(shadowRect)[0] * tool_funcs.getDPower(*tool_funcs.getSizeByRect(shadowRect), 75)),
            w * 0.425, 0.0, h
        )
        
        drawText(
            w * 0.3, h * (98 / 1080),
            "音频问题疑难解答",
            font = f"{(w + h) / 62.5}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = "rgb(255, 255, 255)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"""ctx.drawRectMultilineTextDiagonal(\
                {w * 0.28125}, {h * (241 / 1080)},\
                {w * 0.7984375}, {h}, {root.string2sctring_hqm(const.DSP_SETTING_TIP)},\
                'rgb(255, 255, 255)',\
                '{(w + h) / 120}px PhigrosFont', {(w + h) / 120}, {- w * 0.0046875}, 1.25\
            );""",
            add_code_array = True
        )
        
        drawButton("ButtonLeftBlack", "Arrow_Left", (0, 0))
                
        if time.time() - audioQARenderSt < 1.25:
            p = (time.time() - audioQARenderSt) / 1.25
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {(1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        
        if tonextUI and time.time() - tonextUISt < 0.75:
            p = (time.time() - tonextUISt) / 0.75
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        elif tonextUI:
            clearCanvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=nextUI, daemon=True).start()
            break
        
        root.run_js_wait_code()
    
    dspSettingWidgetEventManager.widgets.clear()
    dspSettingWidgets.clear()

def aboutUsRender():
    aboutUsRenderSt = time.time()
    nextUI, tonextUI, tonextUISt = None, False, float("nan")
    clickedStart = False
    clickedStartButtonTime = float("nan")
    skipStart = False
    skipStartButtonTime = float("nan")
    
    def skipEventCallback(*args):
        nonlocal skipStart, skipStartButtonTime
        
        skipStart, skipStartButtonTime = True, time.time()
    
    def CancalSkipEventCallback(*args):
        nonlocal skipStart, skipStartButtonTime
        
        skipStart, skipStartButtonTime = False, float("nan")
    
    def clickStartButtonCallback(*args):
        nonlocal clickedStart, clickedStartButtonTime
        
        if not clickedStart:
            clickedStart, clickedStartButtonTime = True, time.time()
    
    skipEvent = eventManager.regClickEventFs(skipEventCallback, False)
    skipEventRelease = eventManager.regReleaseEventFs(CancalSkipEventCallback)
    clickStartButtonEvent = eventManager.regClickEventFs(clickStartButtonCallback, False)
    
    while True:
        clearCanvas(wait_execute = True)
        
        if not clickedStart or time.time() - clickedStartButtonTime <= 0.75:
            phiIconWidth = w * 0.296875
            phiIconHeight = phiIconWidth / Resource["phigros"].width * Resource["phigros"].height
            alpha = 1.0 if clickedStartButtonTime != clickedStartButtonTime else ((time.time() - clickedStartButtonTime) / 0.75 - 1.0) ** 2
            
            drawAlphaImage(
                "phigros",
                w / 2 - phiIconWidth / 2, h / 2 - phiIconHeight / 2,
                phiIconWidth, phiIconHeight,
                alpha,
                wait_execute = True
            )
            
            drawText(
                w * 0.5015625, h * (733 / 1080),
                text = "t   o   u   c   h      t   o      s   t   a   r   t",
                font = f"{(w + h) / 80 * (1.0 + (math.sin(time.time() * 1.5) + 1.1) / 35)}px PhigrosFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = f"rgba(255, 255, 255, {alpha})",
                wait_execute = True
            )
        
        if clickedStart:
            if not mixer.music.get_busy():
                mixer.music.load("./resources/AboutUs.mp3")
                mixer.music.play(-1)
            dy = h - h * ((time.time() - clickedStartButtonTime) / 12.5)
            fontsize = (w + h) / 102.5
            root.run_js_code(
                f"aboutus_textheight = ctx.drawRectMultilineTextCenter(\
                    {w * 0.05}, {dy}, {w * 0.95}, {h},\
                    {root.string2sctring_hqm(const.PHI_ABOUTUSTEXT)},\
                    'rgb(255, 255, 255)', '{fontsize}px PhigrosFont', {fontsize}, 1.4\
                );",
                add_code_array = True
            )
        else:
            dy, fontsize = h, 0.0
            root.run_js_code(f"aboutus_textheight = {h * 2.0};", add_code_array = True)
        
        if time.time() - aboutUsRenderSt < 1.25:
            p = (time.time() - aboutUsRenderSt) / 1.25
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {(1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        
        if (skipStart and skipStartButtonTime == skipStartButtonTime) or (tonextUI and skipStartButtonTime == skipStartButtonTime):
            p = (time.time() - skipStartButtonTime) / 1.75 if (skipStart and skipStartButtonTime == skipStartButtonTime) else (1.0 - (time.time() - tonextUISt) / 0.75)
            drawText(
                w * 0.028125, h * (50 / 1080),
                "长按以跳过",
                font = f"{(w + h) / 80}px PhigrosFont",
                textAlign = "left",
                textBaseline = "top",
                fillStyle = f"rgba(255, 255, 255, {p})",
                wait_execute = True
            )
        
        if tonextUI and time.time() - tonextUISt < 0.75:
            p = (time.time() - tonextUISt) / 0.75
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        elif tonextUI:
            clearCanvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=nextUI, daemon=True).start()
            break
        
        if skipStart and time.time() - skipStartButtonTime > 1.75:
            eventManager.unregEvent(skipEvent)
            eventManager.unregEvent(skipEventRelease)
            eventManager.unregEvent(clickStartButtonEvent)
            nextUI, tonextUI, tonextUISt = mainRender, True, time.time()
            mixer.music.fadeout(500)
            skipStart = False
        
        root.run_js_wait_code()
        if dy + root.run_js_code("aboutus_textheight;") < - fontsize and not tonextUI:
            eventManager.unregEvent(skipEvent)
            eventManager.unregEvent(skipEventRelease)
            eventManager.unregEvent(clickStartButtonEvent)
            nextUI, tonextUI, tonextUISt = mainRender, True, time.time()
            mixer.music.fadeout(500)

def chartPlayerRender(
    chartAudio: str,
    chartImage: str,
    chartFile: str,
    startAnimation: bool,
    chart_information: dict,
    blackIn: bool,
    foregroundFrameRender: typing.Callable[[], typing.Any],
    nextUI: typing.Callable[[], typing.Any]
):
    global show_start_time
    global note_max_width, note_max_height
    global note_max_size_half
    global raw_audio_length
    global coreConfig
    
    globalNoteWidth = w * 0.1234375 * getUserData("setting-noteScale")
    note_max_width = globalNoteWidth * const.NOTE_DUB_FIXSCALE
    note_max_height = max(
        [
            note_max_width / Resource["Notes"]["Tap"].width * Resource["Notes"]["Tap"].height,
            note_max_width / Resource["Notes"]["Tap_dub"].width * Resource["Notes"]["Tap_dub"].height,
            note_max_width / Resource["Notes"]["Drag"].width * Resource["Notes"]["Drag"].height,
            note_max_width / Resource["Notes"]["Drag_dub"].width * Resource["Notes"]["Drag_dub"].height,
            note_max_width / Resource["Notes"]["Flick"].width * Resource["Notes"]["Flick"].height,
            note_max_width / Resource["Notes"]["Flick_dub"].width * Resource["Notes"]["Flick_dub"].height,
            note_max_width / Resource["Notes"]["Hold_Head"].width * Resource["Notes"]["Hold_Head"].height,
            note_max_width / Resource["Notes"]["Hold_Head_dub"].width * Resource["Notes"]["Hold_Head_dub"].height,
            note_max_width / Resource["Notes"]["Hold_End"].width * Resource["Notes"]["Hold_End"].height
        ]
    )
    note_max_size_half = ((note_max_width ** 2 + note_max_height ** 2) ** 0.5) / 2
    
    chart_information["BackgroundDim"] = getUserData("setting-backgroundDim")
    chartJsonData: dict = json.loads(open(chartFile, "r", encoding="utf-8").read())
    CHART_TYPE = const.CHART_TYPE.PHI if "formatVersion" in chartJsonData else const.CHART_TYPE.RPE
    if CHART_TYPE == const.CHART_TYPE.PHI: chartJsonData["offset"] += getUserData("setting-chartOffset") / 1000
    elif CHART_TYPE == const.CHART_TYPE.RPE: chartJsonData["META"]["offset"] += getUserData("setting-chartOffset")
    chart_obj = chartfuncs_phi.Load_Chart_Object(chartJsonData) if CHART_TYPE == const.CHART_TYPE.PHI else chartfuncs_rpe.Load_Chart_Object(chartJsonData)
    mixer.music.load(chartAudio)
    raw_audio_length = mixer.music.get_length()
    audio_length = raw_audio_length + (chart_obj.META.offset / 1000 if CHART_TYPE == const.CHART_TYPE.RPE else 0.0)
    
    respacker = webcv.PILResourcePacker(root)
    
    root.run_js_code("delete background; delete begin_animation_image; delete finish_animation_image;")
    chart_image = Image.open(chartImage)
    background_image_blur = chart_image.resize((w, h)).filter(ImageFilter.GaussianBlur((w + h) / 50))
    background_image = ImageEnhance.Brightness(background_image_blur).enhance(getUserData("setting-backgroundDim"))
    respacker.reg_img(background_image, "background")
    
    finish_animation_image_mask = Image.new("RGBA", (1, 5), (0, 0, 0, 0))
    finish_animation_image_mask.putpixel((0, 4), (0, 0, 0, 204))
    finish_animation_image_mask.putpixel((0, 3), (0, 0, 0, 128))
    finish_animation_image_mask.putpixel((0, 2), (0, 0, 0, 64))
    
    animation_image = chart_image.copy().convert("RGBA")
    tool_funcs.cutAnimationIllImage(animation_image)
    
    finish_animation_image = chart_image.copy().convert("RGBA")
    finish_animation_image_mask = finish_animation_image_mask.resize(finish_animation_image.size)
    finish_animation_image.paste(finish_animation_image_mask, (0, 0), finish_animation_image_mask)
    
    respacker.reg_img(chart_image, "begin_animation_image")
    respacker.reg_img(finish_animation_image, "finish_animation_image")
    
    respacker.load(*respacker.pack())
    
    cksmanager = phicore.ClickSoundManager(Resource["Note_Click_Audio"])
    coreConfig = phicore.PhiCoreConfig(
        SETTER = lambda vn, vv: globals().update({vn: vv}),
        root = root, w = w, h = h,
        chart_information = chart_information,
        chart_obj = chart_obj,
        CHART_TYPE = CHART_TYPE, Resource = Resource,
        ClickEffectFrameCount = ClickEffectFrameCount,
        globalNoteWidth = globalNoteWidth,
        note_max_size_half = note_max_size_half,
        audio_length = audio_length, raw_audio_length = raw_audio_length,
        show_start_time = float("nan"), chart_image = chart_image,
        clickeffect_randomblock = True,
        clickeffect_randomblock_roundn = 0.0,
        LoadSuccess = LoadSuccess, chart_res = {},
        cksmanager = cksmanager,
        enable_clicksound = getUserData("setting-enableClickSound"),
        rtacc = False, noautoplay = "--debug" not in sys.argv, showfps = "--debug" in sys.argv,
        lfdaot = False, speed = 1.0, render_range_more = False,
        render_range_more_scale = 1.0,
        debug = "--debug" in sys.argv,
        combotips = "COMBO" if "--debug" not in sys.argv else "AUTOPLAY", noplaychart = False,
        clicksound_volume = getUserData("setting-clickSoundVolume"),
        musicsound_volume = getUserData("setting-musicVolume"),
        enable_controls = False
    )
    phicore.CoreConfigure(coreConfig)
    
    if startAnimation:
        phicore.loadingAnimation(False, foregroundFrameRender)
    
    if phicore.noautoplay:
        if CHART_TYPE == const.CHART_TYPE.PHI:
            pplm_proxy = chartobj_phi.PPLMPHI_Proxy(chart_obj)
        elif CHART_TYPE == const.CHART_TYPE.RPE:
            pplm_proxy = chartobj_rpe.PPLMRPE_Proxy(chart_obj)
        
        pppsm = tool_funcs.PhigrosPlayManager(chart_obj.note_num)
        pplm = tool_funcs.PhigrosPlayLogicManager(
            pplm_proxy, pppsm,
            getUserData("setting-enableClickSound"),
            lambda ts: Resource["Note_Click_Audio"][ts].play()
        )
        
        root.jsapi.set_attr("PhigrosPlay_KeyDown", lambda t: pplm.pc_click(t - show_start_time))
        root.jsapi.set_attr("PhigrosPlay_KeyUp", lambda t: pplm.pc_release(t - show_start_time))
        root.run_js_code("_PhigrosPlay_KeyDown = PhigrosPlay_KeyEvent(() => {pywebview.api.call_attr('PhigrosPlay_KeyDown', new Date().getTime() / 1000)}, false);")
        root.run_js_code("_PhigrosPlay_KeyUp = PhigrosPlay_KeyEvent(() => {pywebview.api.call_attr('PhigrosPlay_KeyUp', new Date().getTime() / 1000)}, false);")
        root.run_js_code("window.addEventListener('keydown', _PhigrosPlay_KeyDown);")
        root.run_js_code("window.addEventListener('keyup', _PhigrosPlay_KeyUp);")
    else:
        pplm = None
    
    show_start_time = time.time()
    coreConfig.show_start_time = show_start_time
    phicore.CoreConfigure(coreConfig)
    
    def clickEventCallback(x, y):
        global show_start_time
        nonlocal paused, pauseAnimationSt, pauseSt
        nonlocal nextUI, tonextUI, tonextUISt
        
        if rendingAnimationSt != rendingAnimationSt: # nan, playing chart
            pauseATime = 0.25 if paused else 3.0
            pauseP = tool_funcs.fixorp((time.time() - pauseAnimationSt) / pauseATime)
            if not paused and tool_funcs.inrect(x, y, (
                w * 9.6 / 1920, h * -1.0 / 1080,
                w * 96 / 1920, h * 102.6 / 1080
            )) and (time.time() - chartPlayerRenderSt) > 1.25 and pauseP == 1.0:
                paused, pauseAnimationSt = True, time.time()
                mixer.music.pause()
                Resource["Pause"].play()
                pauseSt = time.time()
            
            pauseUIButtonR = (w + h) * 0.0275
            if paused and tool_funcs.inrect(x, y, (
                w * 0.5 - w * 0.1109375 - pauseUIButtonR / 2,
                h * 0.5 - pauseUIButtonR / 2,
                w * 0.5 - w * 0.1109375 + pauseUIButtonR / 2,
                h * 0.5 + pauseUIButtonR / 2
            )):
                eventManager.unregEvent(clickEvent)
                tonextUI, tonextUISt = True, time.time()
                Resource["UISound_4"].play()
                
            elif paused and tool_funcs.inrect(x, y, (
                w * 0.5 - pauseUIButtonR / 2,
                h * 0.5 - pauseUIButtonR / 2,
                w * 0.5 + pauseUIButtonR / 2,
                h * 0.5 + pauseUIButtonR / 2
            )):
                eventManager.unregEvent(clickEvent)
                nextUIBak = nextUI
                nextUI, tonextUI, tonextUISt = lambda: chartPlayerRender(
                    chartAudio = chartAudio,
                    chartImage = chartImage,
                    chartFile = chartFile,
                    startAnimation = False,
                    chart_information = chart_information,
                    blackIn = True,
                    foregroundFrameRender = lambda: None,
                    nextUI = nextUIBak
                ), True, time.time()
                
            elif paused and tool_funcs.inrect(x, y, (
                w * 0.5 + w * 0.1109375 - pauseUIButtonR / 2,
                h * 0.5 - pauseUIButtonR / 2,
                w * 0.5 + w * 0.1109375 + pauseUIButtonR / 2,
                h * 0.5 + pauseUIButtonR / 2
            )):
                paused, pauseAnimationSt = False, time.time()
                
        if rendingAnimation is not phicore.settlementAnimationFrame or (time.time() - rendingAnimationSt) <= 0.5:
            return
        
        if tool_funcs.inrect(x, y, (
            0, 0,
            w * const.FINISH_UI_BUTTON_SIZE, w * const.FINISH_UI_BUTTON_SIZE / 190 * 145
        )):
            eventManager.unregEvent(clickEvent)
            nextUIBak = nextUI
            nextUI, tonextUI, tonextUISt = lambda: chartPlayerRender(
                chartAudio = chartAudio,
                chartImage = chartImage,
                chartFile = chartFile,
                startAnimation = False,
                chart_information = chart_information,
                blackIn = True,
                foregroundFrameRender = lambda: None,
                nextUI = nextUIBak
            ), True, time.time()
            
        elif tool_funcs.inrect(x, y, (
            w - w * const.FINISH_UI_BUTTON_SIZE, h - w * const.FINISH_UI_BUTTON_SIZE / 190 * 145,
            w, h
        )):
            eventManager.unregEvent(clickEvent)
            tonextUI, tonextUISt = True, time.time()
    
    clickEvent = eventManager.regClickEventFs(clickEventCallback, False)
    
    # 前面初始化时间太长了, 放这里
    chartPlayerRenderSt = time.time()
    nextUI, tonextUI, tonextUISt = nextUI, False, float("nan")
    rendingAnimation = phicore.lineCloseAimationFrame
    rendingAnimationSt = float("nan")
    stoped = False
    paused, pauseAnimationSt, pauseSt = False, 0.0, float("nan")
    mixer.music.play()
    
    while True:
        pauseATime = 0.25 if paused else 3.0
        pauseP = tool_funcs.fixorp((time.time() - pauseAnimationSt) / pauseATime)
        pauseBgBlurP = (1.0 - (1.0 - pauseP) ** 4) if paused else 1.0 - pauseP ** 15
        root.run_js_code(f"mask.style.backdropFilter = 'blur({(w + h) / 100 * pauseBgBlurP}px)';", add_code_array = True)
        
        def _renderPauseUIButtons(p: float, dx: float):
            def _drawPauseButton(x: float, imname: str, scale: float):
                ims = (w + h) * 0.0275
                setCtx("dialog_canvas_ctx")
                drawAlphaImage(
                    imname,
                    x - ims / 2, h / 2 - ims / 2,
                    ims * scale, ims * scale,
                    1.0 - (1.0 - p) ** 2,
                    wait_execute = True
                )
                setCtx("ctx")
            _drawPauseButton(w * 0.5 - w * 0.1109375 + dx, "PUIBack", 1.0)
            _drawPauseButton(w * 0.5 + dx, "PUIRetry", 1.0)
            _drawPauseButton(w * 0.5 + w * 0.1109375 + dx, "PUIResume", 0.95)
            
        root.run_js_code(f"dialog_canvas_ctx.clear();", add_code_array = True)
        if paused:
            _renderPauseUIButtons(pauseP, 0.0)
        else:
            pauseUIDrawPLP = 0.2 / 3.0
            if pauseP <= pauseUIDrawPLP:
                puiBsP = pauseP / pauseUIDrawPLP
                _renderPauseUIButtons(1.0 - puiBsP, - w / 15 * (puiBsP ** 4))
            fastEaseX = 3.75
            fastEase = lambda x: rpe_easing.ease_funcs[19](x * fastEaseX) if x <= 1 / fastEaseX else 1.0
            numberEase = lambda x: int(x) + fastEase(x % 1.0)
            root.run_js_code("_ctxBak = ctx; ctx = dialog_canvas_ctx;", add_code_array = True)
            def _drawNumber(number: str, dxv: float):
                if pauseP == 1.0: return
                x = w / 2 - w * 0.1109375 * dxv
                alpha = ((w / 2 - abs(w / 2 - x)) / (w / 2)) ** 25
                if pauseP >= 0.8:
                    alpha *= 1.0 - (1.0 - (1.0 - (pauseP - 0.8) / 0.2) ** 2)
                drawText(
                    x, h / 2,
                    number,
                    font = f"{(w + h) / 30}px PhigrosFont",
                    textAlign = "center",
                    textBaseline = "middle",
                    fillStyle = f"rgba(255, 255, 255, {alpha})",
                    wait_execute=True
                )
            _drawNumber("3", numberEase(pauseP * 3.0) - 1.0)
            _drawNumber("2", numberEase(pauseP * 3.0) - 2.0)
            _drawNumber("1", numberEase(pauseP * 3.0) - 3.0)
            root.run_js_code("ctx = _ctxBak; _ctxBak = null;", add_code_array = True)
        
        if not paused and pauseP == 1.0 and pauseSt == pauseSt and not mixer.music.get_busy():
            mixer.music.unpause()
            show_start_time += time.time() - pauseSt
            coreConfig.show_start_time = show_start_time
            phicore.CoreConfigure(coreConfig)
            pauseSt = float("nan")
        
        if not paused and pauseP == 1.0:
            clearCanvas(wait_execute = True)
        
            if not stoped:
                now_t = time.time() - show_start_time
                checkOffset(now_t)
                if CHART_TYPE == const.CHART_TYPE.PHI:
                    Task = phicore.GetFrameRenderTask_Phi(now_t, False, False, pplm)
                elif CHART_TYPE == const.CHART_TYPE.RPE:
                    Task = phicore.GetFrameRenderTask_Rpe(now_t, False, False, pplm)
                    
                Task.ExecTask()
                
                break_flag = phicore.processExTask(Task.ExTask)
                
                if break_flag and not stoped:
                    phicore.initSettlementAnimation(pplm)
                    rendingAnimationSt = time.time()
                    stoped = True
            else:
                if rendingAnimation is phicore.lineCloseAimationFrame:
                    if time.time() - rendingAnimationSt <= 0.75:
                        rendingAnimation((time.time() - rendingAnimationSt) / 0.75, pplm.ppps.getCombo() if phicore.noautoplay else phicore.chart_obj.note_num, False)
                    else:
                        rendingAnimation, rendingAnimationSt = phicore.settlementAnimationFrame, time.time()
                        mixer.music.load("./resources/Over.mp3")
                        Thread(target=lambda: (time.sleep(0.25), mixer.music.play(-1)), daemon=True).start()
                
                if rendingAnimation is phicore.settlementAnimationFrame: # 不能用elif, 不然会少渲染一个帧
                    rendingAnimation(tool_funcs.fixorp((time.time() - rendingAnimationSt) / 3.5), False)
        
        if time.time() - chartPlayerRenderSt < 1.25 and blackIn:
            p = (time.time() - chartPlayerRenderSt) / 1.25
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {(1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        
        if tonextUI and time.time() - tonextUISt < 0.75:
            p = (time.time() - tonextUISt) / 0.75
            if not paused:
                root.run_js_code(
                    f"ctx.fillRectEx(\
                        0, 0, {w}, {h},\
                        'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                    );",
                    add_code_array = True
                )
            else:
                root.run_js_code("_ctxBak = ctx; ctx = dialog_canvas_ctx;", add_code_array = True)
                root.run_js_code(
                    f"ctx.fillRectEx(\
                        0, 0, {w}, {h},\
                        'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                    );",
                    add_code_array = True
                )
                root.run_js_code("ctx = _ctxBak; _ctxBak = null;", add_code_array = True)
        elif tonextUI:
            clearCanvas(wait_execute = True)
            root.run_js_code(f"dialog_canvas_ctx.clear()", add_code_array = True)
            root.run_js_code(f"mask.style.backdropFilter = 'blur(0px)';", add_code_array = True)
            root.run_js_wait_code()
            Thread(target=nextUI, daemon=True).start()
            break
        
        root.run_js_wait_code()
    
    if phicore.noautoplay:
        root.run_js_code("window.removeEventListener('keydown', _PhigrosPlay_KeyDown);")
        root.run_js_code("window.removeEventListener('keyup', _PhigrosPlay_KeyUp);")
            
    mixer.music.set_volume(1.0)
    cksmanager.stop()

def chooseChartRender(chapter_item: phigame_obj.Chapter):
    illrespacker = webcv.PILResourcePacker(root)
    for song in chapter_item.songs:
        illrespacker.reg_img(open(tool_funcs.gtpresp(song.image), "rb").read(), f"songill_{song.songId}")
    illrespacker.load(*illrespacker.pack())
    
    chooseChartControl = phigame_obj.ChooseChartControl(chapter_item, w, h)
    eventManager.regClickEventFs(chooseChartControl.scter_mousedown, False)
    eventManager.regReleaseEvent(phigame_obj.ReleaseEvent(chooseChartControl.scter_mouseup))
    eventManager.regMoveEvent(phigame_obj.MoveEvent(chooseChartControl.scter_mousemove))
    
    chooseChartRenderSt = time.time()
    nextUI, tonextUI, tonextUISt = None, False, float("nan")
    clickedBackButton = False
    choose_state = phigame_obj.ChartChooseUI_State()
    
    def clickBackButtonCallback(*args):
        nonlocal clickedBackButton
        nonlocal nextUI, tonextUI, tonextUISt
        
        if not clickedBackButton:
            eventManager.unregEvent(clickBackButtonEvent)
            eventManager.unregEvent(clickEvent)
            nextUI, tonextUI, tonextUISt = mainRender, True, time.time()
            mixer.music.fadeout(500)
            Resource["UISound_4"].play()
    
    clickBackButtonEvent = phigame_obj.ClickEvent(
        rect = (0, 0, ButtonWidth, ButtonHeight),
        callback = clickBackButtonCallback,
        once = False
    )
    eventManager.regClickEvent(clickBackButtonEvent)
    
    def clickEventCallback(x, y):
        # 反转排序
        if tool_funcs.inrect(x, y, (
            w * 0.14843750, h * (72 / 1080),
            w * 0.14843750 + SortIconWidth, h * (72 / 1080) + SortIconHeight
        )):
            choose_state.sort_reverse = not choose_state.sort_reverse
        
        # 下一个排序方法
        if tool_funcs.inrect(x, y, (
            w * 0.16875, h * (69 / 1080),
            w * 0.1953125, h * (96 / 1080)
        )):
            choose_state.next_sort_method()
    
    clickEvent = eventManager.regClickEventFs(clickEventCallback, False)
    
    while True:
        clearCanvas(wait_execute = True)
        
        drawBackground()
        drawFaculas()
        
        chartsShadowRect = (
            w * -0.009375, 0,
            w * 0.4921875, h
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, chartsShadowRect))},\
                {tool_funcs.getDPower(*tool_funcs.getSizeByRect(chartsShadowRect), 75)},\
                'rgba(0, 0, 0, 0.3)'\
            );""",
            add_code_array = True
        )
        
        songShadowRect = (
            w * 0.0640625, h * (361 / 1080),
            w * 0.45, h * (505 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, songShadowRect))},\
                {tool_funcs.getDPower(*tool_funcs.getSizeByRect(songShadowRect), 75)},\
                'rgba(0, 0, 0, 0.6)'\
            );""",
            add_code_array = True
        )
        
        barShadowRect = (
            w * 0.121875, h * (12 / 1080),
            w * 0.49375, h * (123 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, barShadowRect))},\
                {tool_funcs.getDPower(*tool_funcs.getSizeByRect(barShadowRect), 75)},\
                'rgba(0, 0, 0, 0.6)'\
            );""",
            add_code_array = True
        )
        
        difRect = (
            w * 0.340625, h * (355 / 1080),
            w * 0.440625, h * (513 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, difRect))},\
                {tool_funcs.getDPower(*tool_funcs.getSizeByRect(difRect), 75)},\
                'rgb(255, 255, 255)'\
            );""",
            add_code_array = True
        )
        
        playButtonRect = (
            w * 0.878125, h * (861 / 1080),
            w * 2.0, h * (1012 / 1080)
        )
        root.run_js_code(
            f"""ctx.drawDiagonalRectangle(\
                {",".join(map(str, playButtonRect))},\
                {tool_funcs.getDPower(*tool_funcs.getSizeByRect(playButtonRect), 75)},\
                'rgb(255, 255, 255)'\
            );""",
            add_code_array = True
        )
        
        root.run_js_code(
            f"""ctx.drawTriangleFrame(\
                {w * 0.93125}, {h * (905 / 1080)},\
                {w * 0.93125}, {h * (967 / 1080)},\
                {w * 0.959375}, {h * (936 / 1080)},\
                'rgb(0, 0, 0)', {(w + h) * 0.001}\
            );""",
            add_code_array = True
        )
        
        drawText(
            w * 0.1484375, h * (34 / 1080),
            "排序方式",
            font = f"{(w + h) / 135}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = f"rgb(255, 255, 255)",
            wait_execute = True
        )
        
        root.run_js_code(
            f"""ctx.drawScaleImage(\
                {root.get_img_jsvarname("sort")},\
                {w * 0.14843750}, {h * (72 / 1080)},\
                {SortIconWidth}, {SortIconHeight},\
                1, {-1 if choose_state.sort_reverse else 1}\
            );""",
            add_code_array = True
        )
        
        drawText(
            w * 0.16875, h * (69 / 1080),
            const.PHI_SORTMETHOD_STRING_MAP[choose_state.sort_method],
            font = f"{(w + h) / 100}px PhigrosFont",
            textAlign = "left",
            textBaseline = "top",
            fillStyle = f"rgb(255, 255, 255)",
            wait_execute = True
        )
        
        drawButton("ButtonLeftBlack", "Arrow_Left", (0, 0))
                
        if time.time() - chooseChartRenderSt < 1.25:
            p = (time.time() - chooseChartRenderSt) / 1.25
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {(1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        
        if tonextUI and time.time() - tonextUISt < 0.75:
            p = (time.time() - tonextUISt) / 0.75
            root.run_js_code(
                f"ctx.fillRectEx(\
                    0, 0, {w}, {h},\
                    'rgba(0, 0, 0, {1.0 - (1.0 - p) ** 2})'\
                );",
                add_code_array = True
            )
        elif tonextUI:
            clearCanvas(wait_execute = True)
            root.run_js_wait_code()
            Thread(target=nextUI, daemon=True).start()
            break
        
        root.run_js_wait_code()
        
    eventManager.unregEventByChooseChartControl(chooseChartControl)
    illrespacker.unload(illrespacker.getnames())
    
def updateFontSizes():
    global userName_FontSize
    
    userName_Width1px = root.run_js_code(f"""ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(getUserData("userdata-userName"))}).width;""") / 50
    userName_FontSize = w * 0.209375 / (userName_Width1px if userName_Width1px != 0.0 else 1.0)
    if userName_FontSize > w * 0.0234375:
        userName_FontSize = w * 0.0234375

def resize(w_: int, h_: int):
    global w, h
    w, h = w_ - dw_legacy, h_ - dh_legacy
    updateFontSizes()

def updateSettingConfig():
    userData.update({
        "setting-chartOffset": PlaySettingWidgets["OffsetSlider"].value,
        "setting-noteScale": PlaySettingWidgets["NoteScaleSlider"].value,
        "setting-backgroundDim": PlaySettingWidgets["BackgroundDimSlider"].value,
        "setting-enableClickSound": PlaySettingWidgets["ClickSoundCheckbox"].checked,
        "setting-musicVolume": PlaySettingWidgets["MusicVolumeSlider"].value,
        "setting-uiVolume": PlaySettingWidgets["UISoundVolumeSlider"].value,
        "setting-clickSoundVolume": PlaySettingWidgets["ClickSoundVolumeSlider"].value,
        "setting-enableMorebetsAuxiliary": PlaySettingWidgets["MorebetsAuxiliaryCheckbox"].checked,
        "setting-enableFCAPIndicator": PlaySettingWidgets["FCAPIndicatorCheckbox"].checked,
        "setting-enableLowQuality": PlaySettingWidgets["LowQualityCheckbox"].checked
    })
    
    Resource["CalibrationHit"].set_volume(getUserData("setting-clickSoundVolume"))

def updateDSPConfig():
    userData.update({
        "internal-dspBufferExponential": dspSettingWidgets["ValueSlider"].value
    })

def updateSettingWidgets():
    PlaySettingWidgets["OffsetLabel"].right_text = f"""{int(getUserData("setting-chartOffset"))}ms"""
    PlaySettingWidgets["OffsetTip"].right_text = "*请调节至第三拍的声音与按键音恰好重合的状态" if getUserData("setting-enableClickSound") else "*请调节至第三拍的声音与按键爆开几乎同时的状态"

def updateDSPWidgets():
    dspSettingWidgets["ValueLabel"].right_text = f"""{2 ** getUserData("internal-dspBufferExponential")}"""

def updateConfig():
    rcfg = userData.copy()
    
    try: updateSettingConfig()
    except KeyError: pass
    try: updateDSPConfig()
    except KeyError: pass
    
    try: updateSettingWidgets()
    except KeyError: pass
    try: updateDSPWidgets()
    except KeyError: pass
    
    if userData != rcfg:
        saveUserData(userData)
    
    if rcfg["setting-enableLowQuality"] != getUserData("setting-enableLowQuality"):
        applyConfig()

def applyConfig():
    if getUserData("setting-enableLowQuality"):
        root.run_js_code(f"""lowquality_scale = {1.0 / webdpr * getUserData("internal-lowQualityScale")};""")
        root.run_js_code(f"""lowquality_imjscvscale_x = {getUserData("internal-lowQualityScale-JSLayer")};""")
        root.run_js_code(f"ctx.imageSmoothingEnabled = false;")
    else:
        root.run_js_code(f"lowquality_scale = {1.0 / webdpr};")
        root.run_js_code(f"lowquality_imjscvscale_x = 1.0;")
        root.run_js_code(f"ctx.imageSmoothingEnabled = true;")
    root.run_js_code(f"resizeCanvas({w}, {h});") # update canvas

root = webcv.WebCanvas(
    width = 1, height = 1,
    x = 0, y = 0,
    title = "PhigrosPlayer - Phigros Simulator",
    debug = "--debug" in sys.argv,
    resizable = "--resizeable" in sys.argv,
    frameless = "--frameless" in sys.argv
)
webdpr = root.run_js_code("window.devicePixelRatio;")
root.run_js_code(f"lowquality_scale = {1.0 / webdpr};")

if "--fullscreen" in sys.argv:
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.resize(w, h)
    root.web.toggle_fullscreen()
    dw_legacy, dh_legacy = 0, 0
else:
    if "--size" not in sys.argv:
        w, h = int(root.winfo_screenwidth() * 0.6), int(root.winfo_screenheight() * 0.6)
    else:
        w, h = int(eval(sys.argv[sys.argv.index("--size") + 1])), int(eval(sys.argv[sys.argv.index("--size") + 2]))
    winw, winh = (
        w if w <= root.winfo_screenwidth() else int(root.winfo_screenwidth() * 0.75),
        h if h <= root.winfo_screenheight() else int(root.winfo_screenheight() * 0.75)
    )
    root.resize(winw, winh)
    w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
    dw_legacy, dh_legacy = winw - w_legacy, winh - h_legacy
    dw_legacy *= webdpr; dh_legacy *= webdpr
    dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
    del w_legacy, h_legacy
    root.resize(winw + dw_legacy, winh + dh_legacy)
    root.move(int(root.winfo_screenwidth() / 2 - (winw + dw_legacy) / webdpr / 2), int(root.winfo_screenheight() / 2 - (winh + dh_legacy) / webdpr / 2))

w *= webdpr; h *= webdpr; w = int(w); h = int(h)

root.reg_event("resized", resize)
root.run_js_code(f"resizeCanvas({w}, {h});")

if "--window-host" in sys.argv:
    windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))

Load_Chapters()
Resource = Load_Resource()
eventManager = phigame_obj.EventManager()
bindEvents()
updateFontSizes()
applyConfig()
Thread(target=showStartAnimation, daemon=True).start()
    
root.wait_for_close()
windll.kernel32.ExitProcess(0)
