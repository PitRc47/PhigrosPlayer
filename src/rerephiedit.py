from __future__ import annotations

import err_processer as _
import init_logging as _
import fix_workpath as _
import import_argvs as _
import check_edgechromium as _
import check_bin as _

import json
import sys
import time
import datetime
import logging
import typing
import random
import math
import hashlib
from threading import Thread
from os import popen, mkdir
from os.path import exists, isfile
from shutil import rmtree
from ntpath import basename

import requests
from PIL import Image, ImageFilter
from pydub import AudioSegment

import webcv
import dxsound
import const
import uilts
import dialog
import info_loader
import ppr_help
import file_loader
import phira_respack
import phicore
import tempdir
import socket_webviewbridge
import wcv2matlike
import needrelease
import phichart
import phigame_obj
import rpe_easing
import dxsmixer_unix
from dxsmixer import mixer
from exitfunc import exitfunc
from graplib_webview import *

import load_extended as _

RRPEConfig_default = {
    "charts": []
}

RRPEConfig_chart_default = {
    "id": None,
    "name": "",
    "composer": "",
    "illustrator": "",
    "charter": "",
    "level": "UK Lv.1",
    "chartPath": None,
    "illuPath": None,
    "musicPath": None,
    "stdBpm": 140.0,
    "group": "Default"
}

def saveRRPEConfig():
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(RRPEConfig, indent=4, ensure_ascii=False))
    except Exception as e:
        logging.error(f"config save failed: {e}")

def loadRRPEConfig():
    global RRPEConfig
    
    RRPEConfig = RRPEConfig_default.copy()
    try:
        RRPEConfig.update(json.loads(open(CONFIG_PATH, "r", encoding="utf-8").read()))
    except Exception as e:
        logging.error(f"config load failed: {e}")

def getConfigData(key: str):
    return RRPEConfig.get(key, RRPEConfig_default[key])

def setConfigData(key: str, value: typing.Any):
    RRPEConfig[key] = value

try: mkdir("./rrpe_data")
except Exception as e: logging.error(f"rrpe_data mkdir failed: {e}")

CONFIG_PATH = "./rrpe_data/rrpe_config.json"
CHARTS_PATH = "./rrpe_data/charts"

try: mkdir(CHARTS_PATH)
except Exception as e: logging.error(f"charts mkdir failed: {e}")

loadRRPEConfig()

for chart in getConfigData("charts"):
    chart_bak = chart.copy()
    chart.clear()
    chart.update(RRPEConfig_chart_default)
    chart.update(chart_bak)

saveRRPEConfig()

def loadResource():
    global globalNoteWidth
    global note_max_width, note_max_height
    global note_max_size_half
    global WaitLoading, LoadSuccess
    global chart_res
    global cksmanager
    
    logging.info("Loading Resource...")
    WaitLoading = mixer.Sound("./resources/WaitLoading.mp3")
    LoadSuccess = mixer.Sound("./resources/LoadSuccess.wav")
    LoadSuccess.set_volume(0.75)
    globalNoteWidth = w * const.NOTE_DEFAULTSIZE
    
    phi_rpack = phira_respack.PhiraResourcePack("./resources/resource_packs/default")
    phi_rpack.setToGlobal()
    phi_rpack.printInfo()
    
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
        "challenge_mode_levels": [
            Image.open(f"./resources/challenge_mode_levels/{i}.png")
            for i in range(6)
        ],
        "le_warn": Image.open("./resources/le_warn.png"),
        "Retry": Image.open("./resources/Retry.png"),
        "Arrow_Right": Image.open("./resources/Arrow_Right.png"),
        "Over": mixer.Sound("./resources/Over.mp3"),
        "Pause": mixer.Sound("./resources/Pause.wav"),
        "PauseImg": Image.open("./resources/Pause.png"),
        "ButtonLeftBlack": Image.open("./resources/Button_Left_Black.png"),
        "ButtonRightBlack": None
    }
    
    Resource.update(phi_rpack.createResourceDict())
    
    respacker = webcv.LazyPILResPacker(root)
    
    Resource["ButtonRightBlack"] = Resource["ButtonLeftBlack"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    
    for k, v in Resource["Notes"].items():
        respacker.reg_img(Resource["Notes"][k], f"Note_{k}")
    
    for i in range(phira_respack.globalPack.effectFrameCount):
        respacker.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
        respacker.reg_img(Resource["Note_Click_Effect"]["Good"][i], f"Note_Click_Effect_Good_{i + 1}")
        
    for k,v in Resource["levels"].items():
        respacker.reg_img(v, f"Level_{k}")
    
    for i, v in enumerate(Resource["challenge_mode_levels"]):
        respacker.reg_img(v, f"cmlevel_{i}")
        
    respacker.reg_img(Resource["le_warn"], "le_warn")
    respacker.reg_img(Resource["Retry"], "Retry")
    respacker.reg_img(Resource["Arrow_Right"], "Arrow_Right")
    respacker.reg_img(Resource["PauseImg"], "PauseImg")
    respacker.reg_img(Resource["ButtonLeftBlack"], "ButtonLeftBlack")
    respacker.reg_img(Resource["ButtonRightBlack"], "ButtonRightBlack")
    
    chart_res = {}
        
    root.reg_res(open("./resources/font.ttf", "rb").read(), "pgrFont.ttf")
    root.reg_res(open("./resources/font-thin.ttf", "rb").read(), "pgrFontThin.ttf")
    respacker.load(*respacker.pack())
    
    root.wait_jspromise(f"loadFont('pgrFont', \"{root.get_resource_path("pgrFont.ttf")}\");")
    root.wait_jspromise(f"loadFont('pgrFontThin', \"{root.get_resource_path("pgrFontThin.ttf")}\");")
    root.unreg_res("pgrFont.ttf")
    root.unreg_res("pgrFontThin.ttf")
    
    # root.file_server.shutdown()
    note_max_width = globalNoteWidth * phira_respack.globalPack.dub_fixscale
    note_max_height = max((
        note_max_width / Resource["Notes"]["Tap"].width * Resource["Notes"]["Tap"].height,
        note_max_width / Resource["Notes"]["Tap_dub"].width * Resource["Notes"]["Tap_dub"].height,
        note_max_width / Resource["Notes"]["Drag"].width * Resource["Notes"]["Drag"].height,
        note_max_width / Resource["Notes"]["Drag_dub"].width * Resource["Notes"]["Drag_dub"].height,
        note_max_width / Resource["Notes"]["Flick"].width * Resource["Notes"]["Flick"].height,
        note_max_width / Resource["Notes"]["Flick_dub"].width * Resource["Notes"]["Flick_dub"].height,
        note_max_width / Resource["Notes"]["Hold_Head"].width * Resource["Notes"]["Hold_Head"].height,
        note_max_width / Resource["Notes"]["Hold_Head_dub"].width * Resource["Notes"]["Hold_Head_dub"].height,
        note_max_width / Resource["Notes"]["Hold_End"].width * Resource["Notes"]["Hold_End"].height
    ))
    note_max_size_half = ((note_max_width ** 2 + note_max_height ** 2) ** 0.5) / 2
                
    shaders = {
        "chromatic": open("./shaders/chromatic.glsl", "r", encoding="utf-8").read(),
        "circleBlur": open("./shaders/circle_blur.glsl", "r", encoding="utf-8").read(),
        "fisheye": open("./shaders/fisheye.glsl", "r", encoding="utf-8").read(),
        "glitch": open("./shaders/glitch.glsl", "r", encoding="utf-8").read(),
        "grayscale": open("./shaders/grayscale.glsl", "r", encoding="utf-8").read(),
        "noise": open("./shaders/noise.glsl", "r", encoding="utf-8").read(),
        "pixel": open("./shaders/pixel.glsl", "r", encoding="utf-8").read(),
        "radialBlur": open("./shaders/radial_blur.glsl", "r", encoding="utf-8").read(),
        "shockwave": open("./shaders/shockwave.glsl", "r", encoding="utf-8").read(),
        "vignette": open("./shaders/vignette.glsl", "r", encoding="utf-8").read()
    }
    
    cksmanager = phicore.ClickSoundManager(Resource["Note_Click_Audio"])
    logging.info("Load Resource Successfully")
    return Resource

logging.info("Loading Window...")
root = webcv.WebCanvas(
    width = 1, height = 1,
    x = -webcv.screen_width, y = -webcv.screen_height,
    title = "phispler - editor",
    debug = "--debug" in sys.argv,
    resizable = False,
    renderdemand = True, renderasync = True
)

def updateCoreConfig(chart_config: dict, editor: ChartEditor):
    chart_information = {
        "Name": chart_config["name"],
        "Artist": chart_config["composer"],
        "Level": chart_config["level"],
        "Illustrator": chart_config["illustrator"],
        "Charter": chart_config["charter"],
        "BackgroundDim": 0.6
    }
    
    phicore.CoreConfigure(phicore.PhiCoreConfig(
        SETTER = lambda vn, vv: globals().update({vn: vv}),
        root = root, w = w, h = h,
        chart_information = chart_information,
        chart_obj = editor.chart,
        Resource = Resource,
        globalNoteWidth = globalNoteWidth,
        note_max_size_half = note_max_size_half,
        raw_audio_length = raw_audio_length,
        chart_res = chart_res,
        cksmanager = cksmanager,
        showfps = True,
        # debug = True, 
        combotips = "EDITOR",
    ))
    
class UIManager:
    def __init__(self):
        self.uiItems: list[BaseUI] = []
    
    def bind_events(self):
        def _bind_event(name: str, target_name: str, args_eval: str):
            apiname = f"uim_event_{target_name}"
            root.jsapi.set_attr(apiname, lambda *args: self._event_proxy(target_name, *args))
            root.run_js_code(f"window.addEventListener(\"{name}\", e => pywebview.api.call_attr(\"{apiname}\", {args_eval}));")
        
        _bind_event("mousemove", "mouse_move", "e.x, e.y")
        _bind_event("mousedown", "mouse_down", "e.x, e.y, e.button")
        _bind_event("mouseup", "mouse_up", "e.x, e.y, e.button")
        _bind_event("wheel", "mouse_wheel", "e.x, e.y, e.deltaY")
        _bind_event("keydown", "key_down", "e.key")
    
    def render(self, tag: str):
        for ui in self.uiItems:
            if ui.tag == tag:
                ui.render()
    
    def _event_proxy(self, name: str, *args):
        for ui in self.uiItems:
            getattr(ui, name)(*args)
    
    def extend_uiitems(self, items: list[BaseUI], tag: str):
        for item in items:
            item.tag = tag
            
        self.uiItems.extend(items)
    
    def remove_uiitems(self, tag: str):
        for i in self.uiItems.copy():
            if i.tag == tag:
                i.when_remove()
                self.uiItems.remove(i)
    
    def get_input_value_bytag(self, tag: str):
        for ui in self.uiItems:
            if isinstance(ui, Input) and ui.value_tag == tag:
                return ui.text

class BaseUI:
    tag: typing.Optional[str] = None
    
    def render(self): ...
    def mouse_move(self, x: int, y: int): ...
    def mouse_down(self, x: int, y: int, i: int): ...
    def mouse_up(self, x: int, y: int, i: int): ...
    def mouse_wheel(self, x: int, y: int, d: int): ...
    def key_down(self, k: str): ...
    def key_up(self, k: int): ...
    def when_remove(self): ...

class Button(BaseUI):
    def __init__(
        self,
        x: float, y: float,
        text: str, color: str,
        command: typing.Optional[typing.Callable[[float, float], None]] = None,
        test: typing.Optional[typing.Callable[[float, float], bool]] = None,
        size: typing.Optional[tuple[int, int]] = None,
        fontscale: float = 1.0,
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.fontscale = fontscale
        self.rect = const.EMPTY_RECT
        self.command = command
        self.test = test
        self.size = size
        self.mouse_isin = False
        
        self.scale_value_tr = phigame_obj.valueTranformer(rpe_easing.ease_funcs[9], 0.3)
        self.scale_value_tr.target = 1.0
    
    def render(self):
        self.rect = drawRPEButton(
            self.x, self.y,
            self.text, self.color,
            scale = self.scale_value_tr.value,
            **({} if self.size is None else {"size": self.size}),
            fontscale = self.fontscale
        )
    
    def mouse_move(self, x: int, y: int):
        isin = uilts.inrect(x, y, self.rect)
        
        if isin != self.mouse_isin:
            self.scale_value_tr.target = 1.1 if isin else 1.0
            self.mouse_isin = isin
    
    def mouse_down(self, x: int, y: int, _):
        if uilts.inrect(x, y, self.rect) and self.command is not None:
            if self.test is None or self.test(x, y):
                self.command(x, y)

class Label(BaseUI):
    def __init__(
        self,
        x: float, y: float,
        text: str, color: str,
        font: str,
        textAlign: str = "left",
        textBaseline: str = "top"
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.textAlign = textAlign
        self.textBaseline = textBaseline

    def render(self):
        drawText(
            self.x, self.y,
            self.text,
            font = self.font,
            fillStyle = self.color,
            textAlign = self.textAlign,
            textBaseline = self.textBaseline,
            wait_execute = True
        )

class Input(BaseUI):
    def __init__(
        self,
        x: float, y: float,
        text: str, font: str,
        width: float, height: float,
        default_text: typing.Optional[str] = None,
        value_tag: typing.Optional[str] = None
    ):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.width = width
        self.height = height
        self.default_text = default_text
        self.value_tag = value_tag
        self.id = random.randint(0, 2 << 31)
        
        self.removed = False
    
    def render(self):
        if self.removed:
            return
        
        fillRectEx(self.x, self.y, self.width, self.height, "rgba(255, 255, 255, 0.5)", wait_execute=True)
        strokeRectEx(self.x, self.y, self.width, self.height, "white", (w + h) / 650, wait_execute=True)
        
        self.text = root.run_js_code(f"updateCanvasInput({self.id}, {self.x}, {self.y}, {self.width}, {self.height}, \"{self.font}\", {repr(self.default_text) if self.default_text is not None else "null"})")
    
    def when_remove(self):
        self.removed = True
        root.run_js_code(f"removeCanvasInput({self.id})")

class MessageShower(BaseUI):
    def __init__(self):
        self.msgs: list[Message] = []
        self.max_show_time = 2.0
        self.padding_y = h / 50
    
    def render(self):
        for msg in self.msgs.copy():
            if time.time() - msg.st > self.max_show_time + msg.left_tr.animation_time:
                self.msgs.remove(msg)
                continue
            elif time.time() - msg.st > self.max_show_time and not msg.timeout:
                msg.timeout = True
                msg.top_tr.target -= self.padding_y
                msg.alpha_tr.target = 0.0
                
                for msg2 in self.msgs:
                    msg2.top_tr.target -= msg2.height + self.padding_y
            
            rect = (
                msg.left_tr.value,
                msg.top_tr.value,
                msg.left_tr.value + msg.width,
                msg.top_tr.value + msg.height
            )
            
            ctxSave(wait_execute=True)
            ctxMutGlobalAlpha(msg.alpha_tr.value, wait_execute=True)
            
            fillRectEx(*uilts.xxyy_rect2_xywh(rect), msg.color, wait_execute=True)
            drawText(
                rect[0] + msg.padding_x,
                rect[1] + msg.height / 2,
                msg.text,
                font = msg.font,
                fillStyle = "white",
                textAlign = "left",
                textBaseline = "middle",
                wait_execute = True
            )
            
            timeout_p = uilts.fixorp((time.time() - msg.st) / self.max_show_time)
            timeout_height = msg.padding_y * 0.4
            fillRectEx(
                rect[0],
                rect[1] + (rect[3] - rect[1]) - timeout_height,
                (rect[2] - rect[0]) * timeout_p,
                timeout_height,
                "rgba(255, 255, 255, 0.4)",
                wait_execute = True
            )
            
            ctxRestore(wait_execute=True)
    
    def submit(self, msg: Message):
        vaild_msgs = [i for i in self.msgs if not i.timeout]
        
        msg.top_tr.target = max(
            self.padding_y
            if not vaild_msgs else
            (vaild_msgs[-1].top_tr.target + vaild_msgs[-1].height + self.padding_y),
            
            self.padding_y
        )
        self.msgs.append(msg)

class Message:
    INFO_COLOR = "skyblue"
    WARNING_COLOR = "orange"
    ERROR_COLOR = "red"
    
    TEXT_SIZE = 79
    
    def __init__(self, text: str, color: str):
        self.text = text
        self.font = f"{(w + h) / Message.TEXT_SIZE}px pgrFont"
        self.color = color
        self.st = time.time()
        self.timeout = False
        
        textsize = root.run_js_code(f"ctx.getTextSize({root.string2sctring_hqm(text)}, \"{self.font}\");")
        self.padding_x = w / 75
        self.padding_y = h / 65
        self.width = textsize[0] + self.padding_x * 2
        self.height = textsize[1] + self.padding_y * 2
        
        self.left_tr = phigame_obj.valueTranformer(rpe_easing.ease_funcs[9])
        self.left_tr.target = w * 1.1
        self.left_tr.target = w - self.width - w / 60
        
        self.top_tr = phigame_obj.valueTranformer(rpe_easing.ease_funcs[9])
        
        self.alpha_tr = phigame_obj.valueTranformer(rpe_easing.ease_funcs[9])
        self.alpha_tr.target = 1.0

class ChartChooser(BaseUI):
    def __init__(
        self,
        change_test: typing.Optional[typing.Callable[[], bool]] = None,
        when_change: typing.Optional[typing.Callable[[], None]] = None
    ):
        self.last_chart = None
        self.last_call_wc = time.time()
        self.i = 0
        self.dc = 0
        
        self.change_test = change_test
        self.when_change = when_change
        self.tr_map: dict[str, tuple[phigame_obj.valueTranformer, ...]] = {}
    
    def get_chart_tr_values(self, i: int, is_chosing: bool, chosing_index: int):
        size = pos1k(800, 450) if is_chosing else pos1k(508, 285)
        center_pos = uilts.getCenterPointByRect((*pos1k(141, 315), *pos1k(940, 765)))
        
        if not is_chosing:
            di = i - chosing_index
            di_less = (di - 1) if di > 0 else (di + 1)
            center_pos = (
                center_pos[0] + (pos1k(800, 0)[0] / 2 * (1 if di > 0 else -1)) + (di * pos1k(303.5, 0)[0] + di_less * pos1k(253.5, 0)[0]),
                pos1k(0, 640)[1]
            )
            
        return (
            size,
            center_pos
        )
    
    def update(self, charts: list[dict]):
        self.i += self.dc
        self.dc = 0
        
        if charts:
            self.i %= len(charts)
        else:
            return
        
        chosing_chart = charts[self.i]
        
        if chosing_chart != self.last_chart and time.time() - self.last_call_wc > 0.3:
            self.last_chart = chosing_chart
            self.last_call_wc = time.time()
            if self.when_change is not None:
                self.when_change()
        
        all_ids = []
        for i, chart in enumerate(charts):
            chart_id = chart["id"]
            all_ids.append(chart_id)
            
            if chart_id not in self.tr_map:
                self.tr_map[chart_id] = tuple(
                    phigame_obj.valueTranformer(rpe_easing.ease_funcs[9])
                    for _ in range(4)
                )
                
            tr_values = self.get_chart_tr_values(i, chart is chosing_chart, self.i)
            def _set(i: int, v: float):
                if self.tr_map[chart_id][i].target != v:
                    self.tr_map[chart_id][i].target = v
            
            _set(0, tr_values[0][0])
            _set(1, tr_values[0][1])
            _set(2, tr_values[1][0])
            _set(3, tr_values[1][1])
        
        for k in self.tr_map.copy().keys():
            if k not in all_ids:
                self.tr_map.pop(k)
    
    def key_down(self, k: str):
        if self.change_test is None or self.change_test():
            if k == "ArrowLeft":
                self.dc -= 1
            elif k == "ArrowRight":
                self.dc += 1
            else:
                return

class ChartEditor:
    def __init__(self, chart: phichart.CommonChart):
        self.chart = chart
        
        self.step_dumps: list[bytes] = []
        self.can_undo = False
        self.now_step_i = -1
        self.last_chart_now_t = 0
        self.paused = True
    
    def emit_command(self, command: EditBaseCmd):
        self.new_dump()
        self.can_undo = True
        
        if isinstance(command, ...):
            ...
            
        elif isinstance(command, EditBaseCmd):
            pass
        else:
            assert False, f"Unknown command type: {type(command)}"
    
    def new_dump(self):
        if self.can_undo:
            if self.now_step_i < len(self.step_dumps) - 1:
                self.step_dumps = self.step_dumps[:self.now_step_i + 1]
            
        self.step_dumps.append(self.chart.dump())
        self.now_step_i += 1
    
    def undo(self):
        if self.can_undo:
            self.now_step_i -= 1
            self.load_chart_from_dumps()
    
    def load_chart_from_dumps(self):
        self.chart = phichart.CommonChart.loaddump(self.step_dumps[self.now_step_i])
    
    def pause_play(self):
        self.paused = True
        mixer.music.pause()
        
    def unpause_play(self):
        self.paused = False
        mixer.music.unpause()
    
    def seek_by(self, delta: float):
        mixer.music.set_pos(mixer.music.get_pos() + delta)
    
    def update(self):
        ...

    def when_timejump(self, new_t: float):
        self.chart.fast_init()
        
        for line in self.chart.lines:
            for note in line.notes:
                note.isontime = note.time < new_t
    
    @property
    def chart_now_t(self) -> float:
        ret = mixer.music.get_pos()
        
        if ret < self.last_chart_now_t:
            self.when_timejump(ret)
        
        self.last_chart_now_t = ret
        return ret

class EditBaseCmd:
    ...

class Edit_NewNote(EditBaseCmd):
    def __init__(self, note: phichart.Note):
        self.note = note
    
def drawRPEButton(
    x: float, y: float,
    text: str, color: str,
    *,
    scale: float = 1.0,
    size: tuple[int, int] = (341, 84),
    fontscale: float = 1.0
):
    button_size = pos1k(*size)
    x, y = (x + button_size[0] / 2, y + button_size[1] / 2)
    rect = (
        x - button_size[0] / 2 * scale,
        y - button_size[1] / 2 * scale,
        x + button_size[0] / 2 * scale,
        y + button_size[1] / 2 * scale
    )
    
    xywh_rect = uilts.xxyy_rect2_xywh(rect)
    
    ctxSave(wait_execute=True)
    ctxMutGlobalAlpha(0.8, wait_execute=True)
    fillRectEx(*xywh_rect, color, wait_execute=True)
    ctxRestore(wait_execute=True)
    
    strokeRectEx(*xywh_rect, color, (w + h) / 650 * scale * fontscale, wait_execute=True)
    strokeRectEx(*xywh_rect, "rgba(255, 255, 255, 0.4)", (w + h) / 650 * scale * fontscale, wait_execute=True)
    
    drawText(
        *uilts.getCenterPointByRect(rect),
        text,
        font = f"{(w + h) / 75 * scale * fontscale}px pgrFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "white",
        wait_execute = True
    )
    
    return rect

def pos1k(x: float, y: float):
    return w * (x / 1920), h * (y / 1080)

def createNewChartId():
    dt = datetime.datetime.now()
    return f"{dt.year}.{dt.month}.{dt.day}.{dt.hour}.{dt.minute}.{dt.second}.{dt.microsecond}-{random.randint(0, 1024)}"

def hashChartId(chart_id: str):
    return "hash_" + hashlib.md5(chart_id.encode("utf-8")).hexdigest()

def web_alert(msg: str):
    root.run_js_code(f"alert({root.string2sctring_hqm(msg)});")

def web_prompt(msg: str) -> typing.Optional[str]:
    return root.run_js_code(f"prompt({root.string2sctring_hqm(msg)});")

def web_confirm(msg: str) -> bool:
    return root.run_js_code(f"confirm({root.string2sctring_hqm(msg)});")

def editorRender(chart_config: dict):
    global raw_audio_length
    
    mixer.music.stop()
    mixer.music.unload()
    
    chart = phichart.CommonChart.loaddump(open(chart_config["chartPath"], "rb").read())
    editor = ChartEditor(chart)
    
    respacker = webcv.LazyPILResPacker(root)
    
    chart_image = Image.open(chart_config["illuPath"])
    
    if chart_image.mode != "RGB":
        chart_image = chart_image.convert("RGB")
    
    background_image_blur = chart_image.filter(ImageFilter.GaussianBlur(sum(chart_image.size) / 50))
    respacker.reg_img(background_image_blur, "background_blur")
    respacker.reg_img(chart_image, "chart_image")
    
    respacker.load(*respacker.pack())
    
    mixer.music.load(chart_config["musicPath"])
    mixer.music.play()
    mixer.music.pause()
    
    raw_audio_length = mixer.music.get_length()
    updateCoreConfig(chart_config, editor)
    
    nextUI = None
    
    editor.unpause_play()
    
    while True:
        clearCanvas(wait_execute=True)
        
        editor.update()
        extasks = phicore.renderChart_Common(editor.chart_now_t, clear=False, rjc=False)
        phicore.processExTask(extasks)
        
        editor.seek_by(random.uniform(-1/30,1/15))
        
        globalUIManager.render("global")
        
        root.run_js_wait_code()
        
        if nextUI is not None:
            globalUIManager.remove_uiitems("editorRender")
            respacker.unload(respacker.getnames())
            Thread(target=nextUI, daemon=True).start()
            return

def mainRender():
    nextUI = None
    
    topButtonLock = False
    createChartData = None
    needUpdateIllus = False
    
    illuPacker: typing.Optional[webcv.LazyPILResPacker] = None
    def updateIllus():
        nonlocal illuPacker
        
        if illuPacker is not None:
            illuPacker.unload(illuPacker.getnames())
        
        illuPacker = webcv.LazyPILResPacker(root)
        
        for chart in getConfigData("charts"):
            illuPacker.reg_img(chart["illuPath"], f"illu_{hashChartId(chart["id"])}")
        
        illuPacker.load(*illuPacker.pack())
    
    def createChart(*_):
        nonlocal createChartData, topButtonLock
        
        topButtonLock = True
        
        music_file = dialog.openfile(Filter="音乐文件 (*.mp3;*.wav;*.ogg)|*.mp3;*.wav;*.ogg|所有文件 (*.*)|*.*")
        if music_file is None or not isfile(music_file):
            topButtonLock = False
            return
        
        illu_file = dialog.openfile(Filter="图片文件 (*.png;*.jpg;*.jpeg)|*.png;*.jpg;*.jpeg|所有文件 (*.*)|*.*", fn="可跳过  can be skipped")
        if illu_file is None or not isfile(illu_file):
            illu_file = "./resources/transparent_blocks.png"
        
        createChartData = {
            "music": music_file,
            "illu": illu_file
        }
        
        def _cancal(*_):
            nonlocal createChartData
            
            globalUIManager.remove_uiitems("mainRender-createChart")
            createChartData = None
        
        def _confirm(*_):
            nonlocal createChartData, needUpdateIllus
            
            userInputData = {
                k: globalUIManager.get_input_value_bytag(k)
                for k in ["chartName", "chartComposer", "chartCharter", "chartBPM", "chartLines"]
            }
            
            try:
                v = float(userInputData["chartBPM"])
                if math.isnan(v) or math.isinf(v) or v == 0.0:
                    raise ValueError
            except Exception:
                globalMsgShower.submit(Message("请输入有效的BPM", Message.ERROR_COLOR))
                return
            
            try:
                v = int(userInputData["chartLines"])
                if v < 0:
                    raise ValueError
            except Exception:
                globalMsgShower.submit(Message("请输入有效的线数", Message.ERROR_COLOR))
                return
            
            createChartData.update(userInputData)
            
            chart_config = RRPEConfig_chart_default.copy()
            chart_config["name"] = createChartData["chartName"]
            chart_config["composer"] = createChartData["chartComposer"]
            chart_config["charter"] = createChartData["chartCharter"]
            chart_config["stdBpm"] = float(createChartData["chartBPM"])
            chart_config["id"] = createNewChartId()
            
            chart_id = chart_config["id"]
            
            try: mkdir(f"{CHARTS_PATH}/{chart_id}")
            except Exception: logging.error(f"chart mkdir failed: {e}")
            
            chart_obj = phichart.CommonChart(lines=[phichart.JudgeLine() for _ in range(int(createChartData["chartLines"]))])
            
            with open(f"{CHARTS_PATH}/{chart_id}/chart.bpc", "wb") as f:
                f.write(chart_obj.dump())
            
            try: illu = Image.open(createChartData["illu"])
            except Exception:
                illu = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
                logging.error(f"illu open failed: {e}")
            
            illu.save(f"{CHARTS_PATH}/{chart_id}/image.png", format="PNG")
            
            try:
                seg: AudioSegment = AudioSegment.from_file(createChartData["music"])
                seg.export(f"{CHARTS_PATH}/{chart_id}/music.wav", format="wav")
            except Exception:
                globalMsgShower.submit(Message("音频读取失败", Message.ERROR_COLOR))
                rmtree(f"{CHARTS_PATH}/{chart_id}")
                return
            
            chart_config["chartPath"] = f"{CHARTS_PATH}/{chart_id}/chart.bpc"
            chart_config["illuPath"] = f"{CHARTS_PATH}/{chart_id}/image.png"
            chart_config["musicPath"] = f"{CHARTS_PATH}/{chart_id}/music.wav"
            
            getConfigData("charts").append(chart_config)
            saveRRPEConfig()
            needUpdateIllus = True
            
            globalUIManager.remove_uiitems("mainRender-createChart")
            createChartData = None
        
        globalUIManager.extend_uiitems(uilts.unfold_list([
            [
                Label(*pos1k(586, 283 + 133 * i), name, "white", f"{(w + h) / 75}px pgrFont", textBaseline="middle"),
                Input(*pos1k(885, 253 + 133 * i), "", f"{(w + h) / 95}px pgrFont", *pos1k(500, 60), default_text[0] if default_text else None, key)
            ]
            for i, (name, key, *default_text) in enumerate([
                ("谱面名称", "chartName"),
                ("作曲者", "chartComposer"),
                ("谱面设计", "chartCharter"),
                ("基础BPM", "chartBPM", "140"),
                ("基础线数", "chartLines", "24")
            ])
        ] + [
            Button(*pos1k(529, 883), "取消", "red", _cancal, size=(210, 71), fontscale=0.9),
            Button(*pos1k(1183, 883), "确定", "green", _confirm, size=(210, 71), fontscale=0.9),
        ]), "mainRender-createChart")
        
        topButtonLock = False
    
    def deleteChart(*_):
        nonlocal needUpdateIllus
        
        charts = getConfigData("charts")
        
        if not charts:
            globalMsgShower.submit(Message("你还没有谱面可以删除...", Message.ERROR_COLOR))
            return
        
        chooser.update(charts)
        chosing_chart = charts[chooser.i]
        
        if web_confirm(f"你确定要删除谱面 \"{chosing_chart["name"]}\" 吗？\n这个操作不可逆！\n你真的要删除吗？这个谱面会丢失很久（真的很久！）\n\n谱面 config: {json.dumps(chosing_chart, indent=4, ensure_ascii=False)}"):
            charts.remove(chosing_chart)
            dxsmixer_unix.mixer.music.stop()
            dxsmixer_unix.mixer.music.unload()
            
            try: rmtree(f"{CHARTS_PATH}/{chosing_chart["id"]}")
            except Exception as e: logging.error(f"chart rmtree failed: {e}")
            
            saveRRPEConfig()
            needUpdateIllus = True
    
    def gotoEditor(*_):
        nonlocal nextUI
        
        charts = getConfigData("charts")
        
        if not charts:
            globalMsgShower.submit(Message("你还没有谱面可以编辑...", Message.ERROR_COLOR))
            return
        
        chart_config = charts[chooser.i]
        nextUI = lambda: editorRender(chart_config)
    
    def can_click_top_button(*_):
        return (
            not topButtonLock and
            createChartData is None
        )
    
    def chooser_when_change():
        chart = getConfigData("charts")[chooser.i]
        
        def _play_preview():
            try:
                dxsmixer_unix.mixer.music.load(chart["musicPath"])
                dxsmixer_unix.mixer.music.play(-1)
            except Exception as e:
                logging.error(f"music play failed: {e}")
                globalMsgShower.submit(Message(f"音频播放失败: {e}", Message.ERROR_COLOR))
                return
        
        Thread(target=_play_preview, daemon=True).start()
    
    uiItems = [
        Button(*pos1k(80, 51), "创建谱面", "green", createChart, can_click_top_button),
        Button(*pos1k(462, 51), "导入谱面", "gray", None, can_click_top_button),
        Button(*pos1k(846, 51), "导出谱面", "gray", None, can_click_top_button),
        Button(*pos1k(1124, 192), "分组显示", "gray", None, can_click_top_button),
        Button(*pos1k(1507, 192), "排序方式", "gray", None, can_click_top_button),
        Button(*pos1k(78, 957), "删除谱面", "red", deleteChart, can_click_top_button),
        Button(*pos1k(1127, 957), "修改谱面信息", "yellow", None, can_click_top_button),
        Button(*pos1k(1509, 957), "进入编辑", "green", gotoEditor, can_click_top_button),
    ]
    
    chooser = ChartChooser(
        change_test=can_click_top_button,
        when_change=chooser_when_change
    )
    
    uiItems.append(chooser)
    globalUIManager.extend_uiitems(uiItems, "mainRender")
    updateIllus()
    
    while True:
        clearCanvas(wait_execute=True)
        
        if not getConfigData("charts"):
            drawText(
                w / 2, h / 2,
                "点击 “创建谱面” 后选择音乐、曲绘来创建你的第一张谱面",
                font = f"{(w + h) / 65}px pgrFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "white",
                wait_execute = True
            )
        else:
            charts = getConfigData("charts")
            chooser.update(charts)
            chosing_chart = charts[chooser.i]
            
            ctxSave(wait_execute=True)
            bgBlurRatio = (w + h) / 50
            bgScale = max((w + bgBlurRatio) / w, (h + bgBlurRatio) / h)
            ctxSetFilter(f"blur({bgBlurRatio}px)", wait_execute=True)
            ctxTranslate(w / 2, h / 2, wait_execute=True)
            ctxScale(bgScale, bgScale, wait_execute=True)
            ctxTranslate(-w / 2 * bgScale, -h / 2 * bgScale, wait_execute=True)
            drawCoverFullScreenImage(
                f"illu_{hashChartId(chosing_chart["id"])}",
                w * bgScale, h * bgScale, wait_execute=True
            )
            ctxRestore(wait_execute=True)
            
            fillRectEx(0, 0, w, h, "rgba(0, 0, 0, 0.6)", wait_execute=True)
            
            drawText(
                *pos1k(161, 202),
                chosing_chart["level"],
                font = f"{(w + h) / 65}px pgrFont",
                textAlign = "left",
                textBaseline = "middle",
                fillStyle = "white",
                wait_execute = True
            )
            
            drawText(
                *pos1k(161, 263),
                "谱面设计: " + chosing_chart["charter"],
                font = f"{(w + h) / 65}px pgrFont",
                textAlign = "left",
                textBaseline = "middle",
                fillStyle = "white",
                wait_execute = True
            )
            
            drawText(
                *pos1k(161, 820),
                chosing_chart["name"],
                font = f"{(w + h) / 60}px pgrFont",
                textAlign = "left",
                textBaseline = "middle",
                fillStyle = "white",
                wait_execute = True
            )
            
            drawText(
                *pos1k(161, 880),
                chosing_chart["composer"],
                font = f"{(w + h) / 80}px pgrFont",
                textAlign = "left",
                textBaseline = "middle",
                fillStyle = "white",
                wait_execute = True
            )
            
            
            uilts.shadowDrawer.root = root
            for chart in charts:
                trs = chooser.tr_map[chart["id"]]
                size, center_pos = (trs[0].value, trs[1].value), (trs[2].value, trs[3].value)
                
                with uilts.shadowDrawer("rgba(16, 16, 16, 0.8)", (w + h) / 150):
                    fillRectEx(
                    center_pos[0] - size[0] / 2,
                    center_pos[1] - size[1] / 2,
                    *size,
                    "black",
                    wait_execute=True
                )
                    
                drawCoverFullScreenImage(
                    f"illu_{hashChartId(chart["id"])}",
                    *size,
                    center_pos[0] - size[0] / 2,
                    center_pos[1] - size[1] / 2,
                    wait_execute=True
                )
        
        globalUIManager.render("mainRender")
        
        if createChartData is not None:
            fillRectEx(0, 0, w, h, "rgba(0, 0, 0, 0.2)", wait_execute=True)
            fillRectEx(*pos1k(261, 69 + 78), *pos1k(1920 - 261 * 2, 841), "rgba(64, 64, 64, 0.8)", wait_execute=True)
            fillRectEx(*pos1k(261, 69), *pos1k(1920 - 261 * 2, 80), "gray", wait_execute=True)
            drawText(
                *uilts.getCenterPointByRect(uilts.xywh_rect2_xxyy((*pos1k(261, 69), *pos1k(1920 - 261 * 2, 80)))),
                "添加谱面",
                font = f"{(w + h) / 65}px pgrFont",
                textAlign = "center",
                textBaseline = "middle",
                fillStyle = "white",
                wait_execute = True
            )
            
            globalUIManager.render("mainRender-createChart")
        
        globalUIManager.render("global")
        
        root.run_js_wait_code()
        
        if needUpdateIllus:
            updateIllus()
            needUpdateIllus = False
        
        if nextUI is not None:
            globalUIManager.remove_uiitems("mainRender")
            dxsmixer_unix.mixer.music.fadeout(250)
            
            if illuPacker is not None:
                illuPacker.unload(illuPacker.getnames())
                
            Thread(target=nextUI, daemon=True).start()
            return

def init():
    global webdpr
    global w, h
    global Resource
    global globalUIManager, globalMsgShower
    
    if webcv.disengage_webview:
        socket_webviewbridge.hook(root)

    w, h, webdpr, _, _ = root.init_window_size_and_position(0.6)
    
    webdpr = root.run_js_code("window.devicePixelRatio;")
    
    if webdpr != 1.0:
        root.run_js_code(f"lowquality_scale = {1.0 / webdpr};")

    rw, rh = w, h
    root.run_js_code(f"resizeCanvas({rw}, {rh});")
    
    globalUIManager = UIManager()
    globalUIManager.bind_events()
    
    globalMsgShower = MessageShower()
    globalUIManager.extend_uiitems([globalMsgShower], "global")
    
    Resource = loadResource()

    # updateCoreConfig()

    Thread(target=mainRender, daemon=True).start()
    root.wait_for_close()
    atexit_run()

def atexit_run():
    tempdir.clearTempDir()
    needrelease.run()
    exitfunc(0)

Thread(target=root.init, args=(init, ), daemon=True).start()
root.start()
atexit_run()
