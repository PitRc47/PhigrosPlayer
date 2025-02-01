from __future__ import annotations

import time
import typing
import math
import logging
import threading
from dataclasses import dataclass
from queue import Queue

from PIL import Image

import webcv
import const
import tool_funcs
import rpe_easing
import chartobj_phi
import chartobj_rpe
import phi_tips
import dxsound
import phira_resource_pack
from dxsmixer import mixer, musicCls
from graplib_webview import *

drawUI_Default_Kwargs = {
    f"{k}_{k2}": v
    for k in ("combonumber", "combo", "score", "name", "level", "pause", "bar") for k2, v in (("dx", 0.0), ("dy", 0.0), ("scaleX", 1.0), ("scaleY", 1.0), ("color", "rgba(255, 255, 255, 1.0)"))
}
mainFramerateCalculator = tool_funcs.FramerateCalculator()
clickEffectEasingType = 16

@dataclass
class PhiCoreConfig:
    SETTER: typing.Callable[[str, typing.Any], typing.Any]
    
    root: webcv.WebCanvas
    w: int
    h: int
    chart_information: dict
    chart_obj: chartobj_phi.Phigros_Chart | chartobj_rpe.Rpe_Chart
    CHART_TYPE: int
    Resource: dict
    ClickEffectFrameCount: int
    globalNoteWidth: float
    note_max_size_half: float
    audio_length: float
    raw_audio_length: float
    show_start_time: float
    chart_image: Image.Image
    clickeffect_randomblock: bool
    clickeffect_randomblock_roundn: int
    LoadSuccess: musicCls
    chart_res: dict[str, tuple[Image.Image, tuple[int, int]]]
    cksmanager: ClickSoundManager
    enable_clicksound: bool
    rtacc: bool
    noautoplay: bool
    showfps: bool
    lfdaot: bool
    speed: float
    render_range_more: bool
    render_range_more_scale: float
    debug: bool
    combotips: bool
    noplaychart: bool
    clicksound_volume: float
    musicsound_volume: float
    enable_controls: bool

@dataclass
class PhiCoreConfigEx:
    chart_name_text: str
    chart_name_font_text_size: float
    chart_artist_text: str
    chart_artist_text_font_size: float
    chart_level_number: str
    chart_level_number_font_size: float
    chart_level_text: str
    chart_level_text_font_size: float
    tip: str
    tip_font_size: float
    chart_charter_text: str
    chart_illustrator_text: str
    chart_charter_text_font_size: float
    chart_illustrator_text_font_size: float
    
def CoreConfigure(config: PhiCoreConfig):
    global SETTER
    global root, w, h, chart_information
    global chart_obj, CHART_TYPE
    global Resource
    global ClickEffectFrameCount
    global globalNoteWidth
    global note_max_size_half, audio_length
    global raw_audio_length, show_start_time
    global chart_image
    global clickeffect_randomblock
    global clickeffect_randomblock_roundn, LoadSuccess
    global chart_res, cksmanager
    global enable_clicksound, rtacc, noautoplay
    global showfps, lfdaot
    global speed, render_range_more
    global render_range_more_scale
    global debug, combotips, noplaychart
    global enable_controls
    
    SETTER = config.SETTER
    root = config.root
    w, h = config.w, config.h
    chart_information = config.chart_information
    chart_obj = config.chart_obj
    CHART_TYPE = config.CHART_TYPE
    Resource = config.Resource
    ClickEffectFrameCount = config.ClickEffectFrameCount
    globalNoteWidth = config.globalNoteWidth
    note_max_size_half = config.note_max_size_half
    audio_length = config.audio_length
    raw_audio_length = config.raw_audio_length
    show_start_time = config.show_start_time
    chart_image = config.chart_image
    clickeffect_randomblock = config.clickeffect_randomblock
    clickeffect_randomblock_roundn = config.clickeffect_randomblock_roundn
    LoadSuccess = config.LoadSuccess
    chart_res = config.chart_res
    cksmanager = config.cksmanager
    enable_clicksound = config.enable_clicksound
    rtacc = config.rtacc
    noautoplay = config.noautoplay
    showfps = config.showfps
    lfdaot = config.lfdaot
    speed = config.speed
    render_range_more = config.render_range_more
    render_range_more_scale = config.render_range_more_scale
    debug = config.debug
    combotips = config.combotips
    noplaychart = config.noplaychart
    enable_controls = config.enable_controls
    
    if Resource["Note_Click_Audio"] is not None: # use in tools
        mixer.music.set_volume(config.musicsound_volume)
        for i in Resource["Note_Click_Audio"].values():
            i.set_volume(config.clicksound_volume)
    
    logging.info("CoreConfigure Done")

def CoreConfigureEx(config: PhiCoreConfigEx):
    global chart_name_text, chart_name_font_text_size
    global chart_artist_text, chart_artist_text_font_size
    global chart_level_number, chart_level_number_font_size
    global chart_level_text, chart_level_text_font_size
    global tip, tip_font_size
    global chart_charter_text
    global chart_illustrator_text
    global chart_charter_text_font_size, chart_illustrator_text_font_size
    
    chart_name_text = config.chart_name_text
    chart_name_font_text_size = config.chart_name_font_text_size
    chart_artist_text = config.chart_artist_text
    chart_artist_text_font_size = config.chart_artist_text_font_size
    chart_level_number = config.chart_level_number
    chart_level_number_font_size = config.chart_level_number_font_size
    chart_level_text = config.chart_level_text
    chart_level_text_font_size = config.chart_level_text_font_size
    tip = config.tip
    tip_font_size = config.tip_font_size
    chart_charter_text = config.chart_charter_text
    chart_illustrator_text = config.chart_illustrator_text
    chart_charter_text_font_size = config.chart_charter_text_font_size
    chart_illustrator_text_font_size = config.chart_illustrator_text_font_size
    
    logging.info("CoreConfigureEx Done")

class ClickSoundManager:
    def __init__(self, res: dict[int, dxsound.directSound]):
        self.res = res
        self.queue: Queue[int|None] = Queue()
        
        for _ in range(const.CSOUND_MANAGER_THREADNUM):
            threading.Thread(target=self.runner, daemon=True).start()
    
    def play(self, nt: int):
        self.queue.put(nt)
    
    def stop(self):
        self.queue.put(None)
    
    def runner(self):
        while True:
            nt = self.queue.get()
            if nt is None:
                self.queue.put(None)
                break
            self.res[nt].play()

def processClickEffectBase(
    x: float, y: float,
    p: float, rblocks: tuple[tuple[float, float]]|None,
    perfect: bool, noteWidth: float,
    root: webcv.WebCanvas,
    framecount: int,
    enable_rblocks: bool = True,
    rblocks_roundn: float = 0.0,
    caller: typing.Callable[[typing.Callable, typing.Any], typing.Any] = lambda f, *args, **kwargs: f(*args, **kwargs)
):
    if rblocks is None: rblocks = tool_funcs.newRandomBlocks()
    
    color = (
        (phira_resource_pack.globalPack.perfectRGB if not phira_resource_pack.globalPack.isdefault_perfect else (255, 236, 160))
        if perfect else
        phira_resource_pack.globalPack.goodRGB
    )
    
    alpha = (
        phira_resource_pack.globalPack.perfectAlpha
        if perfect else
        phira_resource_pack.globalPack.goodAlpha
    ) / 255
    
    imn = f"""Note_Click_Effect_{"Perfect" if perfect else "Good"}"""
    effectSize = noteWidth * 1.375
    blockSize = noteWidth / 5
    
    if enable_rblocks and not phira_resource_pack.globalPack.hideParticles:
        randomblock_r = effectSize * rpe_easing.ease_funcs[clickEffectEasingType + 1](p) / 1.2
        nowBlockSize = blockSize * (0.426 * math.sin(p * math.pi / 1.185) + 0.5) # start: 0.5, end: 0.7, max: ~0.925
        
        for deg, randdr in rblocks:
            pointr = randomblock_r + randdr * blockSize
            
            if pointr < 0.0: continue
            
            point = tool_funcs.rotate_point(x, y, deg, pointr)
            caller(
                root.run_js_code,
                f"""ctx.addRoundRectData(\
                    {point[0] - nowBlockSize / 2},\
                    {point[1] - nowBlockSize / 2},\
                    {nowBlockSize},\
                    {nowBlockSize},\
                    {nowBlockSize * rblocks_roundn}\
                );""",
                add_code_array = True
            )
    
        caller(root.run_js_code, f"ctx.drawRoundDatas('rgba{color + (1.0 - p, )}');", add_code_array = True)
    
    effectImageSize = effectSize * phira_resource_pack.globalPack.effectScale
    caller(
        drawAlphaImage,
        f"{imn}_{int(p * (framecount - 1)) + 1}",
        x - effectImageSize / 2, y - effectImageSize / 2,
        effectImageSize, effectImageSize, alpha,
        wait_execute = True
    )

def processClickEffect(
    x: float, y: float,
    p: float, rblocks: tuple[tuple[float, float]],
    perfect: bool,
    caller: typing.Callable[[typing.Callable, typing.Any], typing.Any] = lambda f, *args, **kwargs: f(*args, **kwargs)
):
    return processClickEffectBase(
        x = x, y = y, p = p,
        rblocks = rblocks,
        perfect = perfect,
        noteWidth = globalNoteWidth,
        root = root,
        framecount = ClickEffectFrameCount,
        caller = caller,
        enable_rblocks = clickeffect_randomblock,
        rblocks_roundn = clickeffect_randomblock_roundn
    )

def processBadEffect(
    x: float, y: float, rotate: float, st: float, now_t: float, bdfi_t: float,
    caller: typing.Callable[[typing.Callable, typing.Any], typing.Any] = lambda f, *args, **kwargs: f(*args, **kwargs)
):
    p = (now_t - st) / bdfi_t
    this_note_img = Resource["Notes"]["Bad"]
    caller(
        drawRotateImage,
        "Note_Bad",
        x * w, y * h,
        globalNoteWidth,
        globalNoteWidth / this_note_img.width * this_note_img.height,
        rotate,
        1 - p ** 3,
        wait_execute = True
    )

def getNoteDrawPosition(
    x: float, y: float,
    width: float,
    height_b: float,
    img_h: Image.Image,
    img_e: Image.Image,
    rotate: float,
    hadhead: bool
):
    height_h = width / img_h.width * img_h.height
    height_e = width / img_e.width * img_e.height
    
    headpos = (x, y)
    bodypos = tool_funcs.rotate_point(*headpos, rotate, height_h / 2) if hadhead else headpos
    endpos = tool_funcs.rotate_point(*bodypos, rotate, height_b + height_e / 2)
    
    _headheadpos = tool_funcs.rotate_point(*headpos, rotate, -height_h / 2)
    _endendpos = tool_funcs.rotate_point(*endpos, rotate, height_e / 2)
    
    holdrect = (
        tool_funcs.rotate_point(*_headheadpos, rotate - 90, width / 2),
        tool_funcs.rotate_point(*_headheadpos, rotate + 90, width / 2),
        tool_funcs.rotate_point(*_endendpos, rotate + 90, width / 2),
        tool_funcs.rotate_point(*_endendpos, rotate - 90, width / 2)
    )
    
    return (
        headpos,
        bodypos,
        endpos,
        holdrect
    )

def stringifyScore(score:float) -> str:
    score_integer = int(score + 0.5)
    return f"{score_integer:>7}".replace(" ","0")

def drawBg():
    drawImage("background", 0, 0, w, h, wait_execute=True)

# color 一定要传 rgba 的
def draw_ui(
    process:float = 0.0,
    score:str = "0000000",
    combo_state:bool = False,
    combo:int = 0,
    acc:str = "100.00%",
    clear:bool = True,
    background:bool = True,
    animationing:bool = False,
    dy:float = 0.0,
    
    combonumberUI_dx: float = 0.0,
    combonumberUI_dy: float = 0.0,
    combonumberUI_scaleX: float = 1.0,
    combonumberUI_scaleY: float = 1.0,
    combonumberUI_color: str = "rgba(255, 255, 255, 1.0)",
    combonumberUI_rotate: float = 0.0,
    
    comboUI_dx: float = 0.0,
    comboUI_dy: float = 0.0,
    comboUI_scaleX: float = 1.0,
    comboUI_scaleY: float = 1.0,
    comboUI_color: str = "rgba(255, 255, 255, 1.0)",
    comboUI_rotate: float = 0.0,
    
    scoreUI_dx: float = 0.0,
    scoreUI_dy: float = 0.0,
    scoreUI_scaleX: float = 1.0,
    scoreUI_scaleY: float = 1.0,
    scoreUI_color: str = "rgba(255, 255, 255, 1.0)",
    scoreUI_rotate: float = 0.0,
    
    nameUI_dx: float = 0.0,
    nameUI_dy: float = 0.0,
    nameUI_scaleX: float = 1.0,
    nameUI_scaleY: float = 1.0,
    nameUI_color: str = "rgba(255, 255, 255, 1.0)",
    nameUI_rotate: float = 0.0,
    
    levelUI_dx: float = 0.0,
    levelUI_dy: float = 0.0,
    levelUI_scaleX: float = 1.0,
    levelUI_scaleY: float = 1.0,
    levelUI_color: str = "rgba(255, 255, 255, 1.0)",
    levelUI_rotate: float = 0.0,
    
    pauseUI_dx: float = 0.0, # in fact, timeUI...
    pauseUI_dy: float = 0.0,
    pauseUI_scaleX: float = 1.0,
    pauseUI_scaleY: float = 1.0,
    pauseUI_color: str = "rgba(255, 255, 255, 1.0)",
    pauseUI_rotate: float = 0.0,
    
    barUI_dx: float = 0.0,
    barUI_dy: float = 0.0,
    barUI_scaleX: float = 1.0,
    barUI_scaleY: float = 1.0,
    barUI_color: str = "rgba(255, 255, 255, 1.0)",
    barUI_rotate: float = 0.0
):
    if clear: clearCanvas(wait_execute = True)
    if background: drawBg()
    
    pauseImgWidth = w * (32 / 1920)
    pauseImgHeight = pauseImgWidth / 35 * 41
    
    pauseImgWidth *= pauseUI_scaleX
    pauseImgHeight *= pauseUI_scaleY
    
    pauseImgRGBA = list(map(float, pauseUI_color.replace(" ", "").replace("rgba", "").replace("(", "").replace(")", "").split(",")))
    fps = mainFramerateCalculator.framerate
    reqaf_fps = root.get_framerate()
    
    uidata = [
        {
            "type": "call",
            "name": "translate", "args": [0, - h / 7  + dy]
        } if animationing else None,
        {
            "type": "pbar",
            "w": w, "pw": h / 95,
            "process": process,
            "dx": barUI_dx, "dy": barUI_dy,
            "sx": barUI_scaleX, "sy": barUI_scaleY,
            "color": barUI_color, "rotate": barUI_rotate
        },
        {
            "type": "text",
            "text": f"{score}", "fontsize": (w + h) / 75 / 0.75,
            "textBaseline": "top", "textAlign": "right",
            "x": w * (1 - (40 / 1920)), "y": h * (31 / 1080),
            "dx": scoreUI_dx, "dy": scoreUI_dy,
            "sx": scoreUI_scaleX, "sy": scoreUI_scaleY,
            "color": scoreUI_color, "rotate": scoreUI_rotate
        },
        {
            "type": "text",
            "text": f"{acc}", "fontsize": (w + h) / 145 / 0.75,
            "textBaseline": "top", "textAlign": "right",
            "x": w * (1 - (40 / 1920)), "y": h * (85 / 1080),
            "dx": 0.0, "dy": 0.0,
            "sx": scoreUI_scaleX, "sy": scoreUI_scaleY,
            "color": scoreUI_color, "rotate": scoreUI_rotate
        } if rtacc else None,
        {
            "type": "text",
            "text": f"{combo}", "fontsize": (w + h) / 53 / 0.75,
            "textBaseline": "middle", "textAlign": "center",
            "x": w / 2, "y": h * (52 / 1080),
            "dx": combonumberUI_dx, "dy": combonumberUI_dy,
            "sx": combonumberUI_scaleX, "sy": combonumberUI_scaleY,
            "color": combonumberUI_color, "rotate": combonumberUI_rotate
        } if combo_state else None,
        {
            "type": "text",
            "text": f"{combotips}", "fontsize": (w + h) / 160 / 0.75,
            "textBaseline": "top", "textAlign": "center",
            "x": w / 2, "y": h * 0.085,
            "dx": comboUI_dx, "dy": comboUI_dy,
            "sx": comboUI_scaleX, "sy": comboUI_scaleY,
            "color": comboUI_color, "rotate": comboUI_rotate
        } if combo_state else None,
        {
            "type": "image",
            "image": root.get_img_jsvarname("PauseImg"),
            "x": w * (36 / 1920), "y": h * (41 / 1080),
            "dx": pauseUI_dx, "dy": pauseUI_dy,
            "width": pauseImgWidth, "height": pauseImgHeight,
            "rotate": pauseUI_rotate, "color": pauseImgRGBA
        },
        {
            "type": "call",
            "name": "translate", "args": [0, -2 * (- h / 7 + dy)]
        } if animationing else None,
        {
            "type": "text",
            "text": chart_information["Name"], "fontsize": (w + h) / 115 / 0.75,
            "textBaseline": "bottom", "textAlign": "left",
            "x": w * 0.0225, "y": h * 0.965,
            "dx": nameUI_dx, "dy": nameUI_dy,
            "sx": nameUI_scaleX, "sy": nameUI_scaleY,
            "color": nameUI_color, "rotate": nameUI_rotate
        },
        {
            "type": "text",
            "text": chart_information["Level"], "fontsize": (w + h) / 115 / 0.75,
            "textBaseline": "bottom", "textAlign": "right",
            "x": w * 0.9775, "y": h * 0.965,
            "dx": levelUI_dx, "dy": levelUI_dy,
            "sx": levelUI_scaleX, "sy": levelUI_scaleY,
            "color": levelUI_color, "rotate": levelUI_rotate
        },
        {
            "type": "text",
            "text": f"fps {fps:.0f} - reqaf fps {reqaf_fps:.0f}", "fontsize": (w + h) / 275 / 0.75,
            "textBaseline": "bottom", "textAlign": "center",
            "x": w * 0.5, "y": h * 0.975,
            "dx": 0.0, "dy": 0.0,
            "sx": 1.0, "sy": 1.0,
            "color": "rgba(255, 255, 255, 0.5)", "rotate": 0.0
        } if showfps else None,
        {
            "type": "text",
            "text": "PhigrosPlayer - by qaqFei - github.com/qaqFei/PhigrosPlayer - MIT License",
            "fontsize": (w + h) / 275 / 0.75,
            "textBaseline": "bottom", "textAlign": "center",
            "x": w * 0.5, "y": h * 0.99,
            "dx": 0.0, "dy": 0.0,
            "sx": 1.0, "sy": 1.0,
            "color": "rgba(255, 255, 255, 0.5)", "rotate": 0.0
        },
        {
            "type": "call",
            "name": "translate", "args": [0, - h / 7 + dy]
        } if animationing else None
    ]
    
    root.run_js_code(f"ctx.drawUIItems({uidata});", add_code_array = True)
    mainFramerateCalculator.frame()
             
def delDrawuiDefaultVals(kwargs: dict) -> dict:
    return {k: v for k, v in kwargs.items() if v != drawUI_Default_Kwargs.get(k, None)}   

def drawDebugText(text: str, x: float, y: float, rotate: float, color: str, Task: chartobj_phi.FrameRenderTask):
    Task(
        root.run_js_code,
        f"""ctx.drawRotateText(\
            {root.string2sctring_hqm(text)},\
            {",".join(map(str, tool_funcs.rotate_point(x, y, rotate, (w + h) / 75)))},\
            {90 + rotate}, {(w + h) / 85 / 0.75}, '{color}', 1.0, 1.0\
        );""",
        add_code_array = True,
        order = const.CHART_RENDER_ORDERS.DEBUG
    )

def rrmStart(Task: chartobj_phi.FrameRenderTask):
    if not render_range_more: return
    lw, lh = w / render_range_more_scale, h / render_range_more_scale
    lr, lt = w / 2 - lw / 2, h / 2 - lh / 2
    rms = 1 / render_range_more_scale
    
    Task(
        root.run_js_code,
        f"ctx.save(); ctx.translate({lr}, {lt}); ctx.scale({rms}, {rms});",
        add_code_array = True
    )

def rrmEnd(Task: chartobj_phi.FrameRenderTask):
    if not render_range_more: return
    Task(
        root.run_js_code,
        "ctx.restore();",
        add_code_array = True
    )
    
def processExTask(ExTask: list[tuple[str, typing.Any]]):
    break_flag = False
    
    for ext in ExTask:
        match ext[0]:
            case "break":
                break_flag = True
            case "psound":
                cksmanager.play(ext[1])
        
    return break_flag

def GetFrameRenderTask_Phi(now_t: float, clear: bool = True, rjc: bool = True, pplm: tool_funcs.PhigrosPlayLogicManager|None = None):
    Task = chartobj_phi.FrameRenderTask([], [])
    if clear: Task(clearCanvas, wait_execute = True)
    rrmStart(Task)
    Task(drawBg)
    if noplaychart: Task.ExTask.append(("break", ))
        
    now_t *= speed
    noautoplay = pplm is not None # reset a global variable
    if noautoplay:
        pplm.pc_update(now_t)
    
    for lineIndex, line in enumerate(chart_obj.judgeLineList):
        lineBTime = now_t / line.T
        
        lineFloorPosition = chartobj_phi.getFloorPosition(line, lineBTime) * h * const.PGR_UH
        linePos = line.getMove(lineBTime, w, h)
        lineRotate = line.getRotate(lineBTime)
        lineAlpha = line.getAlpha(lineBTime)
        
        lineDrawPos = (
            *tool_funcs.rotate_point(*linePos, lineRotate, h * 5.76 / 2),
            *tool_funcs.rotate_point(*linePos, lineRotate + 180, h * 5.76 / 2)
        )
        lineColor = (*(phira_resource_pack.globalPack.perfectRGB if not noautoplay else pplm.ppps.getLineColor()), lineAlpha)
        lineWebColor = f"rgba{lineColor}"
        
        if (lineColor[-1] > 0.0 and tool_funcs.lineInScreen(w, h, lineDrawPos)) or debug:
            Task(
                root.run_js_code,
                f"""ctx.drawLineEx(\
                    {",".join(map(str, lineDrawPos))},\
                    {h * const.LINEWIDTH.PHI},\
                    '{lineWebColor}'\
                );""",
                add_code_array = True,
                order = const.CHART_RENDER_ORDERS.LINE
            )
            
            if debug:
                drawDebugText(f"{lineIndex}", *linePos, lineRotate - 90, "rgba(255, 255, 170, 0.5)", Task)
                
                Task(
                    root.run_js_code,
                    f"ctx.fillRectEx(\
                        {linePos[0] - (w + h) / 250},\
                        {linePos[1] - (w + h) / 250},\
                        {(w + h) / 250 * 2},\
                        {(w + h) / 250 * 2},\
                        'rgb(238, 130, 238)'\
                    );",
                    add_code_array = True,
                    order = const.CHART_RENDER_ORDERS.DEBUG
                )
        
        for notesChildren in line.renderNotes.copy():
            for note in notesChildren.copy():
                noteClicked = note.sec < now_t
                
                if noteClicked and not note.clicked:
                    note.clicked = True
                    if enable_clicksound and not noautoplay:
                        Task.ExTask.append(("psound", note.type))
                
                if not note.ishold and note.clicked:
                    notesChildren.remove(note)
                    continue
                elif note.ishold and now_t > note.hold_endtime:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and note.state == const.NOTE_STATE.BAD:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and not note.ishold and note.player_clicked:
                    notesChildren.remove(note)
                    continue
                elif not note.clicked and (note.floorPosition * h * const.PGR_UH - lineFloorPosition) < const.FLOAT_LESSZERO_MAGIC and note.type != const.NOTE_TYPE.HOLD:
                    continue
                elif note.ishold and note.speed == 0.0:
                    notesChildren.remove(note)
                    continue
                
                noteFloorPosition = note.floorPosition * h * const.PGR_UH - (
                    lineFloorPosition
                    if not (note.ishold and note.clicked) else (
                        chartobj_phi.getFloorPosition(
                            line, note.time
                        ) * h * const.PGR_UH
                        + tool_funcs.linear_interpolation(
                            note.hold_endtime - now_t,
                            0,
                            note.hold_length_sec,
                            note.hold_length_pgry * h * const.PGR_UH,
                            0
                        )
                    )
                )
                
                if not note.ishold:
                    noteFloorPosition *= note.speed
                
                if noteFloorPosition > h * 2:
                    break
                
                noteAtLinePos = tool_funcs.rotate_point(*linePos, lineRotate, note.positionX * w * const.PGR_UW)
                lineToNoteRotate = (-90 if note.above else 90) + lineRotate
                x, y = tool_funcs.rotate_point(*noteAtLinePos, lineToNoteRotate, noteFloorPosition)
                
                note.nowpos = (x / w, y / h)
                note.nowrotate = lineToNoteRotate + 90
                noteImg = Resource["Notes"][note.img_keyname]
                fix_scale = const.NOTE_DUB_FIXSCALE if note.morebets else 1.0
                noteWidth = globalNoteWidth * fix_scale
                noteHeight = noteWidth / noteImg.width * noteImg.height
                noteHadHead = not (note.ishold and note.clicked) or phira_resource_pack.globalPack.holdKeepHead
                
                if note.ishold:
                    holdLength = note.hold_length_pgry * h * const.PGR_UH
                    holdEndFloorPosition = noteFloorPosition + holdLength
                    noteEndImg = Resource["Notes"][note.img_end_keyname]
                    bodyLength = holdEndFloorPosition if note.clicked else holdLength
                    
                    headpos, bodypos, endpos, holdrect = getNoteDrawPosition(
                        *(noteAtLinePos if note.clicked else (x, y)),
                        noteWidth, bodyLength,
                        noteImg, noteEndImg,
                        lineToNoteRotate,
                        noteHadHead
                    )
                    
                if noteFloorPosition > note_max_size_half:
                    plp_lineLength = h * 5.76
                    
                    nlOutOfScreen_nohold = tool_funcs.noteLineOutOfScreen(
                        x, y, noteAtLinePos,
                        noteFloorPosition,
                        lineRotate, plp_lineLength,
                        lineToNoteRotate,
                        w, h, note_max_size_half
                    )
                    
                    nlOutOfScreen_hold = True if not note.ishold else tool_funcs.noteLineOutOfScreen(
                        x, y, noteAtLinePos,
                        holdEndFloorPosition, lineRotate, plp_lineLength,
                        lineToNoteRotate, w, h, note_max_size_half
                    )
                    
                    if nlOutOfScreen_nohold and nlOutOfScreen_hold:
                        break
                    
                noteCanRender = (
                    tool_funcs.noteCanRender(w, h, note_max_size_half, x, y)
                    if not note.ishold
                    else tool_funcs.noteCanRender(w, h, -1, x, y, holdrect)
                )
                
                if noteCanRender:
                    noteRotate = lineToNoteRotate + 90
                        
                    if noteHadHead:
                        Task(setOrder, note.draworder)
                        Task(
                            drawRotateImage,
                            note.imgname,
                            x if not note.ishold else headpos[0],
                            y if not note.ishold else headpos[1],
                            noteWidth,
                            noteHeight,
                            noteRotate,
                            1.0,
                            wait_execute = True
                        )
                        Task(setOrder, None)
                        
                    if note.ishold:
                        noteEndHeight = noteWidth / noteEndImg.width * noteEndImg.height
                        missAlpha = 0.5 if noautoplay and note.player_missed else 1.0
                        
                        Task(setOrder, note.draworder)
                        Task(
                            drawRotateImage,
                            note.imgname_end,
                            *endpos,
                            noteWidth, noteEndHeight,
                            noteRotate, missAlpha,
                            wait_execute = True
                        )
                        Task(setOrder, None)
                        
                        if bodyLength > 0.0:
                            Task(
                                root.run_js_code,
                                f"ctx.drawAnchorESRotateImage(\
                                    {root.get_img_jsvarname(note.imgname_body)},\
                                    {bodypos[0]}, {bodypos[1]},\
                                    {noteWidth},\
                                    {bodyLength},\
                                    {noteRotate},\
                                    {missAlpha}\
                                );",
                                add_code_array = True,
                                order = note.draworder
                            )
                
                    if debug:
                        drawDebugText(f"{lineIndex}+{note.master_index}", x, y, lineToNoteRotate, "rgba(0, 255, 255, 0.5)", Task)
                        
                        Task(
                            root.run_js_code,
                            f"ctx.fillRectEx(\
                                {x - (w + h) / 250},\
                                {y - (w + h) / 250},\
                                {(w + h) / 250 * 2},\
                                {(w + h) / 250 * 2},\
                                'rgb(0, 255, 0)'\
                            );",
                            add_code_array = True,
                            order = const.CHART_RENDER_ORDERS.DEBUG
                        )

            if not notesChildren:
                line.renderNotes.remove(notesChildren)
                
    Task(root.run_jscode_orders)
    
    effect_time = phira_resource_pack.globalPack.effectDuration
    miss_effect_time = 0.2
    bad_effect_time = 0.5
    
    effect_time *= speed
    miss_effect_time *= speed
    bad_effect_time *= speed
    
    def process_miss(note: chartobj_phi.Note):
        t = now_t / note.master.T
        p = (now_t - note.sec) / miss_effect_time
        linePos = line.getMove(t, w, h)
        lineRotate = line.getRotate(t)
        pos = tool_funcs.rotate_point(
            *linePos,
            lineRotate,
            note.positionX * w * const.PGR_UW
        )
        floorp = note.floorPosition - chartobj_phi.getFloorPosition(note.master, t)
        x, y = tool_funcs.rotate_point(
            *pos,
            (-90 if note.above else 90) + lineRotate,
            floorp * h * const.PGR_UH
        )
        img_keyname = f"""{note.type_string}{"_dub" if note.morebets else ""}"""
        noteImg = Resource["Notes"][img_keyname]
        imgname = f"Note_{img_keyname}"
        fix_scale = const.NOTE_DUB_FIXSCALE if note.morebets else 1.0
        noteWidth = globalNoteWidth * fix_scale
        noteHeight = noteWidth / noteImg.width * noteImg.height
        Task(
            drawRotateImage,
            imgname,
            x, y,
            noteWidth, noteHeight,
            lineRotate,
            1 - p ** 0.5,
            wait_execute = True
        )
        
    if noautoplay:
        for pplmckfi in pplm.clickeffects.copy():
            perfect, eft, erbs, position = pplmckfi
            if eft <= now_t <= eft + effect_time:
                processClickEffect(*position(w, h), (now_t - eft) / effect_time, erbs, perfect, Task)
            
            if eft + effect_time < now_t:
                pplm.clickeffects.remove(pplmckfi)
        
        for pplmbdfi in pplm.badeffects.copy():
            st, rotate, pos = pplmbdfi
            if st <= now_t <= st + bad_effect_time:
                processBadEffect(*pos, rotate, st, now_t, bad_effect_time, Task)
            
            if st + bad_effect_time < now_t:
                pplm.badeffects.remove(pplmbdfi)
        
    for line in chart_obj.judgeLineList:
        for note in line.effectNotes.copy():
            if not noautoplay and not note.clicked: break
            
            if not noautoplay:
                for eft, erbs, position in note.effect_times:
                    if eft <= now_t <= eft + effect_time:
                        processClickEffect(*position(w, h), (now_t - eft) / effect_time, erbs, True, Task)
                        
            else: # noautoplay
                if note.state == const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note.sec <= miss_effect_time and note.type != const.NOTE_TYPE.HOLD:
                        process_miss(note)
                    
            if note.effect_times[-1][0] + max(
                effect_time,
                miss_effect_time,
                bad_effect_time
            ) + 0.2 < now_t:
                line.effectNotes.remove(note)
    
    combo = chart_obj.getCombo(now_t) if not noautoplay else pplm.ppps.getCombo()
    now_t /= speed
    Task(
        draw_ui,
        process = now_t / audio_length,
        score = stringifyScore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else stringifyScore(pplm.ppps.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        acc = "100.00%" if not noautoplay else f"{(pplm.ppps.getAcc() * 100):.2f}%",
        clear = False,
        background = False
    )
    
    rrmEnd(Task)
    if rjc: Task(root.run_js_wait_code)
    
    if now_t >= raw_audio_length:
        Task.ExTask.append(("break", ))
    
    return Task

def GetFrameRenderTask_Rpe(now_t: float, clear: bool = True, rjc: bool = True, pplm: tool_funcs.PhigrosPlayLogicManager|None = None):
    Task = chartobj_phi.FrameRenderTask([], [])
    if clear: Task(clearCanvas, wait_execute = True)
    rrmStart(Task)
    Task(drawBg)
    if noplaychart: Task.ExTask.append(("break", ))
    
    attachUIData = {}
        
    now_t *= speed
    now_t -= chart_obj.META.offset / 1000
    
    noautoplay = pplm is not None # reset a global variable
    if noautoplay:
        pplm.pc_update(now_t)
    
    nowLineColor = phira_resource_pack.globalPack.perfectRGB if not noautoplay else pplm.ppps.getLineColor()
    normalBeatTime = chart_obj.sec2beat(now_t, 1.0)
    
    for line in chart_obj.sortedLines:
        beatTime = chart_obj.sec2beat(now_t, line.bpmfactor) if line.bpmfactor != 1.0 else normalBeatTime
        linePos, lineAlpha, lineRotate, lineColor, lineScaleX, lineScaleY, lineText = line.GetState(beatTime, nowLineColor)
        linePos = (linePos[0] * w, linePos[1] * h)
        lineDrawPos = (
            *tool_funcs.rotate_point(*linePos, lineRotate, w * 4000 / const.RPE_WIDTH * lineScaleX / 2),
            *tool_funcs.rotate_point(*linePos, lineRotate + 180, w * 4000 / const.RPE_WIDTH * lineScaleX / 2)
        )
        negativeAlpha = lineAlpha < 0.0
        lineWebColor = f"rgba{lineColor + (lineAlpha, )}"
        lineWidth = h * const.LINEWIDTH.RPE * lineScaleY
        
        if line.attachUI is not None: # has a "bar" key is not supported, but you cannot merge the 2 if !!!!!!!!
            if line.attachUI in ("combonumber", "combo", "score", "name", "level", "pause", "bar"):
                attachUIData.update({
                    f"{line.attachUI}UI_dx": linePos[0] - w / 2,
                    f"{line.attachUI}UI_dy": linePos[1] - h / 2,
                    f"{line.attachUI}UI_scaleX": lineScaleX,
                    f"{line.attachUI}UI_scaleY": lineScaleY,
                    f"{line.attachUI}UI_color": lineWebColor,
                    f"{line.attachUI}UI_rotate": lineRotate
                })
        elif lineAlpha > 0.0:
            if line.Texture != "line.png":
                texture_width, texture_height = tool_funcs.conimgsize(*chart_res[line.Texture][1], w, h)
                texture_width *= lineScaleX; texture_height *= lineScaleY
                if tool_funcs.TextureLine_CanRender(w, h, (texture_width ** 2 + texture_height ** 2) ** 0.5 / 2, *linePos):
                    texturename = root.get_img_jsvarname(f"lineTexture_{line.index}")
                    if line.isGif:
                        Task(
                            root.run_js_code,
                            f"{texturename}.currentTime = {now_t} % {texturename}.duration;",
                            add_code_array = True
                        )
                    Task(
                        root.run_js_code,
                        f"""{f"setColorMatrix{tuple(map(lambda x: x / 255, lineColor))}; ctx.filter = 'url(#textureLineColorFilter)'; " if lineColor != (255, 255, 255) else ""}\
                        ctx.drawRotateImage(\
                            {texturename},\
                            {linePos[0]},\
                            {linePos[1]},\
                            {texture_width},\
                            {texture_height},\
                            {lineRotate},\
                            {lineAlpha}\
                        ); {"ctx.filter = 'none';" if lineColor != (255, 255, 255) else ""}""",
                        add_code_array = True,
                        order = const.CHART_RENDER_ORDERS.LINE
                    )
            elif lineText is not None:
                Task(
                    root.run_js_code,
                    f"""ctx.drawRPEMultipleRotateText(\
                        '{root.string2cstring(lineText)}',\
                        {linePos[0]},\
                        {linePos[1]},\
                        {lineRotate},\
                        {(w + h) / 75 * 1.35},\
                        '{lineWebColor}',\
                        {lineScaleX},\
                        {lineScaleY}\
                    );""",
                    add_code_array = True,
                    order = const.CHART_RENDER_ORDERS.LINE
                )
            elif tool_funcs.lineInScreen(w, h, lineDrawPos):
                Task(
                    root.run_js_code,
                    f"""ctx.drawLineEx(\
                        {",".join(map(str, lineDrawPos))},\
                        {lineWidth},\
                        '{lineWebColor}'\
                    );""",
                    add_code_array = True,
                    order = const.CHART_RENDER_ORDERS.LINE
                )
            
            if debug and tool_funcs.pointInScreen(linePos, w, h):
                drawDebugText(f"{line.index}", *linePos, lineRotate - 90, "rgba(255, 255, 170, 0.5)", Task)
                
                Task(
                    root.run_js_code,
                    f"ctx.fillRectEx(\
                        {linePos[0] - (w + h) / 250},\
                        {linePos[1] - (w + h) / 250},\
                        {(w + h) / 250 * 2},\
                        {(w + h) / 250 * 2},\
                        'rgb(238, 130, 238)'\
                    );",
                    add_code_array = True,
                    order = const.CHART_RENDER_ORDERS.DEBUG
                )
        
        line.playingFloorPosition = line.GetFloorPositionByTime(now_t)
        
        for notesChildren in line.renderNotes.copy():
            for note in notesChildren.copy():
                note_clicked = note.startTime.value < beatTime
                
                if note_clicked and not note.clicked:
                    note.clicked = True
                    if enable_clicksound and not note.isFake and not noautoplay:
                        Task.ExTask.append(("psound", note.hitsound_reskey))
                
                if not note.ishold and note.clicked:
                    notesChildren.remove(note)
                    continue
                elif note.ishold and beatTime > note.endTime.value:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and note.state == const.NOTE_STATE.BAD:
                    notesChildren.remove(note)
                    continue
                elif noautoplay and not note.ishold and note.player_clicked:
                    notesChildren.remove(note)
                    continue
                
                noteFloorPosition = (note.floorPosition - line.playingFloorPosition) * h * note.speed + note.yOffset / const.RPE_HEIGHT * h
                if line.isCover and noteFloorPosition < const.FLOAT_LESSZERO_MAGIC and not note.clicked and not note.ishold:
                    continue
                
                noteAtLinePos = tool_funcs.rotate_point(*linePos, lineRotate, note.positionX2 * w)
                lineToNoteRotate = lineRotate + (-90 if note.above else 90)
                x, y = tool_funcs.rotate_point(*noteAtLinePos, lineToNoteRotate, noteFloorPosition)
                
                if enable_controls:
                    rpex = tool_funcs.aconrpepos(x, y)[0]
                    ax, px, sx, yx = line.controlEvents.gtvalue(rpex)
                    noteFloorPosition *= yx
                    x, y = tool_funcs.rotate_point(*noteAtLinePos, lineToNoteRotate, noteFloorPosition)
                    rpex, rpey = tool_funcs.aconrpepos(x, y)
                    noteAlpha = note.float_alpha * ax
                    rpex *= px
                    noteWidthX = note.width * sx
                    x, y = tool_funcs.conrpepos(rpex, rpey)
                else:
                    noteAlpha = note.float_alpha
                    noteWidthX = note.width
                
                note.nowpos = (x / w, y / h)
                note.nowrotate = lineToNoteRotate + 90
                    
                noteImg = Resource["Notes"][note.img_keyname]
                noteWidth = globalNoteWidth * (const.NOTE_DUB_FIXSCALE if note.morebets else 1.0)
                noteHadHead = not (note.ishold and note.clicked) or phira_resource_pack.globalPack.holdKeepHead
                    
                if note.ishold:
                    noteEndImg = Resource["Notes"][note.img_end_keyname]
                    holdLength = note.holdLength * h * note.speed
                    holdEndFloorPosition = noteFloorPosition + holdLength
                    bodyLength = holdEndFloorPosition if note.clicked else holdLength
                    
                    if line.isCover and holdEndFloorPosition < 0 and not note.clicked:
                        continue
                    
                    headpos, bodypos, endpos, holdrect = getNoteDrawPosition(
                        *(noteAtLinePos if note.clicked else (x, y)),
                        noteWidth, bodyLength,
                        noteImg, noteEndImg,
                        lineToNoteRotate,
                        noteHadHead
                    )
                    
                if noteFloorPosition > note_max_size_half:
                    plp_lineLength = w * 4000 / const.RPE_WIDTH
                    
                    nlOutOfScreen_nohold = tool_funcs.noteLineOutOfScreen(
                        x, y, noteAtLinePos,
                        noteFloorPosition,
                        lineRotate, plp_lineLength,
                        lineToNoteRotate,
                        w, h, note_max_size_half
                    )
                    
                    nlOutOfScreen_hold = True if not note.ishold else tool_funcs.noteLineOutOfScreen(
                        x, y, noteAtLinePos,
                        holdEndFloorPosition, lineRotate, plp_lineLength,
                        lineToNoteRotate, w, h, note_max_size_half
                    )
                    
                    if nlOutOfScreen_nohold and nlOutOfScreen_hold:
                        break # it is safe to break, because speed and yOffset value is same in a notesChildren.
                
                noteCanRender = (
                    tool_funcs.noteCanRender(w, h, note_max_size_half, x, y)
                    if not note.ishold
                    else tool_funcs.noteCanRender(w, h, -1, x, y, holdrect)
                ) and not negativeAlpha and now_t >= 0.0 and note.secst - now_t <= note.visibleTime
                
                if noteCanRender:
                    noteRotate = lineRotate + note.rotate_add
                    noteHeight = noteWidth / noteImg.width * noteImg.height
                    
                    if noteHadHead:
                        Task(setOrder, note.draworder)
                        Task(
                            drawRotateImage,
                            note.imgname,
                            x if not note.ishold else headpos[0],
                            y if not note.ishold else headpos[1],
                            noteWidth * noteWidthX,
                            noteHeight,
                            noteRotate,
                            noteAlpha,
                            wait_execute = True
                        )
                        Task(setOrder, None)
                        
                    if note.ishold:
                        noteEndHeight = noteWidth / noteEndImg.width * noteEndImg.height
                        missAlpha = 0.5 if noautoplay and note.player_missed else 1.0
                        
                        Task(setOrder, note.draworder)
                        Task(
                            drawRotateImage,
                            note.imgname_end,
                            *endpos,
                            noteWidth * noteWidthX,
                            noteEndHeight,
                            noteRotate,
                            noteAlpha * missAlpha,
                            wait_execute = True
                        )
                        Task(setOrder, None)
                        
                        if bodyLength > 0.0:
                            Task(
                                root.run_js_code,
                                f"ctx.drawAnchorESRotateImage(\
                                    {root.get_img_jsvarname(note.imgname_body)},\
                                    {bodypos[0]}, {bodypos[1]},\
                                    {noteWidth * noteWidthX},\
                                    {bodyLength},\
                                    {noteRotate},\
                                    {noteAlpha * missAlpha}\
                                );",
                                add_code_array = True,
                                order = note.draworder
                            )
                        
                    if debug:
                        drawDebugText(f"{line.index}+{note.master_index}", x, y, lineToNoteRotate, "rgba(0, 255, 255, 0.5)", Task)
                        
                        Task(
                            root.run_js_code,
                            f"ctx.fillRectEx(\
                                {x - (w + h) / 250},\
                                {y - (w + h) / 250},\
                                {(w + h) / 250 * 2},\
                                {(w + h) / 250 * 2},\
                                'rgb(0, 255, 0)'\
                            );",
                            add_code_array = True,
                            order = const.CHART_RENDER_ORDERS.DEBUG
                        )
            
            if not notesChildren:
                line.renderNotes.remove(notesChildren)
    
    Task(root.run_jscode_orders)
    
    effect_time = phira_resource_pack.globalPack.effectDuration
    miss_effect_time = 0.2
    bad_effect_time = 0.5
    
    effect_time *= speed
    miss_effect_time *= speed
    bad_effect_time *= speed
    
    if noautoplay:
        def process_miss(note: chartobj_rpe.Note):
            t = chart_obj.sec2beat(now_t, note.masterLine.bpmfactor)
            p = (now_t - note.secst) / miss_effect_time
            linePos = tool_funcs.conrpepos(*line.GetPos(t)); linePos = (linePos[0] * w, linePos[1] * h)
            lineRotate = sum([line.getEventValue(t, layer.rotateEvents, 0.0) for layer in line.eventLayers])
            pos = tool_funcs.rotate_point(
                *linePos,
                lineRotate,
                note.positionX2 * w
            )
            floorp = note.floorPosition - line.playingFloorPosition
            x, y = tool_funcs.rotate_point(
                *pos,
                (-90 if note.above else 90) + lineRotate,
                floorp * h
            )
            img_keyname = f"""{note.type_string}{"_dub" if note.morebets else ""}"""
            noteImg = Resource["Notes"][img_keyname]
            imgname = f"Note_{img_keyname}"
            fix_scale = const.NOTE_DUB_FIXSCALE if note.morebets else 1.0
            noteWidth = globalNoteWidth * fix_scale
            noteHeight = noteWidth / noteImg.width * noteImg.height
            Task(
                drawRotateImage,
                imgname,
                x, y,
                noteWidth * note.width,
                noteHeight,
                lineRotate,
                note.float_alpha * (1 - p ** 0.5),
                wait_execute = True
            )
    
    if noautoplay:
        for pplmckfi in pplm.clickeffects.copy():
            perfect, eft, erbs, position = pplmckfi
            if eft <= now_t <= eft + effect_time:
                processClickEffect(*position(w, h), (now_t - eft) / effect_time, erbs, perfect, Task)
            
            if eft + effect_time < now_t:
                pplm.clickeffects.remove(pplmckfi)
        
        for pplmbdfi in pplm.badeffects.copy():
            st, rotate, pos = pplmbdfi
            if st <= now_t <= st + bad_effect_time:
                processBadEffect(*pos, rotate, st, now_t, bad_effect_time, Task)
            
            if st + bad_effect_time < now_t:
                pplm.badeffects.remove(pplmbdfi)
                
    for line in chart_obj.judgeLineList:
        for note in line.effectNotes.copy():
            if not noautoplay and not note.clicked: break
            
            if not noautoplay:
                for eft, erbs, position in note.effect_times:
                    if eft <= now_t <= eft + effect_time:
                        processClickEffect(*position(w, h), (now_t - eft) / effect_time, erbs, True, Task)
                        
            else: # noautoplay
                if note.state == const.NOTE_STATE.MISS:
                    if 0.0 <= now_t - note.secst <= miss_effect_time and not note.ishold:
                        process_miss(note)
                
            if note.effect_times[-1][0] + max(
                effect_time,
                miss_effect_time,
                bad_effect_time
            ) + 0.2 < now_t:
                line.effectNotes.remove(note)
    
    if chart_obj.extra is not None:
        extra_values = chart_obj.extra.getValues(now_t, False)
        for name, values in extra_values:
            doShader(name, values, Task)
    
    combo = chart_obj.getCombo(now_t) if not noautoplay else pplm.ppps.getCombo()
    Task(
        draw_ui,
        process = now_t / speed / audio_length,
        score = stringifyScore((combo * (1000000 / chart_obj.note_num)) if chart_obj.note_num != 0 else 1000000) if not noautoplay else stringifyScore(pplm.ppps.getScore()),
        combo_state = combo >= 3,
        combo = combo,
        acc = "100.00%" if not noautoplay else f"{(pplm.ppps.getAcc() * 100):.2f}%",
        clear = False,
        background = False,
        **delDrawuiDefaultVals(attachUIData)
    )
    
    if chart_obj.extra is not None:
        extra_values = chart_obj.extra.getValues(now_t, True)
        for name, values in extra_values:
            doShader(name, values, Task)
        
    now_t /= speed
    now_t += chart_obj.META.offset / 1000
            
    rrmEnd(Task)
    if rjc: Task(root.run_js_wait_code)
    
    if now_t >= raw_audio_length:
        Task.ExTask.append(("break", ))
    
    return Task

def doShader(
    name: str,
    values: dict,
    caller: typing.Callable[[typing.Callable, typing.Any], typing.Any] = lambda f, *args, **kwargs: f(*args, **kwargs)
):
    caller(
        root.run_js_code,
        f"mainShaderLoader.renderToCanvas(ctx, {repr(name)}, {repr(values)})",
        add_code_array = True
    )

def getLevelNumber() -> str:
    lv = chart_information["Level"].lower()
    if "lv." in lv:
        return lv.split("lv.")[1]
    elif "lv" in lv:
        return lv.split("lv")[1]
    elif "level" in lv:
        return lv.split("level")[1]
    else:
        return "?"
    
def getLevelText() -> str:
    return chart_information["Level"].split(" ")[0]

def getFontSize(text: str, maxwidth: str, maxsize: float):
    js_result = root.run_js_code(f"ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(text)}).width;")
    w1px = float(js_result) / 50
    if w1px == 0: w1px = 1.0
    return min(maxsize, maxwidth / w1px)

def loadingAnimationFrame(p: float, sec: float, clear: bool = True, fcb: typing.Callable[[], typing.Any] = lambda: None) -> chartobj_phi.FrameRenderTask:
    Task = chartobj_phi.FrameRenderTask([], [])
    
    if clear: Task(clearCanvas, wait_execute = True)
    all_ease_value = tool_funcs.begin_animation_eases.im_ease(p)
    background_ease_value = tool_funcs.begin_animation_eases.background_ease(p) * 1.25
    info_data_ease_value = tool_funcs.begin_animation_eases.info_data_ease((p - 0.2) * 3.25)
    info_data_ease_value_2 = tool_funcs.begin_animation_eases.info_data_ease((p - 0.275) * 3.25)
    
    Task(drawBg)
    fcb()
    
    blackShadowRect = (
        0, 0,
        background_ease_value * w, h
    )
    blackShadowDPower = tool_funcs.getDPower(*tool_funcs.getSizeByRect(blackShadowRect), 75)
    blackShadowPolygon = (
        (0, 0),
        (background_ease_value * w, 0),
        (background_ease_value * w * (1 - blackShadowDPower), h),
        (0, h),
        (0, 0)
    )
    Task(
        drawPolygon,
        blackShadowPolygon,
        fillStyle = f"rgba(0, 0, 0, {0.75 * (1 - p)})",
        wait_execute = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate({all_ease_value * w}, 0.0);",
        add_code_array = True
    )
    
    infoframe_x = w * 0.0640625
    infoframe_y = h * (362 / 1080)
    infoframe_width = w * 0.3859375
    infoframe_height = h * (143 / 1080)
    Task(
        drawPolygon,
        tool_funcs.rect2drect(
            (
                infoframe_x, infoframe_y,
                infoframe_x + infoframe_width,
                infoframe_y + infoframe_height
            ),
            75
        ),
        fillStyle = "rgba(0, 0, 0, 0.75)",
        wait_execute = True
    )
    
    levelframe_x = w * 0.3421875
    levelframe_y = h * (355 / 1080)
    levelframe_width = w * 0.0984375
    levelframe_height = h * (157 / 1080)
    Task(
        drawPolygon,
        tool_funcs.rect2drect(
            (
                levelframe_x, levelframe_y,
                levelframe_x + levelframe_width,
                levelframe_y + levelframe_height
            ),
            75
        ),
        fillStyle = "white",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.1,
        h * (416 / 1080),
        text = chart_name_text,
        font = f"{(chart_name_font_text_size)}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = "white",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.0984375,
        h * (467 / 1080),
        text = chart_artist_text,
        font = f"{(chart_artist_text_font_size)}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = "white",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.390625,
        h * (424 / 1080),
        text = chart_level_number,
        font = f"{(chart_level_number_font_size)}px PhigrosFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "#2F2F2F",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.390625,
        h * (467 / 1080),
        text = chart_level_text,
        font = f"{(chart_level_text_font_size)}px PhigrosFont",
        textAlign = "center",
        textBaseline = "middle",
        fillStyle = "#2F2F2F",
        wait_execute = True
    )
    
    tipalpha = tool_funcs.begin_animation_eases.tip_alpha_ease(p)
    Task(
        drawText,
        w * 0.053125,
        h * (1004 / 1080),
        text = f"Tip: {tip}",
        font = f"{tip_font_size}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = f"rgba(255, 255, 255, {tipalpha})",
        wait_execute = True
    )
    
    loadingBlockX = w * 0.84375
    loadingBlockY = h * (971 / 1080)
    loadingBlockWidth = w * 0.1046875
    loadingBlockHeight = h * (50 / 1080)
    loadingBlockTime = 0.65
    loadingBlockState: typing.Literal[0, 1] = int(sec / loadingBlockTime) % 2
    loadingBlockP = (sec % loadingBlockTime) / loadingBlockTime
    loadingBlockP = min(loadingBlockP / 0.95, 1.0)
    loadingBlockEasingType = 10
    loadingBlockEasing = (
        rpe_easing.ease_funcs[loadingBlockEasingType - 1](loadingBlockP)
        if loadingBlockState == 0 else
        (1.0 - rpe_easing.ease_funcs[loadingBlockEasingType - 1](1.0 - loadingBlockP))
    )
    
    loadingBlockLeft = loadingBlockX if loadingBlockState == 0 else (loadingBlockX + loadingBlockEasing * loadingBlockWidth)
    loadingBlockRight = (loadingBlockX + loadingBlockWidth) if loadingBlockState == 1 else (loadingBlockX + loadingBlockEasing * loadingBlockWidth)
    Task(
        root.run_js_code,
        f"ctx.fillRectEx(\
            {loadingBlockLeft}, {loadingBlockY}, {loadingBlockRight - loadingBlockLeft}, {loadingBlockHeight},\
            'rgba(255, 255, 255, {tipalpha})'\
        );",
        add_code_array = True
    )
    
    def drawLoading(x0: float, x1: float, color: str):
        Task(
            root.run_js_code,
            f"ctx.drawClipXText(\
                'Loading...',\
                {loadingBlockX + loadingBlockWidth / 2},\
                {loadingBlockY + loadingBlockHeight / 2},\
                'center', 'middle', '{color}',\
                '{(w + h) / 100}px PhigrosFont',\
                {x0}, {x1}\
            );",
            add_code_array = True
        )
    
    drawLoading(loadingBlockX, loadingBlockX + loadingBlockWidth, f"rgba(255, 255, 255, {tipalpha})")
    drawLoading(loadingBlockLeft, loadingBlockRight, f"rgba(0, 0, 0, {tipalpha})")
    
    info_charter_dx = (1 - info_data_ease_value) * -1 * w * 0.075
    info_ill_dx = (1 - info_data_ease_value_2) * -1 * w * 0.075
    
    Task(
        drawText,
        w * 0.1265625 + info_charter_dx,
        h * (561 / 1080),
        text = "Chart",
        font = f"{w / 98}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.1265625 + info_charter_dx,
        h * (590 / 1080),
        text = chart_charter_text,
        font = f"{chart_charter_text_font_size}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value})",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.1125 + info_ill_dx,
        h * (645 / 1080),
        text = "Illustration",
        font = f"{w / 98}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
        wait_execute = True
    )
    
    Task(
        drawText,
        w * 0.1109375 + info_ill_dx,
        h * (677 / 1080),
        text = chart_illustrator_text,
        font = f"{chart_illustrator_text_font_size}px PhigrosFont",
        textAlign = "left",
        textBaseline = "middle",
        fillStyle = f"rgba(255, 255, 255, {info_data_ease_value_2})",
        wait_execute = True
    )
    
    baimg_w = w * 0.5078125
    baimg_h = h * (512 / 1080)
    dpower = tool_funcs.getDPower(baimg_w, baimg_h, 75)
    
    baimg_rawr = chart_image.width / chart_image.height
    baimg_r = baimg_w / baimg_h
    if baimg_rawr > baimg_r:
        baimg_draww = baimg_h * baimg_rawr
        baimg_drawh = baimg_h
    else:
        baimg_draww = baimg_w
        baimg_drawh = baimg_w / baimg_rawr
    
    Task(
        root.run_js_code,
        f"ctx.drawDiagonalRectangleClipImage(\
            {w * 0.690625 - baimg_w / 2}, {h * (476 / 1080) - baimg_h / 2},\
            {w * 0.690625 + baimg_w / 2}, {h * (476 / 1080) + baimg_h / 2},\
            {root.get_img_jsvarname('begin_animation_image')},\
            {baimg_w / 2 - baimg_draww / 2}, {baimg_h / 2 - baimg_drawh / 2},\
            {baimg_draww}, {baimg_drawh}, {dpower}, 1.0\
        );",
        add_code_array = True
    )
    
    Task(
        root.run_js_code,
        f"ctx.translate(-{all_ease_value * w},0.0);",
        add_code_array = True
    )
    
    Task(root.run_js_wait_code)
    return Task

def loadingAnimation(clear: bool = True, fcb: typing.Callable[[], typing.Any] = lambda: None):
    animation_time = 4.5
    
    chart_name_text = chart_information["Name"]
    chart_level_number = getLevelNumber()
    chart_level_text = getLevelText()
    chart_artist_text = chart_information["Artist"]
    chart_charter_text = chart_information["Charter"]
    chart_illustrator_text = chart_information["Illustrator"]
    tip = phi_tips.get_tip()
    
    infoframe_width = w * 0.321875
    
    tip_font_size = getFontSize(tip, w * 0.84375 * 0.9, w * 0.020833 / 1.25)
    chart_name_font_text_size = getFontSize(chart_name_text, infoframe_width * 0.6, w * 0.025)
    chart_level_number_font_size = getFontSize(chart_level_number, infoframe_width * 0.125, h * (66 / 1080))
    chart_level_text_font_size = getFontSize(chart_level_text, infoframe_width * 0.075, h * (24 / 1080))
    chart_artist_text_font_size = getFontSize(chart_artist_text, infoframe_width * 0.65, w * 0.0161875)
    chart_charter_text_font_size = getFontSize(chart_charter_text, infoframe_width * 0.85, (w + h) * 0.011)
    chart_illustrator_text_font_size = getFontSize(chart_illustrator_text, infoframe_width * 0.85, (w + h) * 0.011)
    
    if len(chart_level_number) == 1:
        chart_level_text_font_size *= 1.35
    
    CoreConfigureEx(PhiCoreConfigEx(
        chart_name_text = chart_name_text,
        chart_name_font_text_size = chart_name_font_text_size,
        chart_artist_text = chart_artist_text,
        chart_artist_text_font_size = chart_artist_text_font_size,
        chart_level_number = chart_level_number,
        chart_level_number_font_size = chart_level_number_font_size,
        chart_level_text = chart_level_text,
        chart_level_text_font_size = chart_level_text_font_size,
        tip = tip,
        tip_font_size = tip_font_size,
        chart_charter_text = chart_charter_text,
        chart_illustrator_text = chart_illustrator_text,
        chart_charter_text_font_size = chart_charter_text_font_size,
        chart_illustrator_text_font_size = chart_illustrator_text_font_size,
    ))
    
    LoadSuccess.play()
    
    animation_st = time.time()
    while True:
        sec = time.time() - animation_st
        p = sec / animation_time
        if p > 1.0:
            break
        
        Task = loadingAnimationFrame(p, sec, clear, fcb)
        Task.ExecTask()
        
def lineOpenAnimation(fcb: typing.Callable[[], typing.Any] = lambda: None):
    csat = 1.25
    st = time.time()
        
    showLine = False
    
    if CHART_TYPE == const.CHART_TYPE.PHI:
        lineWidth = const.LINEWIDTH.PHI
        
        for line in chart_obj.judgeLineList:
            linePos = line.getMove(0.0, w, h)
            lineRotate = line.getRotate(0.0)
            lineAlpha = line.getAlpha(0.0)
            
            if (
                abs(linePos[1] - h / 2) <= 0.001 * h
                and abs(lineRotate) <= 0.001
                and abs(lineAlpha) >= 0.999
            ):
                showLine = True
                break

    elif CHART_TYPE == const.CHART_TYPE.RPE:
        lineWidth = const.LINEWIDTH.RPE
        
        for line in chart_obj.judgeLineList:
            (
                linePos,
                lineAlpha,
                lineRotate
            ) = line.GetState(0.0, (0, 0, 0))[:3]
            
            if (
                abs(linePos[1] - 0.5) <= 0.001 * h
                and abs(lineRotate) <= 0.001
                and abs(lineAlpha) >= 0.999
            ):
                showLine = True
                break
        
    lineWidth *= h
    
    while True:
        p = (time.time() - st) / csat
        if p > 1.0:
            break
        
        fcb()
        val = rpe_easing.ease_funcs[12](p)
        draw_ui(
            animationing = True,
            dy = h / 7 * val
        )
        
        if showLine:
            drawLine(
                w / 2 - (val * w / 2), h / 2,
                w / 2 + (val * w / 2), h / 2,
                strokeStyle = const.JUDGELINE_PERFECT_COLOR,
                lineWidth = lineWidth / render_range_more_scale if render_range_more else lineWidth,
                wait_execute = True
            )
        
        root.run_js_wait_code()
    
    time.sleep(0.15)

def initSettlementAnimation(pplm: tool_funcs.PhigrosPlayLogicManager|None = None):
    global im_size
    global ChartNameString, ChartNameStringFontSize
    global ChartLevelString, ChartLevelStringFontSize
    global ScoreString, LevelName, MaxCombo, AccString
    global PerfectCount, GoodCount, BadCount, MissCount
    global EarlyCount, LateCount
    
    im_size = 0.475
    LevelName = "AP" if not noautoplay else pplm.ppps.getLevelString()
    EarlyCount = 0 if not noautoplay else pplm.ppps.getEarlyCount()
    LateCount = 0 if not noautoplay else pplm.ppps.getLateCount()
    PerfectCount = chart_obj.note_num if not noautoplay else pplm.ppps.getPerfectCount()
    GoodCount = 0 if not noautoplay else pplm.ppps.getGoodCount()
    BadCount = 0 if not noautoplay else pplm.ppps.getBadCount()
    MissCount = 0 if not noautoplay else pplm.ppps.getMissCount()
    Acc = 1.0 if not noautoplay else pplm.ppps.getAcc()
    ScoreString = "1000000" if not noautoplay else stringifyScore(pplm.ppps.getScore())
    MaxCombo = chart_obj.note_num if not noautoplay else pplm.ppps.getMaxCombo()
    AccString = f"{(Acc * 100):.2f}%"
    ChartNameString = chart_information["Name"]
    ChartNameStringFontSize = w * im_size * 0.65 / (root.run_js_code(f"""ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(ChartNameString)}).width;""") / 50)
    ChartLevelString = chart_information["Level"]
    ChartLevelStringFontSize = w * im_size * 0.275 / (root.run_js_code(f"""ctx.font='50px PhigrosFont'; ctx.measureText({root.string2sctring_hqm(ChartLevelString)}).width;""") / 50)
    if ChartNameStringFontSize > w * 0.0275:
        ChartNameStringFontSize = w * 0.0275
    if ChartLevelStringFontSize > w * 0.0275 * 0.55:
        ChartLevelStringFontSize = w * 0.0275 * 0.55

def settlementAnimationFrame(p: float, rjc: bool = True):
    clearCanvas(wait_execute = True)
    im_ease_value = tool_funcs.finish_animation_eases.all_ease(p)
    im_ease_pos = w * 1.25 * (1 - im_ease_value)
    data_block_1_ease_value = tool_funcs.finish_animation_eases.all_ease(p - 0.015)
    data_block_1_ease_pos = w * 1.25 * (1 - data_block_1_ease_value)
    data_block_2_ease_value = tool_funcs.finish_animation_eases.all_ease(p - 0.035)
    data_block_2_ease_pos = w * 1.25 * (1 - data_block_2_ease_value)
    data_block_3_ease_value = tool_funcs.finish_animation_eases.all_ease(p - 0.055)
    data_block_3_ease_pos = w * 1.25 * (1 - data_block_3_ease_value)
    button_ease_value = tool_funcs.finish_animation_eases.button_ease(p * 4.5 - 0.95)
    level_size = 0.1125
    level_size *= tool_funcs.finish_animation_eases.level_size_ease(p)
    button_ease_pos = - w * const.FINISH_UI_BUTTON_SIZE * (1 - button_ease_value)
    
    drawBg()
    
    baimg_w = w * 0.5203125
    baimg_h = h * (624 / 1080)
    dpower = tool_funcs.getDPower(baimg_w, baimg_h, 75)
    
    baimg_rawr = chart_image.width / chart_image.height
    baimg_r = baimg_w / baimg_h
    if baimg_rawr > baimg_r:
        baimg_draww = baimg_h * baimg_rawr
        baimg_drawh = baimg_h
    else:
        baimg_draww = baimg_w
        baimg_drawh = baimg_w / baimg_rawr
    
    root.run_js_code(
        f"""ctx.drawDiagonalRectangleClipImage(\
            {w * 0.315625 - baimg_w / 2 + im_ease_pos}, {h * (539 / 1080) - baimg_h / 2},\
            {w * 0.315625 + baimg_w / 2 + im_ease_pos}, {h * (539 / 1080) + baimg_h / 2},\
            {root.get_img_jsvarname("finish_animation_image")},\
            {baimg_w / 2 - baimg_draww / 2}, {baimg_h / 2 - baimg_drawh / 2},\
            {baimg_draww}, {baimg_drawh}, {dpower}, 1.0\
        );""",
        add_code_array = True
    )
    
    drawText(
        w * 0.0828125 + im_ease_pos,
        h * (815 / 1080),
        text = ChartNameString,
        font = f"{ChartNameStringFontSize}px PhigrosFont",
        textAlign = "left",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF", 
        wait_execute = True
    )
    
    drawText(
        w * 0.48125 + im_ease_pos,
        h * (822 / 1080),
        text = ChartLevelString,
        font = f"{ChartLevelStringFontSize}px PhigrosFont",
        textAlign = "right",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF", 
        wait_execute = True
    )
    
    
    def drawDiagonalDataBlock(sy: float, ey: float, ease_pos: float):
        sy *= h
        ey *= h
        db_x = w * 0.5046875
        db_y = h * (227 / 1080)
        db_width = w * 0.4484375
        db_height = h * (624 / 1080)
        db_dpower = tool_funcs.getDPower(db_width, db_height, 75)
        db_dw = db_dpower * db_width
        sy += db_y
        ey += db_y
        
        db_itemrect = (
            db_x + db_dw * (1.0 - (ey - db_y) / db_height) + ease_pos, sy,
            db_x + db_width - db_dw * ((sy - db_y) / db_height) + ease_pos, ey
        )
        
        drawPolygon(
            tool_funcs.rect2drect(db_itemrect, 75),
            fillStyle = "rgba(0, 0, 0, 0.5)",
            wait_execute = True
        )
    
    drawDiagonalDataBlock(0.0, 312 / 1080, data_block_1_ease_pos)
    drawDiagonalDataBlock(357 / 1080, 467 / 1080, data_block_2_ease_pos)
    drawDiagonalDataBlock(512 / 1080, 622 / 1080, data_block_3_ease_pos)
    
    drawText(
        w * 0.584375 + data_block_1_ease_pos,
        h * (467 / 1080),
        text = ScoreString,
        font = f"{(w + h) / 38}px PhigrosFont",
        textAlign = "left",
        textBaseline = "bottom",
        fillStyle = f"rgba(255, 255, 255, {tool_funcs.finish_animation_eases.score_alpha_ease(p)})",
        wait_execute = True
    )
    
    root.run_js_code(
        f"""ctx.drawAlphaCenterImage(\
            {root.get_img_jsvarname(f"Level_{LevelName}")},\
            {w * 0.8578125 + data_block_1_ease_pos}, {h * (380 / 1080)},\
            {w * level_size}, {w * level_size},\
            {tool_funcs.finish_animation_eases.level_alpha_ease(p)}\
        );""",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {tool_funcs.finish_animation_eases.playdata_alpha_ease(p - 0.02)}",
        add_code_array = True
    )
    
    drawText( # Max Combo
        w * 0.55625 + data_block_2_ease_pos,
        h * (650 / 1080),
        text = f"{MaxCombo}",
        textAlign = "left",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 65}px PhigrosFont",
        wait_execute = True
    )
    
    drawText(
        w * 0.55625 + data_block_2_ease_pos,
        h * (674 / 1080),
        text = "Max Combo",
        textAlign = "left",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 125}px PhigrosFont",
        wait_execute = True
    )
    
    drawText( # Accuracy
        w * 0.878125 + data_block_2_ease_pos,
        h * (650 / 1080),
        text = AccString,
        textAlign = "right",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 65}px PhigrosFont",
        wait_execute = True
    )
    
    drawText(
        w * 0.878125 + data_block_2_ease_pos,
        h * (674 / 1080),
        text = "Accuracy",
        textAlign = "right",
        textBaseline = "bottom",
        fillStyle = "#FFFFFF",
        font = f"{(w + h) / 125}px PhigrosFont",
        wait_execute = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {tool_funcs.finish_animation_eases.playdata_alpha_ease(p - 0.04)}",
        add_code_array = True
    )
    
    def drawDataCount(x: float, text: str, count: int):
        drawText( # Perfect Count
            x + data_block_3_ease_pos,
            h * (826 / 1080),
            text = text,
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = "white",
            font = f"{(w + h) / 185}px PhigrosFont",
            wait_execute = True
        )
        
        drawText(
            x + data_block_3_ease_pos,
            h * (806 / 1080),
            text = f"{count}",
            textAlign = "center",
            textBaseline = "bottom",
            fillStyle = "white",
            font = f"{(w + h) / 75}px PhigrosFont",
            wait_execute = True
        )
    
    def drawELCount(y: float, text: float, count: int):
        drawText(
            w * 0.7764375 + data_block_3_ease_pos,
            y,
            text = text,
            textAlign = "left",
            textBaseline = "bottom",
            fillStyle = "white",
            font = f"{(w + h) / 146}px PhigrosFont",
            wait_execute = True
        )
        
        drawText(
            w * 0.8548125 + data_block_3_ease_pos,
            y,
            text = f"{count}",
            textAlign = "right",
            textBaseline = "bottom",
            fillStyle = "white",
            font = f"{(w + h) / 146}px PhigrosFont",
            wait_execute = True
        )
        
    drawDataCount(w * 0.5515625, "Perfect", PerfectCount)
    drawDataCount(w * 0.6234375, "Good", GoodCount)
    drawDataCount(w * 0.6765625, "Bad", BadCount)
    drawDataCount(w * 0.7296875, "Miss", MissCount)
    drawELCount(h * (794 / 1080), "Early", EarlyCount)
    drawELCount(h * (823 / 1080), "Late", LateCount)
    
    root.run_js_code(
        "ctx.globalAlpha = 1.0;",
        add_code_array = True
    )
    
    Retry_Button_Width = w * const.FINISH_UI_BUTTON_SIZE
    Retry_Button_Height = w * const.FINISH_UI_BUTTON_SIZE / 190 * 145
    Retry_imsize = Retry_Button_Height * 0.3
    
    Continue_Button_Width, Continue_Button_Height = Retry_Button_Width, Retry_Button_Height
    Continue_imsize = Retry_imsize
    
    drawImage( # Retry Button
        "ButtonLeftBlack",
        button_ease_pos, 0,
        width = Retry_Button_Width,
        height = Retry_Button_Height,
        wait_execute = True
    )
    
    drawImage(
        "Retry",
        button_ease_pos + w * const.FINISH_UI_BUTTON_SIZE * 0.3 - Retry_imsize / 2,
        Retry_Button_Height / 2 - (Retry_Button_Height * (8 / 145)) - Retry_imsize / 2,
        width = Retry_imsize,
        height = Retry_imsize,
        wait_execute = True
    )
    
    drawImage( # Continue Button
        "ButtonRightBlack",
        w - button_ease_pos - Continue_Button_Width, h - Continue_Button_Height,
        width = Continue_Button_Width,
        height = Continue_Button_Height,
        wait_execute = True
    )
    
    drawImage(
        "Arrow_Right",
        w - (button_ease_pos + w * const.FINISH_UI_BUTTON_SIZE * 0.35 + Continue_imsize / 2),
        h - (Continue_Button_Height / 2 - (Continue_Button_Height * (8 / 145)) * 1.15 + Continue_imsize / 2),
        width = Continue_imsize,
        height = Continue_imsize,
        wait_execute = True
    )
    
    root.run_js_code(
        "ctx.globalAlpha = 1.0;",
        add_code_array = True
    )
    
    root.run_js_code(
        f"ctx.globalAlpha = {tool_funcs.finish_animation_eases.userinfo_alpha_ease(p - 0.03)}",
        add_code_array = True
    )
    
    # userinfo_right = w * 0.83125
    # userinfo_left = w * 0.7234375
    # userinfo_rect = (
    #     userinfo_left, h * (29 / 1080),
    #     w, h * (133 / 1080)
    # )
    # userinfo_drect = tool_funcs.rect2drect_l(userinfo_rect, 75)
    
    root.run_js_code(
        "ctx.globalAlpha = 1.0;",
        add_code_array = True
    )
    
    if rjc: root.run_js_wait_code()

def lineCloseAimationFrame(p: float, a1_combo: int|None, rjc: bool = True):
    v = p ** 2
    if not noautoplay:
        draw_ui(
            process = 1.0,
            score = ScoreString,
            combo_state = chart_obj.note_num >= 3,
            combo = chart_obj.note_num,
            acc = AccString,
            animationing = True,
            dy = h / 7 * (1 - v)
        )
    else:
        draw_ui(
            process = 1.0,
            score = ScoreString,
            combo_state = a1_combo >= 3,
            combo = a1_combo,
            acc = AccString,
            animationing = True,
            dy = h / 7 * (1 - v)
        )
        
    if rjc: root.run_js_wait_code()
    