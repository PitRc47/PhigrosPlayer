# 难用

import ctypes
import typing
import tkinter as tk
import tkinter.ttk as ttk
from os import system

from PIL import Image, ImageTk

img: Image.Image
tkimg: tuple[float, typing.Optional[ImageTk.PhotoImage]] = (1.0, None)
scale: float = 1.0
img_x: int = 0
img_y: int = 0

def hook_dropfiles_first(hwnd, callback):
    globals()[f"hook_dropfiles_dropfunc_prototype_{hwnd}"] = ctypes.WINFUNCTYPE(*(ctypes.c_uint64,) * 5)(lambda hwnd,msg,wp,lp: [callback([ctypes.windll.shell32.DragQueryFileW(ctypes.c_uint64(wp),0,szFile := ctypes.create_unicode_buffer(260),ctypes.sizeof(szFile)),szFile.value][1]) if msg == 0x233 else None,ctypes.windll.user32.CallWindowProcW(*map(ctypes.c_uint64,(lptr,hwnd,msg,wp,lp)))][1]);ctypes.windll.shell32.DragAcceptFiles(hwnd,True);lptr = ctypes.windll.user32.GetWindowLongPtrA(hwnd,-4);ctypes.windll.user32.SetWindowLongPtrA(hwnd,-4,globals()[f"hook_dropfiles_dropfunc_prototype_{hwnd}"])

def updateImage(flush: bool = False):
    global tkimg
    if tkimg[0] == scale and tkimg[1] is not None and not flush:
        canvas.moveto("image", img_x, img_y)
        return
        
    tkimg = (scale, ImageTk.PhotoImage(img.resize((int(img.width * scale), int(img.height * scale)))))
    
    canvas.delete("all")
    canvas.create_image(img_x, img_y, anchor="nw", image=tkimg[1], tag="image")
    canvas.create_oval(
        0, 0,
        int((w + h) / 400),
        int((w + h) / 400),
        fill="red", outline="red",
        tag="pointer"
    )

def initCanvas(im: Image.Image):
    global img
    
    imr = im.width / im.height
    userr = w / h
    
    if imr > userr:
        cvh = int(h * 0.4)
        im = im.resize((int(cvh * userr), cvh))
    else:
        cvw = int(w * 0.4)
        im = im.resize((cvw, int(cvw / userr)))
    
    img = im
    canvas.config(width=im.width, height=im.height)
    updateImage(flush=True)

def loadImage(path: str):
    try:
        im = Image.open(path).convert("RGB")
        initCanvas(im)
    except Exception as e:
        print(e)

class mouseMover:
    def __init__(self, callback: typing.Callable[[tk.Event], typing.Any]):
        self._mouseIsDown = False
        self._lastx = 0
        self._lasty = 0
        self._x = 0
        self._y = 0
        self.callback = callback
    
    def mouseDown(self, e: tk.Event):
        self._mouseIsDown = True
        self._lastx = e.x
        self._lasty = e.y
        self.mouseMove(e)

    def mouseUp(self, e: tk.Event):
        self._mouseIsDown = False

    def mouseMove(self, e: tk.Event):
        if self._mouseIsDown:
            self._x += e.x - self._lastx
            self._y += e.y - self._lasty
            self._lastx = e.x
            self._lasty = e.y
            self.callback(*self.getpos())
    
    def setto(self, x: int, y: int):
        self._x = x
        self._y = y
        self.callback(*self.getpos())
    
    def getpos(self):
        return self._x, self._y

def immove_callback(x: int, y: int):
    global img_x, img_y
    img_x, img_y = x, y
    updateImage()

def mouseWheel(e: tk.Event):
    global scale
    scale += e.delta / 120 * 2 / 8
    updateImage()

def getres_tonorm(x: int, y: int):
    x -= img_x; y -= img_y
    x /= canvas.winfo_width(); y /= canvas.winfo_height()
    x /= scale; y /= scale
    return x, y

def getres_callback():
    x, y = ptmover.getpos()
    p1 = 0
    p2 = 0
    limit = 10
    
    while True:
        tryx_1 = getres_tonorm(x + p1, 0)[0]
        tryx_2 = getres_tonorm(x - p1, 0)[0]
        tryx1_ok = len(str(tryx_1)) <= limit and tryx_1 <= 1
        tryx2_ok = len(str(tryx_2)) <= limit and tryx_2 >= 0
        
        if tryx1_ok or tryx2_ok:
            p_x = p1 if tryx1_ok else p2
            ans_x = tryx_1 if tryx1_ok else tryx_2
            break
        
        p1 += 1
        p2 -= 1
    
    system("cls")
    print(f"({ans_x}, ({int(getres_tonorm(0, y)[1] * 1080)} / 1080), {p_x})")

ptmover = mouseMover(lambda x, y: canvas.moveto("pointer", x, y))
immover = mouseMover(immove_callback)

root = tk.Tk()
root.withdraw()

root.title("Measurement UI")
root.update()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()

canvas = tk.Canvas(root, highlightthickness=0)
canvas.grid(row=0, column=0, rowspan=500)

canvas.bind("<Button-1>", ptmover.mouseDown)
canvas.bind("<ButtonRelease-1>", ptmover.mouseUp)
canvas.bind("<B1-Motion>", ptmover.mouseMove)

canvas.bind("<Button-3>", immover.mouseDown)
canvas.bind("<ButtonRelease-3>", immover.mouseUp)
canvas.bind("<B3-Motion>", immover.mouseMove)

canvas.bind("<Button-2>", lambda _: ptmover.setto(0, 0))
canvas.bind("<MouseWheel>", mouseWheel)

getres = ttk.Button(root, text="Get Result", command=getres_callback)
getres.grid(row=0, column=1)

hook_dropfiles_first(root.winfo_id(), loadImage)
root.deiconify()
root.mainloop()
