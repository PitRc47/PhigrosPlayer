from __future__ import annotations

import typing

import webcv

root: webcv.WebCanvas

__all__ = (
    "clearCanvas",
    "drawLine",
    "drawText",
    "drawPolygon",
    "drawImage",
)
transparent = "rgba(0, 0, 0, 0)"
number = int|float

def clearCanvas(wait_execute: bool = False):
    root.run_js_code("ctx.clear();", wait_execute)
    
def drawLine(
    x0: number, y0: number,
    x1: number, y1: number,
    lineWidth: number = 1,
    strokeStyle: str = transparent,
    wait_execute: bool = False
):
    code = []
    code.append("ctx.save();")
    code.append(f"ctx.lineWidth = {lineWidth};")
    code.append(f"ctx.strokeStyle = '{strokeStyle}';")
    code.append(f"ctx.beginPath();")
    code.append(f"ctx.moveTo({x0}, {y0});")
    code.append(f"ctx.lineTo({x1}, {y1});")
    code.append("ctx.stroke();")
    code.append("ctx.restore();")
    root.run_js_code("".join(code), wait_execute)

def drawText(
    x: number, y: number,
    text: str, font: typing.Optional[str] = None,
    textAlign: typing.Literal["start", "end", "left", "right", "center"] = "left",
    textBaseline: typing.Literal["top", "hanging", "middle", "alphabetic", "ideographic", "bottom"] = "middle",
    fillStyle: str = transparent,
    strokeStyle: str = transparent,
    method: typing.Literal["fill", "stroke"] = "fill",
    maxwidth: typing.Optional[number] = None,
    wait_execute: bool = False
):
    text = root.string2sctring_hqm(text)
    code = []
    code.append("ctx.save();")
    code.append(f"ctx.font = '{font}';") if font is not None else None
    code.append(f"ctx.textAlign = '{textAlign}';")
    code.append(f"ctx.textBaseline = '{textBaseline}';")
    code.append(f"ctx.fillStyle = '{fillStyle}';") if method == "fill" else None
    code.append(f"ctx.strokeStyle = '{strokeStyle}';") if method == "stroke" else None
    code.append(f"""ctx.{method}Text({text}, {x}, {y}, {maxwidth if maxwidth is not None else "undefined"});""")
    code.append("ctx.restore();")
    root.run_js_code("".join(code), wait_execute)

def drawPolygon(
    points: typing.Iterable[tuple[number, number]],
    fillStyle: str = transparent,
    strokeStyle: str = transparent,
    lineWidth: number = 1,
    method: typing.Literal["fill", "stroke"] = "fill",
    wait_execute: bool = False
):
    code = []
    code.append("ctx.save();")
    code.append(f"ctx.fillStyle = '{fillStyle}';") if method == "fill" else None
    code.append(f"ctx.strokeStyle = '{strokeStyle}';") if method == "stroke" else None
    code.append(f"ctx.lineWidth = {lineWidth};")
    code.append(f"ctx.beginPath();")
    code.append(f"ctx.moveTo({points[0][0]}, {points[0][1]});")
    code.extend(f"ctx.lineTo({x}, {y});" for x, y in points[1:])
    code.append("ctx.closePath();")
    code.append("ctx.fill();") if method == "fill" else None
    code.append("ctx.stroke();") if method == "stroke" else None
    code.append("ctx.restore();")
    root.run_js_code("".join(code), wait_execute)

def drawImage(
    imname: str,
    x: number, y: number,
    width: number, height: number,
    wait_execute: bool = False
):
    jvn = root.get_img_jsvarname(imname)
    root.run_js_code(f"ctx.drawImage({jvn}, {x}, {y}, {width}, {height});", wait_execute)