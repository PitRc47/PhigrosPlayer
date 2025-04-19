from __future__ import annotations

from dataclasses import dataclass
from random import uniform
import threading
import typing
import time

from PIL import Image

import tool_funcs
import const
import rpe_easing

@dataclass
class ClickEvent:
    rect: tuple[float, float, float, float]
    callback: typing.Callable[[int, int], typing.Any]
    once: bool
    tag: str|None = None
    
    def __hash__(self) -> int:
        return id(self)

@dataclass
class MoveEvent:
    callback: typing.Callable[[int, int], typing.Any]
    tag: str|None = None
    
    def __hash__(self) -> int:
        return id(self)
    
@dataclass
class ReleaseEvent:
    callback: typing.Callable[[int, int], typing.Any]
    tag: str|None = None

    def __hash__(self) -> int:
        return id(self)

@dataclass
class EventManager:
    def __init__(self) -> None:
        self.clickEvents: list[ClickEvent] = []
        self.moveEvents: list[MoveEvent] = []
        self.releaseEvents: list[ReleaseEvent] = []
    
    def _callClickCallback(self, e: ClickEvent, x: int, y: int) -> None:
        if tool_funcs.inrect(x, y, e.rect):
            e.callback(x, y)
            if e.once:
                self.unregEvent(e)
                
    @tool_funcs.NoJoinThreadFunc
    def click(self, x: int, y: int) -> None:
        for e in self.clickEvents:
            self._callClickCallback(e, x, y)
            
    @tool_funcs.NoJoinThreadFunc
    def move(self, x: int, y: int) -> None:
        for e in self.moveEvents:
            e.callback(x, y)
    
    @tool_funcs.NoJoinThreadFunc
    def release(self, x: int, y: int) -> None:
        for e in self.releaseEvents:
            e.callback(x, y)
    
    def regClickEvent(self, e: ClickEvent):
        self.clickEvents.append(e)
    
    def regMoveEvent(self, e: MoveEvent):
        self.moveEvents.append(e)

    def regReleaseEvent(self, e: ReleaseEvent):
        self.releaseEvents.append(e)
    
    def regClickEventFs(self, callback: typing.Callable[[int, int], typing.Any], once: bool):
        e = ClickEvent((0, 0, float("inf"), float("inf")), callback, once)
        self.regClickEvent(e)
        return e
    
    def regReleaseEventFs(self, callback: typing.Callable[[int, int], typing.Any]):
        e = ReleaseEvent(callback)
        self.regReleaseEvent(e)
        return e
    
    def unregEvent(self, e: ClickEvent):
        for elist in [self.clickEvents, self.moveEvents, self.releaseEvents]:
            try:
                elist.remove(e)
            except ValueError:
                pass
    
    def unregEventByChooseChartControl(self, ccc: ChooseChartControl):
        for e in self.clickEvents:
            if e.callback is ccc.scter_mousedown:
                self.unregEvent(e)
                break
                
        for e in self.releaseEvents:
            if e.callback is ccc.scter_mouseup:
                self.unregEvent(e)
                break
        
        for e in self.moveEvents:
            if e.callback is ccc.scter_mousemove:
                self.unregEvent(e)
                break

@dataclass
class FaculaAnimationManager:
    def __init__(self) -> None:
        self.faculas = []
    
    def main(self):
        self._createFacula()
        self._createFacula()
        while True:
            time.sleep(uniform(0.35, 1.25))
            self._createFacula()
            for facula in self.faculas:
                if facula["endTime"] < time.time():
                    self.faculas.remove(facula)
    
    def getFaculaState(self, facula: dict) -> dict:
        p = (time.time() - facula["startTime"]) / (facula["endTime"] - facula["startTime"]) # cannot use tool_funcs.linear_interpolation, it will return 0.0, i tkink is jit bug?. or f32 precision problem?
        if p <= 0.2:
            ep = 1.0 - (1.0 - (p / 0.2)) ** 2
        elif p <= 0.8:
            ep = 1.0
        else:
            ep = (1.0 - (p - 0.8) / 0.2) ** 2
        
        return {
            "y": facula["sy"] + (facula["ey"] - facula["sy"]) * p,
            "size": ep * facula["size"],
            "alpha": ep
        }
            
    def _createFacula(self):
        sy = uniform(0.0, 1.0)
        self.faculas.append({
            "startTime": time.time(),
            "endTime": time.time() + uniform(5.0, 7.0),
            "x": uniform(0.05, 0.95),
            "sy": sy,
            "ey": sy - uniform(0.5, 0.7),
            "size": uniform(0.7, 1.3)
        })

@dataclass
class SongDifficlty:
    name: str
    level: str
    chart_audio: str
    chart_image: str
    chart_file: str
    charter: str
    iller: str
    
@dataclass
class Song:
    name: str
    composer: str
    image: str
    preview: str
    difficlty: list[SongDifficlty]
    
    def __post_init__(self):
        self.songId = int(uniform(0.0, 1.0) * (2 << 31))

@dataclass
class Chapter:
    name: str
    cn_name: str
    o_name: str
    image: str
    songs: list[Song]
    im: None|Image.Image = None
    
    def __post_init__(self):
        self.chapterId = int(uniform(0.0, 1.0) * (2 << 31))
    
    def __hash__(self):
        return id(self)

@dataclass
class Chapters:
    items: list[Chapter]
    aFrom: int = -1
    aTo: int = 0
    aSTime: float = float("-inf")

@dataclass
class Setting:
    offset: int = 0 # ms, -400 ~ 600
    scale: float = 1.0 # 1.0 ~ 1.3
    background_dim: float = 1.0 # 0.2 ~ 1.0 (?)
    enable_click_sound: bool = True
    sound_volume: float = 1.0 # 0.0 ~ 1.0
    ui_volume: float = 1.0 # 0.0 ~ 1.0
    click_sound_volume: float = 1.0 # 0.0 ~ 1.0
    moerbets_auxiliary: bool = True
    fcap_indicator: bool = True
    low_quality: bool = False
    
@dataclass
class SettingState:
    aFrom: int = const.PHIGROS_SETTING_STATE.PLAY
    aTo: int = const.PHIGROS_SETTING_STATE.PLAY
    aSTime: float = float("-inf")
    
    def __post_init__(self):
        self._ease_fast = rpe_easing.ease_funcs[11]
        self._ease_slow = rpe_easing.ease_funcs[12]
        self.atime = 0.65
    
    def getBarWidth(self):
        sv = const.PHIGROS_SETTING_BAR_WIDTH_MAP[self.aFrom]
        ev = const.PHIGROS_SETTING_BAR_WIDTH_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self.atime
        p = (time.time() - st) / (et - st)
        p = tool_funcs.fixorp(p)
        p = self._ease_slow(p)
        return p * (ev - sv) + sv
    
    def getLabelWidth(self):
        sv = const.PHIGROS_SETTING_LABEL_WIDTH_MAP[self.aFrom]
        ev = const.PHIGROS_SETTING_LABEL_WIDTH_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self.atime
        p = (time.time() - st) / (et - st)
        p = tool_funcs.fixorp(p)
        p = self._ease_fast(p)
        return p * (ev - sv) + sv
    
    def getLabelX(self):
        sv = const.PHIGROS_SETTING_LABEL_X_MAP[self.aFrom]
        ev = const.PHIGROS_SETTING_LABEL_X_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self.atime
        p = (time.time() - st) / (et - st)
        p = tool_funcs.fixorp(p)
        p = self._ease_slow(p)
        return p * (ev - sv) + sv
    
    def _lerFromTextColor(self, p: float):
        return (255 * p, ) * 3
    
    def _lerToTextColor(self, p: float):
        return (255 * (1.0 - p), ) * 3
    
    def getTextColor(self, t: int):
        if t not in (self.aFrom, self.aTo):
            return (255, 255, 255)
        elif self.aSTime == float("-inf"):
            return (0, 0, 0) # aFrom and aTo is 1
        else:
            st = self.aSTime
            et = self.aSTime + self.atime
            p = (time.time() - st) / (et - st)
            p = tool_funcs.fixorp(p)
            
            # 这里奇怪的算法: 为了视觉上好看和还原一点
            absv = abs(self.aFrom - self.aTo) if self.aFrom != self.aTo else 1.0
            absv += 0.5
            absv **= 1.25
            if t == self.aFrom:
                p = 1.0 - (1.0 - p) ** absv
            else:
                p = 1.0 - (1.0 - p) ** (1 / absv)
                
            return self._lerFromTextColor(p) if self.aFrom == t else self._lerToTextColor(p)
    
    def getTextScale(self, t: int):
        if t not in (self.aFrom, self.aTo):
            return 1.0
        elif self.aSTime == float("-inf"):
            return 1.175
        else:
            st = self.aSTime
            et = self.aSTime + self.atime
            p = (time.time() - st) / (et - st)
            p = tool_funcs.fixorp(p)
            p = self._ease_slow(p)
            
            return tool_funcs.linear_interpolation(p, 0.0, 1.0, 1.175, 1.0) if self.aFrom == t else tool_funcs.linear_interpolation(p, 0.0, 1.0, 1.0, 1.175)
    
    def getShadowRect(self):
        sv = const.PHIGROS_SETTING_SHADOW_XRECT_MAP[self.aFrom]
        ev = const.PHIGROS_SETTING_SHADOW_XRECT_MAP[self.aTo]
        if self.aSTime == float("-inf"):
            return ev
        st = self.aSTime
        et = self.aSTime + self.atime
        p = (time.time() - st) / (et - st)
        p = tool_funcs.fixorp(p)
        p = self._ease_slow(p)
        return (
            p * (ev[0] - sv[0]) + sv[0],
            p * (ev[1] - sv[1]) + sv[1]
        )
        
    def changeState(self, state: int):
        self.aFrom, self.aTo = self.aTo, state
        self.aSTime = time.time()
    
    def getSettingDx(self, shadowRectLeft: float, w: int, t: int):
        return (const.PHIGROS_SETTING_SHADOW_XRECT_MAP[t][0] - shadowRectLeft) * w
        
    def render(
        self,
        drawPlaySetting: typing.Callable[[float, float], None],
        drawAccountAndCountSetting: typing.Callable[[float, float], None],
        drawOtherSetting: typing.Callable[[float, float], None],
        shadowRectLeft: float, w: int,
        settingDx: list[float]
    ):
        sp_state = self.aFrom == self.aTo # before user change ui state
        if sp_state:
            self.aFrom = const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT
            self.aTo = const.PHIGROS_SETTING_STATE.PLAY
        
        st = self.aSTime
        et = self.aSTime + self.atime
        p = (time.time() - st) / (et - st) if self.aSTime != float("-inf") else 1.0
        p = tool_funcs.fixorp(p)
        p = self._ease_slow(p)
        
        drawPlaySettingDx = self.getSettingDx(shadowRectLeft, w, const.PHIGROS_SETTING_STATE.PLAY)
        drawAccountAndCountSettingDx = self.getSettingDx(shadowRectLeft, w, const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT)
        drawOtherSettingDx = self.getSettingDx(shadowRectLeft, w, const.PHIGROS_SETTING_STATE.OTHER)

        drawPlaySettingAlpha = 0.0 if const.PHIGROS_SETTING_STATE.PLAY not in (self.aFrom, self.aTo) else ((1.0 - p) if self.aFrom == const.PHIGROS_SETTING_STATE.PLAY else p)
        drawAccountAndCountSettingAlpha = 0.0 if const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT not in (self.aFrom, self.aTo) else ((1.0 - p) if self.aFrom == const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT else p)
        drawOtherSettingAlpha = 0.0 if const.PHIGROS_SETTING_STATE.OTHER not in (self.aFrom, self.aTo) else ((1.0 - p) if self.aFrom == const.PHIGROS_SETTING_STATE.OTHER else p)

        drawPlaySetting(drawPlaySettingDx, drawPlaySettingAlpha)
        drawAccountAndCountSetting(drawAccountAndCountSettingDx, drawAccountAndCountSettingAlpha)
        drawOtherSetting(drawOtherSettingDx, drawOtherSettingAlpha)
        settingDx.clear()
        settingDx.extend([drawPlaySettingDx, drawAccountAndCountSettingDx, drawOtherSettingDx])
        
        if sp_state:
            self.aFrom = const.PHIGROS_SETTING_STATE.PLAY
            self.aTo = const.PHIGROS_SETTING_STATE.PLAY

    @property
    def atis_p(self): return self.aTo == const.PHIGROS_SETTING_STATE.PLAY
    @property
    def atis_a(self): return self.aTo == const.PHIGROS_SETTING_STATE.ACCOUNT_AND_COUNT
    @property
    def atis_o(self): return self.aTo == const.PHIGROS_SETTING_STATE.OTHER

@dataclass
class PhiBaseWidget:
    tonext: float = 0.0
    
    def MouseDown(self, x: int, y: int): ...
    def MouseUp(self, x: int, y: int): ...
    def MouseMove(self, x: int, y: int): ...
    def InRect(self, x: int, y: int): return False
    
@dataclass
class PhiLabel(PhiBaseWidget):
    left_text: str = ""
    right_text: str = ""
    fontsize: float = 1.0
    color: str = "#FFFFFF"
    
@dataclass
class PhiSlider(PhiBaseWidget):
    value: float = 0.0
    number_points: tuple[tuple[float, float]] = ((0.0, 0.0), (1.0, 1.0))
    lr_button: bool = False
    sliderUnit: float = float("nan")
    conUnit: float = 0.0
    numberType: typing.Union[int, float] = float
    command: typing.Callable[[], typing.Any] = lambda *args, **kwargs: None
    
    sliderRect = (0.0, 0.0, 0.0, 0.0)
    lconButtonRect = (0.0, 0.0, 0.0, 0.0)
    rconButtonRect = (0.0, 0.0, 0.0, 0.0)
    _mouseDown: bool = False
    
    def _fixValue(self):
        self.value = self.number_points[0][1] if self.value < self.number_points[0][1] else (
            self.number_points[-1][1] if self.value > self.number_points[-1][1] else self.value
        )
        self.value = self.numberType(self.value)
        
        self.command()
    
    def _SliderEvent(self, x: int, y: int):
        if not self._mouseDown or (
            tool_funcs.inrect(x, y, self.rconButtonRect)
            or tool_funcs.inrect(x, y, self.lconButtonRect)
        ):
            return
        
        p = (x - self.sliderRect[0]) / (self.sliderRect[2] - self.sliderRect[0])
        p = 0.0 if p < 0.02 else (1.0 if p > 0.97 else p)
        v = tool_funcs.sliderValueValue(p, self.number_points)
        if self.sliderUnit != self.sliderUnit: # nan
            self.value = v
        else:
            up = v / self.sliderUnit
            up = int(up) if abs(up) % 1.0 < 0.5 else int(up) + 1
            self.value = up * self.sliderUnit
        
        self._fixValue()
    
    def _ConButtonEvent(self, x: int, y: int):
        if tool_funcs.inrect(x, y, self.lconButtonRect):
            self.value -= self.conUnit
            
        elif tool_funcs.inrect(x, y, self.rconButtonRect):
            self.value += self.conUnit
        
        self._fixValue()
    
    def MouseDown(self, x: int, y: int):
        self._mouseDown = self.InRect(x, y)
        self._SliderEvent(x, y)
        self._ConButtonEvent(x, y)
        
    def MouseUp(self, x: int, y: int):
        self._mouseDown = False
    
    def MouseMove(self, x: int, y: int):
        if self._mouseDown:
            self._SliderEvent(x, y)
    
    def InRect(self, x: int, y: int):
        return any([
            tool_funcs.inrect(x, y, self.sliderRect),
            tool_funcs.inrect(x, y, self.lconButtonRect),
            tool_funcs.inrect(x, y, self.rconButtonRect)
        ])
    
@dataclass
class PhiCheckbox(PhiBaseWidget):
    text: str = ""
    fontsize: float = 1.0
    checked: bool = False
    command: typing.Callable[[], typing.Any] = lambda *args, **kwargs: None
    
    check_animation_st: float = float("-inf")
    checkboxRect = (0.0, 0.0, 0.0, 0.0)
    _mouseDown: bool = False
    
    def MouseDown(self, x: int, y: int):
        self._mouseDown = self.InRect(x, y)
    
    def MouseUp(self, x: int, y: int):
        if self._mouseDown and self.InRect(x, y):
            self.checked = not self.checked
            self.check_animation_st = time.time()
            self.command()
        self._mouseDown = False
    
    def InRect(self, x: int, y: int):
        return tool_funcs.inrect(x, y, self.checkboxRect)

@dataclass
class PhiButton(PhiBaseWidget):
    text: str = ""
    fontsize: float = 1.0
    width: float = 0.0
    command: typing.Callable[[], typing.Any] = lambda *args, **kwargs: None

    buttonRect = (0.0, 0.0, 0.0, 0.0)

    def MouseDown(self, x: int, y: int):
        if self.InRect(x, y):
            self.command()

    def InRect(self, x: int, y: int):
        return tool_funcs.inrect(x, y, self.buttonRect)

class WidgetEventManager:
    def __init__(self, widgets: list[PhiBaseWidget], condition: typing.Callable[[int, int], bool]):
        self.widgets = widgets
        self.condition = condition
    
    def MouseDown(self, x: int, y: int):
        if not self.condition(x, y): return
        for widget in self.widgets:
            widget.MouseDown(x, y)

    def MouseUp(self, x: int, y: int):
        if not self.condition(x, y): return
        for widget in self.widgets:
            widget.MouseUp(x, y)

    def MouseMove(self, x: int, y: int):
        if not self.condition(x, y): return
        for widget in self.widgets:
            widget.MouseMove(x, y)
    
    def InRect(self, x: int, y: int):
        if not self.condition(x, y): return False
        for widget in self.widgets:
            if widget.InRect(x, y):
                return True
        return False

class SlideControler:
    def __init__(
        self,
        eventRect: typing.Callable[[int, int], bool],
        setFunc: typing.Callable[[float, float], typing.Any],
        minValueX: float, maxValueX: float,
        minValueY: float, maxValueY: float,
        w: int, h: int
    ):
        self.eventRect = eventRect
        self.setFunc = setFunc
        self.minValueX, self.maxValueX = minValueX, maxValueX
        self.minValueY, self.maxValueY = minValueY, maxValueY
        self.w, self.h = w, h
        self._lastlastclickx, self._lastclicky = 0.0, 0.0
        self._lastclickx, self._lastclicky = 0.0, 0.0
        self._dx, self._dy = 0.0, 0.0
        self._mouseDown = False
    
    def mouseDown(self, x: int, y: int):
        if not self.eventRect(x, y):
            return
        
        self._lastclickx, self._lastclicky = x, y
        self._lastlastclickx, self._lastlastclicky = x, y
        self._mouseDown = True
    
    def mouseUp(self, x: int, y: int):
        if self._mouseDown:
            threading.Thread(target=self._easeSroll, daemon=True).start()
            
        self._mouseDown = False
    
    def mouseMove(self, x: int, y: int):
        if not self._mouseDown:
            return
        
        self._dx += x - self._lastclickx
        self._dy += y - self._lastclicky
        self._lastlastclickx, self._lastlastclicky = self._lastclickx, self._lastclicky
        self._lastclickx, self._lastclicky = x, y
        self._set()
    
    def setDx(self, v: float): self._dx = v
    def setDy(self, v: float): self._dy = v
    def getDx(self): return self._dx
    def getDy(self): return self._dy
    
    def _easeSroll(self):
        dx = self._lastclickx - self._lastlastclickx
        dy = self._lastclicky - self._lastlastclicky
        called_easeBackX, called_easeBackY = False, False
        dx *= 1.2; dy *= 1.2
        
        while abs(dx) > self.w * 0.001 or abs(dy) > self.h * 0.001:
            dx *= 0.92; dy *= 0.92
            self._dx += dx; self._dy += dy
            self._set()
            
            # 往右 = 负, 左 = 正, 反的, 所以`- self._d(x / y)`
            
            if - self._dx <= - self.minValueX or - self._dx >= self.maxValueX - self.minValueX:
                threading.Thread(target=self._easeBackX, daemon=True).start()
                called_easeBackX = True
                dx = 0.0
            
            if - self._dy <= - self.minValueY or - self._dy >= self.maxValueY - self.minValueY:
                threading.Thread(target=self._easeBackY, daemon=True).start()
                called_easeBackY = True
                dy = 0.0
            
            time.sleep(1 / 120)
            
        if not called_easeBackX:
            threading.Thread(target=self._easeBackX, daemon=True).start()
        if not called_easeBackY:
            threading.Thread(target=self._easeBackY, daemon=True).start()
    
    def _easeBackX(self):
        cdx = - self._dx
        if self.minValueX <= cdx <= self.maxValueX:
            return
        
        if cdx < 0:
            dx = - cdx
        else:
            dx = self.maxValueX - cdx
        dx *= -1 # 前面cdx = 负的, 所以变回来
        if self._dx + dx > 0: # 超出左界
            dx = - self._dx
        
        lastv, av, ast = 0.0, 0.0, time.time()
        while True:
            p = (time.time() - ast) / 0.75
            if p > 1.0:
                self._dx += dx - av
                self._set()
                break
            
            v = 1.0 - (1.0 - p) ** 4
            dxv = (v - lastv) * dx
            av += dxv
            self._dx += dxv
            self._set()
            lastv = v

            time.sleep(1 / 120)
    
    def _easeBackY(self):
        cdy = - self._dy
        if self.minValueY <= cdy <= self.maxValueY:
            return
        
        if cdy < 0:
            dy = - cdy
        else:
            dy = self.maxValueY - cdy
        dy *= -1 # 前面cdy = 负的, 所以变回来
        if self._dy + dy > 0: # 超出左界
            dy = - self._dy
        
        lastv, av, ast = 0.0, 0.0, time.time()
        while True:
            p = (time.time() - ast) / 0.75
            if p > 1.0:
                self._dy += dy - av
                self._set()
                break
            
            v = 1.0 - (1.0 - p) ** 4
            dyv = (v - lastv) * dy
            av += dyv
            self._dy += dyv
            self._set()
            lastv = v

            time.sleep(1 / 120)

    def _set(self):
        self.setFunc(self._dx, self._dy)

class ChooseChartControl:
    def __init__(
        self, chapter: Chapter,
        w: int, h: int # screen size
    ):
        self._chapter = chapter
        self._songIndex = 0
        self._songLastIndex = 0
        self._songLastChooseSt = -float("inf")
        self._chartsShadowRect = (
            w * -0.009375, 0,
            w * 0.4921875, h
        )
        self._chartsShadowRectDPower = tool_funcs.getDPower(*tool_funcs.getSizeByRect(self._chartsShadowRect), 75)
        
        self._slideControl = SlideControler(
            eventRect = lambda x, y: tool_funcs.indrect(x, y, self._chartsShadowRect, self._chartsShadowRectDPower),
            setFunc = self._slide_setfunc,
            minValueX = 0.0, maxValueX = 0.0,
            minValueY = 0.0, maxValueY = 0.0,
            w = h, h = h
        )
        self.scter_mousedown = self._slideControl.mouseDown
        self.scter_mouseup = self._slideControl.mouseUp
        self.scter_mousemove = self._slideControl.mouseMove
    
    def _slide_setfunc(self, x: float, y: float):
        print(y)

@dataclass
class ChartChooseUI_State:
    sliding_index: int = 0
    song_index: int = 0
    sort_reverse: bool = False
    sort_method: int = const.PHI_SORTMETHOD.DEFAULT

    def next_sort_method(self):
        tempmethod = self.sort_method + 1
        
        if tempmethod > const.PHI_SORTMETHOD.SCORE:
            tempmethod = const.PHI_SORTMETHOD.DEFAULT
            
        self.sort_method = tempmethod