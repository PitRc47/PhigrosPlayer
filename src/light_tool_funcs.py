# this module loads quickly

import math
import typing
from threading import Thread
from os import listdir
from os.path import isfile, abspath

import const

def rotate_point(x, y, θ, r) -> tuple[float, float]:
    xo = r * math.cos(math.radians(θ))
    yo = r * math.sin(math.radians(θ))
    return x + xo, y + yo

def unpack_pos(number: int) -> tuple[int, int]:
    return (number - number % 1000) // 1000, number % 1000

def linear_interpolation(
    t: float,
    st: float, et: float,
    sv: float, ev: float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def easing_interpolation(
    t: float,
    st: float, et: float,
    sv: float, ev: float,
    f: typing.Callable[[float], float]
):
    if t == st: return sv
    return f((t - st) / (et - st)) * (ev - sv) + sv

def is_intersect(
    line_1: tuple[
        tuple[float, float],
        tuple[float, float]
    ],
    line_2: tuple[
        tuple[float, float],
        tuple[float, float]
    ]
) -> bool:
    return not (
        max(line_1[0][0], line_1[1][0]) < min(line_2[0][0], line_2[1][0]) or
        max(line_2[0][0], line_2[1][0]) < min(line_1[0][0], line_1[1][0]) or
        max(line_1[0][1], line_1[1][1]) < min(line_2[0][1], line_2[1][1]) or
        max(line_2[0][1], line_2[1][1]) < min(line_1[0][1], line_1[1][1])
    )

def batch_is_intersect(
    lines_group_1: list[tuple[
        tuple[float, float],
        tuple[float, float]
    ]],
    lines_group_2: list[tuple[
        tuple[float, float],
        tuple[float, float]
    ]]
):
    for i in lines_group_1:
        for j in lines_group_2:
            yield is_intersect(i, j)

def pointInPolygon(ploygon: list[tuple[float, float]], point: tuple[float, float]):
    n = len(ploygon)
    j = n - 1
    res = False
    for i in range(n):
        if (
            (ploygon[i][1] > point[1]) != (ploygon[j][1] > point[1])
            and (
                point[0] < (
                    (ploygon[j][0] - ploygon[i][0])
                    * (point[1] - ploygon[i][1])
                    / (ploygon[j][1] - ploygon[i][1])
                    + ploygon[i][0]
                )
            )
        ):
            res = not res
        j = i
    return res

def getScreenRect(w: int, h: int):
    return [
        ((0, 0), (w, 0)), ((0, 0), (0, h)),
        ((w, 0), (w, h)), ((0, h), (w, h))
    ]

def getScreenPoints(w: int, h: int):
    return [(0, 0), (w, 0), (w, h), (0, h)]

def polygon2lines(p: list[tuple[float, float]]):
    return [(p[i], p[i + 1]) for i in range(-1, len(p) - 1)]

def polygonIntersect(p1: list[tuple[float, float]], p2: list[tuple[float, float]]):
    return (
        any(batch_is_intersect(polygon2lines(p1), polygon2lines(p2)))
        or any(pointInPolygon(p1, i) for i in p2)
        or any(pointInPolygon(p2, i) for i in p1)
    )

def linesInScreen(w: int, h: int, lines: list[tuple[float, float]]):
    return any(batch_is_intersect(
        lines, getScreenRect(w, h)
    )) or any(pointInScreen(j, w, h) for i in lines for j in i)

def polygonInScreen(w: int, h: int, polygon: list[tuple[float, float]]):
    return polygonIntersect(getScreenPoints(w, h), polygon)

def noteCanRender(
    w: int, h: int,
    note_max_size_half: float,
    x: float, y: float,
    hold_points: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
        tuple[float, float]
    ] | None = None
) -> bool: # is type == hold, note_max_size_half is useless
    if hold_points is None: # type != hold
        lt = (x - note_max_size_half, y - note_max_size_half)
        rt = (x + note_max_size_half, y - note_max_size_half)
        rb = (x + note_max_size_half, y + note_max_size_half)
        lb = (x - note_max_size_half, y + note_max_size_half)
    else:
        lt, rt, rb, lb = hold_points
    
    return polygonInScreen(w, h, [lt, rt, rb, lb])

def lineInScreen(w: int|float, h: int|float, line: tuple[float]):
    return linesInScreen(w, h, [((*line[:2], ), (*line[2:], ), )])

def TextureLine_CanRender(
    w: int, h: int,
    texture_max_size_half: float,
    x: float, y: float
) -> bool:
    lt = (x - texture_max_size_half, y - texture_max_size_half)
    rt = (x + texture_max_size_half, y - texture_max_size_half)
    rb = (x + texture_max_size_half, y + texture_max_size_half)
    lb = (x - texture_max_size_half, y + texture_max_size_half)
    
    return polygonInScreen(w, h, [lt, rt, rb, lb])
    
def pointInScreen(point: tuple[float, float], w: int, h: int) -> bool:
    return 0 <= point[0] <= w and 0 <= point[1] <= h

def noteLineOutOfScreen(
    x: float, y: float,
    noteAtJudgeLinePos: tuple[float, float],
    fp: float,
    lineRotate: float,
    lineLength: float,
    lineToNoteRotate: float,
    w: int, h: int,
    note_max_size_half: float
):
    plpttdllotne_line = (
        *rotate_point(x, y, lineRotate, lineLength / 2),
        *rotate_point(x, y, lineRotate + 180, lineLength / 2)
    )
    
    plpttdllotne_cpoint_addfp = rotate_point(
        *noteAtJudgeLinePos,
        lineToNoteRotate,
        fp + 1.0 # add 1.0 px
    )
    
    moved_line = tuple(map(lambda x, y: x + y, plpttdllotne_line, (note_max_size_half, ) * 4))
    
    return (
        not lineInScreen(
            w + note_max_size_half * 2,
            h + note_max_size_half * 2,
            moved_line
        ) and (
            getLineLength(*plpttdllotne_cpoint_addfp, w / 2, h / 2)
            - getLineLength(x, y, w / 2, h / 2)
        ) > 0.0
    )

def ThreadFunc(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs, daemon=True)
        t.start()
        t.join()
    return wrapper

def NoJoinThreadFunc(f):
    def wrapper(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs, daemon=True)
        t.start()
    return wrapper

def conrpepos(x: float, y: float):
    return (
        (x + const.RPE_WIDTH / 2) / const.RPE_WIDTH,
        1.0 - (y + const.RPE_HEIGHT / 2) / const.RPE_HEIGHT
    )

def aconrpepos(x: float, y: float):
    return (
        x * const.RPE_WIDTH - const.RPE_WIDTH / 2,
        (1.0 - y) * const.RPE_HEIGHT - const.RPE_HEIGHT / 2
    )
        
def Format_Time(t: int|float) -> str:
    if t < 0.0: t = 0.0
    m, s = t // 60, t % 60
    m, s = int(m), int(s)
    return f"{m}:{s:>2}".replace(" ", "0")

def inDiagonalRectangle(x0: float, y0: float, x1: float, y1: float, power: float, x: float, y: float):
    x += (y - y0) / (y1 - y0) * (x1 - x0) * power
    return x0 + (x1 - x0) * power <= x <= x1 and y0 <= y <= y1

def compute_intersection(
    x0: float, y0: float,
    x1: float, y1: float,
    x2: float, y2: float,
    x3: float, y3: float
):
    a1 = y1 - y0
    b1 = x0 - x1
    c1 = x1 * y0 - x0 * y1
    a2 = y3 - y2
    b2 = x2 - x3
    c2 = x3 * y2 - x2 * y3
    try:
        return (b2 * c1 - b1 * c2) / (a1 * b2 - a2 * b1), (a1 * c2 - a2 * c1) / (a1 * b2 - a2 * b1)
    except ZeroDivisionError:
        return x0, y0

def getDPower(width: float, height: float, deg: float):
    l1 = 0, 0, width, 0
    l2 = 0, height, *rotate_point(0, height, deg, (width ** 2 + height ** 2) ** 0.5)
    try:
        return compute_intersection(*l1, *l2)[0] / width
    except ZeroDivisionError:
        return 1.0

def getSizeByRect(rect: tuple[float, float, float, float]):
    return rect[2] - rect[0], rect[3] - rect[1]

def getCenterPointByRect(rect: tuple[float, float, float, float]):
    return (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2
    
def getAllFiles(path: str) -> list[str]:
    if path[-1] == "/" or path[:-1] == "\\":
        path = path[:-1]
    path = path.replace("/", "\\")
    files = []
    for item in listdir(path):
        if isfile(f"{path}\\{item}"):
            files.append(f"{path}\\{item}")
        else:
            files.extend(getAllFiles(f"{path}\\{item}"))
    return files

def getLineLength(x0: float, y0: float, x1: float, y1: float):
    return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

def gtpresp(p: str):
    result =  f"./phigros_assets/{p}".replace("\\", "/")
    while "//" in result: result = result.replace("//", "/")
    return result

def inrect(x: float, y: float, rect: tuple[float, float, float, float]) -> bool:
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]

def indrect(x: float, y: float, rect: tuple[float, float, float, float], dpower: float):
    x += (1.0 - (y - rect[1]) / (rect[3] - rect[1])) * (dpower * (rect[2] - rect[0]))
    return inrect(x, y, rect)

def isfloatable(s: str):
    try: float(s); return True
    except: return False

def isallnum(lst: list[str], l: int|None = None):
    return (len(lst) >= l or l is None) and all(map(lambda x: isfloatable(x), lst))

def createBezierFunction(ps: list[float]) -> typing.Callable[[float], float]:
    return lambda t: sum([ps[i] * (1 - t) ** (len(ps) - i - 1) * t ** i for i in range(len(ps))])

def createCuttingEasingFunction(f: typing.Callable[[float], float], l: float, r: float):
    return lambda t: f(t * (r - l) + l)

def pec2rpe_findevent_bytime(es: list[dict], t: float, default: float):
    if not es: return default
    
    ets = list(map(lambda x: abs(x["endTime"][0] - t), es))
    return es[ets.index(min(ets))]["end"]

def pec2rpe(pec: str):
    errs = []
    peclines = pec.replace(" #", "\n#").replace(" &", "\n&").split("\n")
    result = { # if some key and value is not exists, in loading rpe chart, it will be set to default value.
        "META": {},
        "BPMList": [],
        "judgeLineList": []
    }
    
    result["META"]["offset"] = float(peclines.pop(0)) - 150
    
    peclines = list(
        map(
            lambda x: list(filter(lambda x: x, x)),
            map(lambda x: x.split(" "), peclines)
        )
    )
    
    pecbpms = list(filter(lambda x: x and x[0] == "bp" and isallnum(x[1:], 2), peclines))
    pecnotes = list(filter(lambda x: x and x[0] in ("n1", "n2", "n3", "n4") and isallnum(x[1:], 5 if x[0] != "n2" else 6), peclines))
    pecnotespeeds = list(filter(lambda x: x and x[0] == "#" and isallnum(x[1:], 1), peclines))
    pecnotesizes = list(filter(lambda x: x and x[0] == "&" and isallnum(x[1:], 1), peclines))
    peccps = list(filter(lambda x: x and x[0] == "cp" and isallnum(x[1:], 4), peclines))
    peccds = list(filter(lambda x: x and x[0] == "cd" and isallnum(x[1:], 3), peclines))
    peccas = list(filter(lambda x: x and x[0] == "ca" and isallnum(x[1:], 3), peclines))
    peccvs = list(filter(lambda x: x and x[0] == "cv" and isallnum(x[1:], 3), peclines))
    peccms = list(filter(lambda x: x and x[0] == "cm" and isallnum(x[1:], 6), peclines))
    peccrs = list(filter(lambda x: x and x[0] == "cr" and isallnum(x[1:], 5), peclines))
    peccfs = list(filter(lambda x: x and x[0] == "cf" and isallnum(x[1:], 4), peclines))
    
    pecbpms.sort(key = lambda x: float(x[1]))
    
    notezip = list(zip(pecnotes, pecnotespeeds, pecnotesizes))
    notezip.sort(key = lambda x: float(x[0][2]))
    
    peccps.sort(key = lambda x: float(x[1]))
    peccds.sort(key = lambda x: float(x[1]))
    peccas.sort(key = lambda x: float(x[1]))
    peccvs.sort(key = lambda x: float(x[1]))
    peccms.sort(key = lambda x: float(x[1]))
    peccrs.sort(key = lambda x: float(x[1]))
    peccfs.sort(key = lambda x: float(x[1]))
    
    rpex = lambda x: (x / 2048 - 0.5) * const.RPE_WIDTH
    rpey = lambda y: (y / 1400 -  0.5) * const.RPE_HEIGHT
    rpes = lambda s: s / 1400 * const.RPE_HEIGHT
    lines = {}
                    
    checkLine = lambda k: [
        (
            lines.update({k: {
                "eventLayers": [{
                    "speedEvents": [],
                    "moveXEvents": [],
                    "moveYEvents": [],
                    "rotateEvents": [],
                    "alphaEvents": []
                }],
                "notes": []
            }}),
            result["judgeLineList"].append(lines[k])
        ) if k not in lines else None,
    ]
    
    for e in pecbpms:
        try:
            result["BPMList"].append({
                "startTime": [float(e[1]), 0, 1],
                "bpm": float(e[2])
            })
        except Exception as e:
            errs.append(e)
    
    for e, sp, si in notezip:
        try:
            et = None
            if e[0] == "n2": et = [float(e.pop(3)), 0, 1]
            ntype = {"n1": 1, "n2": 2, "n3": 3, "n4": 4}[e[0]]
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            x = float(e[3])
            if et is None: et = st.copy()
            above = int(e[4])
            fake = bool(int(e[5]))
            speed = float(sp[1])
            size = float(si[1])
            
            checkLine(k)
            lines[k]["notes"].append({
                "type": ntype,
                "startTime": st,
                "endTime": et,
                "positionX": x / 2048 * const.RPE_WIDTH,
                "above": above,
                "isFake": fake,
                "speed": speed,
                "size": size
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccps:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            x = float(e[3])
            y = float(e[4])
            
            checkLine(k)
            lines[k]["eventLayers"][0]["moveXEvents"].append({
                "startTime": t, "endTime": t,
                "start": rpex(x), "end": rpex(x),
                "easingType": 1
            })
            lines[k]["eventLayers"][0]["moveYEvents"].append({
                "startTime": t, "endTime": t,
                "start": rpey(y), "end": rpey(y),
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)

    for e in peccds:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            v = float(e[3])
            
            checkLine(k)
            lines[k]["eventLayers"][0]["rotateEvents"].append({
                "startTime": t, "endTime": t,
                "start": v, "end": v,
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccas:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            v = float(e[3])

            checkLine(k)
            lines[k]["eventLayers"][0]["alphaEvents"].append({
                "startTime": t, "endTime": t,
                "start": v, "end": v,
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccvs:
        try:
            k = int(e[1])
            t = [float(e[2]), 0, 1]
            v = float(e[3])

            checkLine(k)
            lines[k]["eventLayers"][0]["speedEvents"].append({
                "startTime": t, "endTime": t,
                "start": rpes(v), "end": rpes(v),
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccms:
        try:
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            et = [float(e[3]), 0, 1]
            ex = float(e[4])
            ey = float(e[5])
            ease = int(e[6])
            
            checkLine(k)
            mxes = lines[k]["eventLayers"][0]["moveXEvents"]
            myes = lines[k]["eventLayers"][0]["moveYEvents"]
            sx = pec2rpe_findevent_bytime(mxes, st[0], rpex(ex))
            sy = pec2rpe_findevent_bytime(myes, st[0], rpey(ey))

            mxes.append({
                "startTime": st, "endTime": et,
                "start": sx, "end": rpex(ex),
                "easingType": ease
            })
            myes.append({
                "startTime": st, "endTime": et,
                "start": sy, "end": rpey(ey),
                "easingType": ease
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccrs:
        try:
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            et = [float(e[3]), 0, 1]
            ev = float(e[4])
            ease = int(e[5])

            checkLine(k)
            res = lines[k]["eventLayers"][0]["rotateEvents"]
            sv = pec2rpe_findevent_bytime(res, st[0], ev)

            res.append({
                "startTime": st, "endTime": et,
                "start": sv, "end": ev,
                "easingType": ease
            })
        except Exception as e:
            errs.append(e)
    
    for e in peccfs:
        try:
            k = int(e[1])
            st = [float(e[2]), 0, 1]
            et = [float(e[3]), 0, 1]
            ev = float(e[4])

            checkLine(k)
            aes = lines[k]["eventLayers"][0]["alphaEvents"]
            sv = pec2rpe_findevent_bytime(aes, st[0], ev)

            aes.append({
                "startTime": st, "endTime": et,
                "start": sv, "end": ev,
                "easingType": 1
            })
        except Exception as e:
            errs.append(e)
    
    return result, errs

def samefile(a: str, b: str):
    a, b = abspath(a), abspath(b)
    a, b = a.replace("\\", "/"), b.replace("\\", "/")
    while "//" in a: a = a.replace("//", "/")
    while "//" in b: b = b.replace("//", "/")
    return a == b

def findfileinlist(fn: str, lst: list[str]):
    for i, f in enumerate(lst):
        if samefile(fn, f):
            return i
    return None

def fileinlist(fn: str, lst: list[str]):
    return findfileinlist(fn, lst) is not None
