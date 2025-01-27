import typing
import base64
import random
import logging
import time
from sys import argv
from os import environ
from dataclasses import dataclass

import numpy
import cv2
from PIL import Image, ImageDraw

import const
import rpe_easing
import binfile
import phira_resource_pack
import tempdir
from light_tool_funcs import *

note_id = -1
random_block_num = eval(argv[argv.index("--random-block-num") + 1]) if "--random-block-num" in argv else 4
rpe_texture_scalemethod = argv[argv.index("--rpe-texture-scalemethod") + 1] if "--rpe-texture-scalemethod" in argv else "by-width"

if rpe_texture_scalemethod not in ("by-width", "by-height"):
    logging.warning(f"Unknown scale method: {rpe_texture_scalemethod}, using 'by-width' instead.")
    rpe_texture_scalemethod = "by-width"

def Get_A_New_NoteId():
    global note_id
    note_id += 1
    return note_id

def newRandomBlocks() -> tuple[tuple[float, float]]:
    return tuple(
        (random.uniform(0.0, 360.0), random.uniform(-0.15, 0.3))
        for _ in range(random_block_num)
    )

bae_bs = 2.15
class begin_animation_eases_class:
    @staticmethod
    def im_ease(x):
        if x <= (1 / bae_bs): return 0.0
        x -= (1 / bae_bs); x /= (1 - (1 / bae_bs))
        a = max(0, 1.4 * x - 0.25) + 0.3
        b = min(a, 1.0)
        return b ** 7
    
    @staticmethod
    def background_ease(x):
        x *= 4
        if x >= 1.0: return 1.0
        if x <= 0.0: return 0.0
        return 1 - (abs(x - 1)) ** 3
    
    @staticmethod
    def tip_alpha_ease(x): #emm... linear
        return min(max(0.0, 3 * x - 0.25), 1.0)
    
    @staticmethod
    def info_data_ease(x):
        if x >= 1.0: return 1.0
        if x <= 0.0: return 0.0
        return 1 - (1 - x) ** 3
    
    @staticmethod
    def background_block_color_alpha_ease(x):
        if x >= 1.0: return 1.0
        if x <= 0.0: return 0.0
        return (1 - x ** 2) ** 0.5

class finish_animation_eases_class:
    @staticmethod
    def all_ease(x):
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        k = 1 - x
        return 1 - k ** 10
    
    @staticmethod
    def score_alpha_ease(x):
        k = 0.125
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2

    @staticmethod
    def level_size_ease(x):
        k = 3.0
        return max(0.5 - (k * max(x - 1 / 6, 0.0)) ** 4, 0.0) + 1.0
    
    @staticmethod
    def level_alpha_ease(x):
        k = 0.25
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2
    
    @staticmethod
    def playdata_alpha_ease(x):
        k = 0.25
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2
    
    @staticmethod
    def userinfo_alpha_ease(x):
        k = 0.1875
        x -= k
        x *= (1 / (1 - k))
        x *= 5.0
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return x ** 2
    
    @staticmethod
    def button_ease(x):
        if x <= 0.0: return 0.0
        if x >= 1.0: return 1.0
        return 1 - (1 - x) ** 3

begin_animation_eases = begin_animation_eases_class()
finish_animation_eases = finish_animation_eases_class()

match rpe_texture_scalemethod:
    case "by-width":
        def conimgsize(w: int, h: int, sw: int, sh: int):
            if w == 0: return 0, 0
            rw = w / const.RPE_WIDTH * sw
            return rw, rw / w * h
        
    case "by-height":
        def conimgsize(w: int, h: int, sw: int, sh: int):
            if h == 0: return 0, 0
            rh = h / const.RPE_HEIGHT * sh
            return rh / h * w, rh

# thanks for HLMC (https://github.com/2278535805)
def rpe_text_tween(sv: str, ev: str, t: float, isfill: bool) -> str:
    if "%P%" in sv and "%P%" in ev:
        sv, ev = sv.replace("%P%", ""), ev.replace("%P%", "")
        if isfill: return sv
        
        try: sv, ev = float(sv), float(ev)
        except ValueError: return "0"
        
        v = sv + t * (ev - sv)
        return f"{v:.0f}" if int(sv) == sv and int(ev) == ev else f"{v:.3f}"
            
    elif not sv and not ev:
        return ""
    elif not ev:
        return rpe_text_tween(ev, sv.replace("%P%", ""), 1.0 - t, isfill)
    elif not sv:
        return ev[:int(t * len(ev))]
    
    else:
        xl, yl = len(sv), len(ev)
        ml = min(xl, yl)
        if sv[:ml] == ev[:ml]:
            take_num = int(round((yl - xl) * t)) + xl
            return sv + ev[xl:take_num]
        else:
            return sv.replace("%P%", "")

def bytes2matlike(data: bytes, w: int, h: int) -> cv2.typing.MatLike:
    buf = numpy.frombuffer(data, dtype=numpy.uint8).reshape((h, w, 4))
    matlike = cv2.cvtColor(buf, cv2.COLOR_BGRA2RGBA)
    return matlike[:, :, :3]

def easeAlpha(p: float):
    if 0.0 <= p <= 0.4: 
        return 1.0 - (1.0 - 2 * p * (0.5 / 0.4)) ** 2
    elif 0.4 <= p <= 0.8:
        return 1.0
    else:
        return (2.0 - 2.0 * ((p - 0.8) * (0.5 / 0.2) + 0.5)) ** 2

def fixorp(p: float):
    return max(0.0, min(1.0, p))

def PhigrosChapterNameAlphaValueTransfrom(p: float):
    if p >= 0.4:
        return 1.0
    return p / 0.4

def PhigrosChapterPlayButtonAlphaValueTransfrom(p: float):
    if p <= 0.6:
        return 0.0
    return (p - 0.6) / 0.4

def PhigrosChapterDataAlphaValueTransfrom(p: float):
    if p <= 0.6:
        return 0.0
    return (p - 0.6) / 0.4

def rect2drect_l(rect: tuple[float], deg: float):
    dpower = getDPower(*getSizeByRect(rect), deg)
    w = rect[2] - rect[0]
    return (
        (rect[0] + w * dpower, rect[1]),
        (rect[2], rect[1]),
        (rect[2], rect[3]),
        (rect[0], rect[3]),
        (rect[0] + w * dpower, rect[1])
    )

def rect2drect(rect: tuple[float], deg: float):
    dpower = getDPower(*getSizeByRect(rect), deg)
    w = rect[2] - rect[0]
    return (
        (rect[0] + w * dpower, rect[1]),
        (rect[2], rect[1]),
        (rect[2] - w * dpower, rect[3]),
        (rect[0], rect[3]),
        (rect[0] + w * dpower, rect[1])
    )

def sliderValueP(value: float, values: tuple[tuple[float, float]]):
    ranges = [(values[i - 1][0], values[i][0], values[i - 1][1], values[i][1]) for i in range(len(values)) if i != 0]
    for r in ranges:
        if r[2] <= value <= r[3]:
            return (value - r[2]) / (r[3] - r[2]) * (r[1] - r[0]) + r[0]
    return 0.0 if value < values[0][1] else 1.0

def sliderValueValue(p: float, values: tuple[tuple[float, float]]):
    ranges = [(values[i - 1][0], values[i][0], values[i - 1][1], values[i][1]) for i in range(len(values)) if i != 0]
    for r in ranges:
        if r[0] <= p <= r[1]:
            return (p - r[0]) / (r[1] - r[0]) * (r[3] - r[2]) + r[2]
    return ranges[0][2] if p < ranges[0][0] else ranges[-1][3]

def cutAnimationIllImage(im: Image.Image):
    imdraw = ImageDraw.Draw(im)
    imdraw.polygon(
        [
            (0, 0),
            (0, im.height),
            (im.width * 0.1, 0),
            (0, 0)
        ],
        fill = "#00000000"
    )
    imdraw.polygon(
        [
            (im.width, 0),
            (im.width, im.height),
            (im.width * (1 - 0.1), im.height),
            (im.width, 0)
        ],
        fill = "#00000000"
    )

def checkOffset(now_t: float, raw_audio_length: float, mixer):
    # must not use set_pos to reset music
    offset_judge_range = (1 / 60) * 4
    
    # if mixer.music.get_busy() and abs(music_offset := now_t - mixer.music.get_pos()) >= offset_judge_range:
    #     if abs(music_offset) < raw_audio_length * 1000 * 0.75:
    #         logging.warning(f"mixer offset > {offset_judge_range:.5f}s, reseted chart time. (offset = {int(music_offset * 1000)}ms)")
    #         return music_offset
        
    return 0.0

def gif2mp4(gif: str):
    tid = random.randint(0, 2 << 31)
    fp = f"{tempdir.createTempDir()}/{tid}.mp4"
    cap = cv2.VideoCapture(gif)
    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    writer = cv2.VideoWriter(fp, cv2.VideoWriter.fourcc(*"h264"), fps, size)
    while True:
        ret, frame = cap.read()
        if not ret: break
        writer.write(frame)
    cap.release()
    writer.release()
    return open(fp, "rb").read(), size

def getShaderDefault(shader: str):
    result = {}
    for line in shader.split("\n"):
        if line.startswith("uniform") and "//" in line and line.count("%") >= 2:
            try:
                name = line.split(";")[0].split(" ")[-1]
                default = list(map(float, line.split("//")[1].replace(" ", "").split("%")[1].split(",")))
                if len(default) == 1: default = default[0]
                result[name] = default
            except Exception as e:
                logging.error(f"shader default parse error: {e}")
    return result

def fixShader(shader: str):
    shader = "\n".join(line for line in shader.split("\n") if not line.strip().startswith("#version"))
    return shader

class PhigrosPlayManager:
    def __init__(self, noteCount: int):
        self.events: list[typing.Literal["P", "G", "B", "M"]] = []
        self.event_offsets: list[float] = [] # the note click offset (s)
        self.noteCount = noteCount
    
    def addEvent(self, event: typing.Literal["P", "G", "B", "M"], offset: float|None = None): # Perfect, Good, Bad, Miss
        self.events.append(event)
        if offset is not None: # offset is only good judge.
            self.event_offsets.append(offset)
    
    def getLineColor(self) -> tuple[int, int, int]:
        if "B" in self.events or "M" in self.events:
            return (255, 255, 255) # White
        if "G" in self.events:
            return phira_resource_pack.globalPack.goodRGB # FC
        return phira_resource_pack.globalPack.perfectRGB # AP

    def getCombo(self):
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                return cut
        return cut
    
    def getAcc(self): # 实时 Acc
        if not self.events: return 1.0
        acc = 0.0
        allcut = len(self.events)
        for e in self.events:
            if e == "P":
                acc += 1.0 / allcut
            elif e == "G":
                acc += 0.65 / allcut
        return acc
    
    def getAccOfAll(self):
        acc = 0.0
        for e in self.events:
            if e == "P":
                acc += 1.0 / self.noteCount
            elif e == "G":
                acc += 0.65 / self.noteCount
        return acc
    
    def getMaxCombo(self):
        r = 0
        cut = 0
        for e in reversed(self.events):
            if e == "P" or e == "G":
                cut += 1
            else:
                r = max(r, cut)
                cut = 0
        return max(r, cut)
    
    def getScore(self):
        return self.getAccOfAll() * 900000 + self.getMaxCombo() / self.noteCount * 100000
    
    def getPerfectCount(self):
        return self.events.count("P")
    
    def getGoodCount(self):
        return self.events.count("G")
    
    def getBadCount(self):
        return self.events.count("B")
    
    def getMissCount(self):
        return self.events.count("M")
    
    def getEarlyCount(self):
        return len(list(filter(lambda x: x > 0, self.event_offsets)))
    
    def getLateCount(self):
        return len(list(filter(lambda x: x < 0, self.event_offsets)))
    
    def getLevelString(self):
        score = self.getScore()
        if self.getPerfectCount() == self.noteCount: return "AP"
        elif self.getBadCount() == 0 and self.getMissCount() == 0: return "FC"
        
        if 0 <= score < 700000:
            return "F"
        elif 700000 <= score < 820000:
            return "C"
        elif 820000 <= score < 880000:
            return "B"
        elif 880000 <= score < 920000:
            return "A"
        elif 920000 <= score < 960000:
            return "S"
        elif 960000 <= score < 1000000:
            return "V"
        elif 1000000 <= score:
            return "AP"
        
        return "F" if score < 0 else "AP"
        
class PPLM_ProxyBase:
    def __init__(self, cobj: typing.Any) -> None: ...
    
    def get_lines(self) -> list[typing.Any]: ...
    def get_all_pnotes(self) -> list[typing.Any]: ...
    def remove_pnote(self, n: typing.Any) -> None: ...
    
    def nproxy_stime(self, n: typing.Any) -> float: ...
    def nproxy_etime(self, n: typing.Any) -> float: ...
    def nproxy_hcetime(self, n: typing.Any) -> float: ...
    
    def nproxy_typein(self, n: typing.Any, ts: tuple[typing.Any]) -> bool: ...
    def nproxy_typeis(self, n: typing.Any, t: typing.Any) -> bool: ...
    def nproxy_typeisnot(self, n: typing.Any, t: typing.Any) -> bool: return not self.nproxy_typeis(n, t)
    def nproxy_phitype(self, n: typing.Any) -> typing.Any: ...
    
    def nproxy_nowpos(self, n: typing.Any) -> tuple[float, float]: ...
    def nproxy_nowrotate(self, n: typing.Any) -> float: ...
    def nproxy_effects(self, n: typing.Any) -> const.ClickEffectType: ...
    
    def nproxy_get_pclicked(self, n: typing.Any) -> bool: ...
    def nproxy_set_pclicked(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_wclick(self, n: typing.Any) -> bool: ...
    def nproxy_set_wclick(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_pclick_offset(self, n: typing.Any) -> float: ...
    def nproxy_set_pclick_offset(self, n: typing.Any, offset: float) -> None: ...
    
    def nproxy_get_ckstate(self, n: typing.Any) -> typing.Any: ...
    def nproxy_set_ckstate(self, n: typing.Any, state: typing.Any) -> None: ...
    def nproxy_get_ckstate_ishit(self, n: typing.Any) -> bool: ...
    
    def nproxy_get_cksound_played(self, n: typing.Any) -> bool: ...
    def nproxy_set_cksound_played(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_missed(self, n: typing.Any) -> bool: ...
    def nproxy_set_missed(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_holdjudged(self, n: typing.Any) -> bool: ...
    def nproxy_set_holdjudged(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_holdjudged_tomanager(self, n: typing.Any) -> bool: ...
    def nproxy_set_holdjudged_tomanager(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_last_testholdmiss_time(self, n: typing.Any) -> float: ...
    def nproxy_set_last_testholdmiss_time(self, n: typing.Any, time: float) -> None: ...
    
    def nproxy_get_safe_used(self, n: typing.Any) -> bool: ...
    def nproxy_set_safe_used(self, n: typing.Any, state: bool) -> None: ...
    
    def nproxy_get_holdclickstate(self, n: typing.Any) -> typing.Any: ...
    def nproxy_set_holdclickstate(self, n: typing.Any, state: typing.Any) -> None: ...
    
    def nproxy_get_pbadtime(self, n: typing.Any) -> float: ...
    def nproxy_set_pbadtime(self, n: typing.Any, time: float) -> None: ...

@dataclass
class PPLM_PC_ClickEvent: time: float
@dataclass
class PPLM_PC_ReleaseEvent: time: float
    
class PhigrosPlayLogicManager:
    def __init__(
            self,
            pplm_proxy: PPLM_ProxyBase,
            ppps: PhigrosPlayManager,
            enable_cksound: bool,
            psound: typing.Callable[[str], typing.Any],
            record: bool = False
        ) -> None:
        
        self.pp = pplm_proxy
        self.ppps = ppps
        self.enable_cksound = enable_cksound
        self.psound = psound
        self.record = record
        
        if self.record:
            self.recorder = binfile.PlayRecorderWriter()
        
        self.pc_clicks: list[PPLM_PC_ClickEvent] = []
        self.pc_clickings: int = 0
        
        self.clickeffects: const.ClickEffectType = []
        self.badeffects: const.BadEffectType = []
        # self.misseffects: const.MissEffectType = []
    
    def pc_click(self, t: float) -> None:
        self.pc_clickings += 1
        self.pc_clicks.append(PPLM_PC_ClickEvent(time=t))
        
        if self.record:
            self.recorder.pc_click(t)
        
    def pc_release(self, t: float) -> None:
        if self.pc_clickings > 0:
            self.pc_clickings -= 1
        
        if self.record:
            self.recorder.pc_release(t)
    
    def pc_update(self, t: float) -> None:
        pnotes = self.pp.get_all_pnotes()
        
        keydown = self.pc_clickings > 0
        
        for i in pnotes.copy():
            if ( # drag / flick range judge
                keydown and
                not self.pp.nproxy_get_wclick(i) and
                self.pp.nproxy_typein(i, (const.NOTE_TYPE.DRAG, const.NOTE_TYPE.FLICK)) and
                abs((self.pp.nproxy_stime(i) - t)) <= const.NOTE_JUDGE_RANGE.GOOD
            ):
                self.pp.nproxy_set_wclick(i, True)
            
            if ( # drag / flick it is time to judge
                self.pp.nproxy_get_wclick(i) and
                not self.pp.nproxy_get_pclicked(i) and
                self.pp.nproxy_stime(i) <= t
            ):
                self.pp.nproxy_set_pclicked(i, True)
                self.pp.nproxy_set_ckstate(i, const.NOTE_STATE.PERFECT)
                self.ppps.addEvent("P")
                self.clickeffects.append((True, t, *self.pp.nproxy_effects(i).pop(0)[1:]))
            
            if ( # play click sound
                self.pp.nproxy_get_pclicked(i) and
                not self.pp.nproxy_get_cksound_played(i) and
                self.pp.nproxy_get_ckstate_ishit(i)
            ):
                if self.enable_cksound:
                    self.psound(self.pp.nproxy_phitype(i))
                    if self.record:
                        self.recorder.clicksound(t, self.pp.nproxy_phitype(i))
                self.pp.nproxy_set_cksound_played(i, True)
            
            if ( # miss judge
                not self.pp.nproxy_get_pclicked(i) and
                not self.pp.nproxy_get_missed(i) and
                self.pp.nproxy_stime(i) - t < -const.NOTE_JUDGE_RANGE.MISS
            ):
                self.pp.nproxy_set_missed(i, True)
                self.ppps.addEvent("M")
            
            if ( # hold holding judge
                keydown and
                self.pp.nproxy_typeis(i, const.NOTE_TYPE.HOLD) and
                self.pp.nproxy_get_pclicked(i) and
                self.pp.nproxy_get_ckstate_ishit(i) and
                self.pp.nproxy_etime(i) - 0.2 >= t
            ):
                self.pp.nproxy_set_last_testholdmiss_time(i, t)
            
            if ( # hold holding miss judge
                not keydown and
                self.pp.nproxy_typeis(i, const.NOTE_TYPE.HOLD) and
                self.pp.nproxy_get_pclicked(i) and
                self.pp.nproxy_get_ckstate_ishit(i) and
                self.pp.nproxy_etime(i) - 0.2 >= t and
                self.pp.nproxy_get_last_testholdmiss_time(i) + 0.16 <= t
            ):
                self.pp.nproxy_set_ckstate(i, const.NOTE_STATE.MISS)
                self.pp.nproxy_set_missed(i, True)
                self.ppps.addEvent("M")
            
            if ( # hold add hit event to manager
                self.pp.nproxy_typeis(i, const.NOTE_TYPE.HOLD) and
                self.pp.nproxy_get_holdjudged(i) and # if judged is true, hold state is perfect/good/ miss(miss at clicking)
                not self.pp.nproxy_get_holdjudged_tomanager(i) and
                self.pp.nproxy_hcetime(i) <= t
            ):
                self.pp.nproxy_set_holdjudged_tomanager(i, True)
                state = self.pp.nproxy_get_ckstate(i)
                if state == const.NOTE_STATE.PERFECT:
                    self.ppps.addEvent("P")
                elif state == const.NOTE_STATE.GOOD:
                    self.ppps.addEvent("G", self.pp.nproxy_get_pclick_offset(i))
            
            if ( # add hold effects
                self.pp.nproxy_typeis(i, const.NOTE_TYPE.HOLD) and
                self.pp.nproxy_get_ckstate_ishit(i) and
                self.pp.nproxy_etime(i) >= t
            ):
                for effect in self.pp.nproxy_effects(i):
                    if effect[0] <= t:
                        self.clickeffects.append((self.pp.nproxy_get_ckstate(i) == const.NOTE_STATE.PERFECT, t, *effect[1:]))
                        self.pp.nproxy_effects(i).remove(effect)
                    else:
                        break
            
            if self.pp.nproxy_typeisnot(i, const.NOTE_TYPE.HOLD) and self.pp.nproxy_stime(i) - t < - const.NOTE_JUDGE_RANGE.MISS * 2:
                self.pp.remove_pnote(i)
            elif self.pp.nproxy_typeis(i, const.NOTE_TYPE.HOLD) and self.pp.nproxy_etime(i) - t < - const.NOTE_JUDGE_RANGE.MISS * 2:
                self.pp.remove_pnote(i)
            elif self.pp.nproxy_stime(i) > t + const.NOTE_JUDGE_RANGE.BAD * 2:
                break
        
        while self.pc_clicks:
            cke = self.pc_clicks.pop()
            
            can_judge_notes = []
            can_use_safe_notes = []
            
            for i in pnotes:
                if (
                    not self.pp.nproxy_get_pclicked(i) and
                    self.pp.nproxy_typein(i, (const.NOTE_TYPE.TAP, const.NOTE_TYPE.HOLD)) and
                    abs((offset := (self.pp.nproxy_stime(i) - cke.time))) <= (
                        const.NOTE_JUDGE_RANGE.BAD \
                            if self.pp.nproxy_typeis(i, const.NOTE_TYPE.TAP) else \
                                const.NOTE_JUDGE_RANGE.GOOD
                    )
                ):
                    can_judge_notes.append((i, offset))
                
                if (
                    self.pp.nproxy_typein(i, (const.NOTE_TYPE.DRAG, const.NOTE_TYPE.FLICK)) and
                    not self.pp.nproxy_get_safe_used(i) and
                    abs((offset := (self.pp.nproxy_stime(i) - cke.time))) <= const.NOTE_JUDGE_RANGE.GOOD
                ):
                    can_use_safe_notes.append((i, offset))

                if self.pp.nproxy_stime(i) > cke.time + const.NOTE_JUDGE_RANGE.BAD * 2:
                    break
            
            can_judge_notes.sort(key = lambda x: abs(x[1]))
            can_use_safe_notes.sort(key = lambda x: x[1])
            
            if not can_judge_notes: continue
            
            n, offset = can_judge_notes[0]
            abs_offset = abs(offset)
            
            if 0.0 <= abs_offset <= const.NOTE_JUDGE_RANGE.PERFECT:
                state = const.NOTE_STATE.PERFECT
                
                self.pp.nproxy_set_ckstate(n, state)
                
                if self.pp.nproxy_typeis(n, const.NOTE_TYPE.HOLD):
                    self.pp.nproxy_set_holdjudged(n, True)
                    self.pp.nproxy_set_holdclickstate(n, state)
                else:
                    self.ppps.addEvent("P")

            elif const.NOTE_JUDGE_RANGE.PERFECT < abs_offset <= const.NOTE_JUDGE_RANGE.GOOD:
                state = const.NOTE_STATE.GOOD

                self.pp.nproxy_set_ckstate(n, state)
                
                if self.pp.nproxy_typeis(n, const.NOTE_TYPE.HOLD):
                    self.pp.nproxy_set_holdjudged(n, True)
                    self.pp.nproxy_set_holdclickstate(n, state)
                else:
                    self.ppps.addEvent("G", offset)
            
            elif const.NOTE_JUDGE_RANGE.GOOD < abs_offset <= const.NOTE_JUDGE_RANGE.BAD: # only tap can goto there
                if can_use_safe_notes and offset < 0.0:
                    drag, _ = can_use_safe_notes[0]
                    if not self.pp.nproxy_get_wclick(drag):
                        self.pp.nproxy_set_wclick(drag, True)
                    self.pp.nproxy_set_safe_used(drag, True)
                    continue
                
                self.pp.nproxy_set_pbadtime(n, cke.time)
                self.pp.nproxy_set_ckstate(n, const.NOTE_STATE.BAD)
                self.ppps.addEvent("B")
                self.badeffects.append((
                    cke.time,
                    self.pp.nproxy_nowrotate(n),
                    self.pp.nproxy_nowpos(n)
                ))
            
            if self.pp.nproxy_get_ckstate(n) != const.NOTE_STATE.MISS:
                self.pp.nproxy_set_pclick_offset(n, offset)
                self.pp.nproxy_set_pclicked(n, True)
            
            if self.pp.nproxy_get_ckstate_ishit(n):
                e = self.pp.nproxy_effects(n).pop(0)
                npos = self.pp.nproxy_nowpos(n)
                self.clickeffects.append((
                    self.pp.nproxy_get_ckstate(n) == const.NOTE_STATE.PERFECT,
                    t,
                    *e[1:-1],
                    eval(f"lambda w, h: ({npos[0]} * w, {npos[1]} * h)") if self.pp.nproxy_typeis(n, const.NOTE_TYPE.HOLD) and self.pp.nproxy_stime(n) >= t else e[-1]
                ))

class FramerateCalculator:
    def __init__(self):
        self._frame_count = 0
        self._frame_lastt = time.perf_counter()
        self._frame_checklimit = 25
        self.framerate = -1
    
    def frame(self):
        self._frame_count += 1
        
        if self._frame_count >= self._frame_checklimit:
            uset = time.perf_counter() - self._frame_lastt
            self.framerate = (self._frame_count / uset) if uset else float("inf")
            self._frame_count = 0
            self._frame_lastt = time.perf_counter()
            
            if self.framerate != float("inf"):
                self._frame_checklimit = self.framerate * 0.1

_TimeoutTaskManagerT = typing.TypeVar("_T")
class TimeoutTaskManager(typing.Generic[_TimeoutTaskManagerT]):
    """
    add_task function t arg must be monotonically incremental 
    """
    
    def __init__(self):
        self.datas = []
        self.valid: typing.Callable[[_TimeoutTaskManagerT], bool] = lambda x: True
        
    def add_task(self, t: float, o: _TimeoutTaskManagerT):
        if self.valid(o):
            self.datas.append((t, o))
    
    def get_task(self, t: float):
        result = []
        
        for i in self.datas.copy():
            tt, o = i
            if tt <= t:
                result.append(o)
                self.datas.remove(i)
            break
            
        return result

if environ.get("ENABLE_JIT", "0") == "1":
    import numba
    
    numbajit_funcs = [
        rotate_point,
        unpack_pos,
        linear_interpolation,
        is_intersect,
        pointInScreen,
        conrpepos,
        aconrpepos,
        inrect,
        inDiagonalRectangle,
        compute_intersection,
        fixorp,
        PhigrosChapterNameAlphaValueTransfrom,
        PhigrosChapterPlayButtonAlphaValueTransfrom,
        PhigrosChapterDataAlphaValueTransfrom,
        getDPower,
        getSizeByRect,
        getCenterPointByRect,
        getLineLength,
        indrect
    ]

    for f in numbajit_funcs:
        globals()[f.__name__] = numba.jit(f)
    efs = rpe_easing.ease_funcs.copy()
    rpe_easing.ease_funcs.clear()
    rpe_easing.ease_funcs.extend(map(numba.jit, efs))
    (*map(lambda x: x(random.uniform(0.0, 1.0)), rpe_easing.ease_funcs), )

    rotate_point(0.0, 0.0, 90, 1.145)
    unpack_pos(1000 * 11 + 45)
    linear_interpolation(0.5, 0.0, 1.0, 0.0, 1.0)
    is_intersect(((0.0, 0.1), (0.0, 0.2)), ((-0.1, 0.1), (0.0, 0.4)))
    pointInScreen((204.2, 1.3), 1920, 1080)
    aconrpepos(*conrpepos(102.4, 30.3))
    inrect(1.3, 13.4, (0.2, 3.1, 0.4, 1.4))
    inDiagonalRectangle(0.0, 0.0, 123.3, 32.2, 3.2, 0.2, 0.4)
    compute_intersection(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    fixorp(2.3)
    PhigrosChapterNameAlphaValueTransfrom(0.7)
    PhigrosChapterPlayButtonAlphaValueTransfrom(0.5)
    PhigrosChapterDataAlphaValueTransfrom(0.1)
    getDPower(24, 42, 75)
    getSizeByRect((0.0, 0.0, 1.0, 4.0))
    getCenterPointByRect((0.0, 0.0, 1.0, 1.0))
    getLineLength(0.0, 0.0, 1.0, 1.0)
    indrect(0.0, 3.0, (0.0, 0.0, 1.0, 4.5), 5.3)
    