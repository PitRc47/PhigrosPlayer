import math
import typing

ease_funcs: list[typing.Callable[[float], float]] = [
    lambda t: t, # 0 - linear
    lambda t: 1 - math.cos(t * math.pi / 2), # 1 - inSine
    lambda t: math.sin(t * math.pi / 2), # 2 - outSine
    lambda t: (1 - math.cos(t * math.pi)) / 2, # 3 - inOutSine
    lambda t: t ** 2, # 4 - inCubic
    lambda t: 1 - (t - 1) ** 2, # 5 - outCubic
    lambda t: (t ** 2 if (t := t * 2) < 1 else -((t - 2) ** 2 - 2)) / 2, # 6 - inOutCubic
    lambda t: t ** 3, # 7 - inQuint
    lambda t: 1 + (t - 1) ** 3, # 8 - outQuint
    lambda t: (t ** 3 if (t := t * 2) < 1 else (t - 2) ** 3 + 2) / 2, # 9 - inOutQuint
    lambda t: t ** 4, # 10 - inCirc
    lambda t: 1 - (t - 1) ** 4, # 11 - outCirc
    lambda t: (t ** 4 if (t := t * 2) < 1 else -((t - 2) ** 4 - 2)) / 2, # 12 - inOutCirc
    lambda _: 0, # 13 - zero
    lambda _: 1 # 14 - one
]
