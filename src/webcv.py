from __future__ import annotations

import fix_workpath as _
import imageload_hook as _
import init_logging as _
import checksys
import json
import threading
import typing
import http.server
import io
import time
import socket
import sys
import logging

from os.path import abspath
from random import randint



import webview
from PIL import Image

import graplib_webview

screen_width = None
screen_height = None
if checksys.main == "Windows":
    from ctypes import windll
    screen_width = windll.user32.GetSystemMetrics(0)
    screen_height = windll.user32.GetSystemMetrics(1)
elif checksys.main == 'Android':
    from jnius import autoclass # type: ignore
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    metrics = PythonActivity.mActivity.getResources().getDisplayMetrics()
    screen_width = metrics.widthPixels
    screen_height = metrics.heightPixels

host = socket.gethostbyname(socket.gethostname()) if "--nolocalhost" in sys.argv else "127.0.0.1"
logging.info(f"server host: {host}")

framerate_counter = '''\
(() => {

_frame_count = 0;
_frame_lastreftime = performance.now();
_framerate_ckeck_limit = 25;
framerate = -1;

_frame_counter = () => {
    _frame_count++;
    
    if (_frame_count >= _framerate_ckeck_limit) {
        const uset = performance.now() - _frame_lastreftime;
        framerate = uset != 0.0 ? _frame_count / (uset / 1000) : Infinity;
        _frame_count = 0;
        _frame_lastreftime = performance.now();
        
        if (framerate != Infinity) {
            _framerate_ckeck_limit = framerate * 0.25;
        }
    }
    
    requestAnimationFrame(_frame_counter);
}

requestAnimationFrame(_frame_counter);

})();
'''

def _parseRangeHeader(data: bytes, rg: typing.Optional[str], setrep_header: typing.Callable[[str, str], typing.Any]):
    if rg is None: return data
    start, end = rg.split("=")[1].split("-")
    start = int(start)
    end = int(end) if end else len(data) - 1
    start = min(max(start, 0), len(data) - 1)
    end = min(end, len(data) - 1)
    setrep_header("Content-Range", f"bytes {start}-{end}/{len(data)}")
    setrep_header("Content-Length", str(end - start + 1))
    return data[start:end+1]

class WebCanvas_FileServerHandler(http.server.BaseHTTPRequestHandler):
    _canvas: WebCanvas
    
    def do_GET(self):
        ctype = None
        if self.path[1:] in self._canvas._regims:
            im: Image.Image = self._canvas._regims[self.path[1:]]
            if hasattr(im, "byteData"):
                data = im.byteData
            else:
                temp_btyeio = io.BytesIO()
                im.save(temp_btyeio, "png")
                data = temp_btyeio.getvalue()
            ctype = "image/png"
                
        elif self.path[1:] in self._canvas._regres:
            data = self._canvas._regres[self.path[1:]]
            
            if self.path.endswith(".png"): ctype = "image/png"
            elif self.path.endswith(".js"): ctype = "application/javascript"
            elif self.path.endswith(".html"): ctype = "text/html"
            elif self.path.endswith(".css"): ctype = "text/css"
            elif self.path.endswith(".json"): ctype = "application/json"
            elif self.path.endswith(".ttf"): ctype = "font/ttf"
            elif self.path.endswith(".woff"): ctype = "font/woff"
            elif self.path.endswith(".woff2"): ctype = "font/woff2"
            elif self.path.endswith(".eot"): ctype = "font/eot"
            elif self.path.endswith(".svg"): ctype = "image/svg+xml"
            elif self.path.endswith(".ttc"): ctype = "font/ttc"
            elif self.path.endswith(".otf"): ctype = "font/otf"
            elif self.path.endswith(".xml"): ctype = "application/xml"
            elif self.path.endswith(".txt"): ctype = "text/plain"
            elif self.path.endswith(".ico"): ctype = "image/x-icon"
            elif self.path.endswith(".webp"): ctype = "image/webp"
            elif self.path.endswith(".mp4"): ctype = "video/mp4"
            elif self.path.endswith(".webm"): ctype = "video/webm"
            elif self.path.endswith(".ogg"): ctype = "video/ogg"
            elif self.path.endswith(".mp3"): ctype = "audio/mpeg"
            elif self.path.endswith(".wav"): ctype = "audio/wav"
            elif self.path.endswith(".flac"): ctype = "audio/flac"
            elif self.path.endswith(".aac"): ctype = "audio/aac"
            elif self.path.endswith(".avi"): ctype = "video/x-msvideo"
            elif self.path.endswith(".mov"): ctype = "video/quicktime"
            elif self.path.endswith(".mkv"): ctype = "video/x-matroska"
            else: ctype = "application/octet-stream"
        
        rangeHeader = self.headers.get("Range")
        code = 206 if rangeHeader else 200
        self.send_response(code)
        if not ctype:
            logging.error(f'Unknown file type:{self.path}')
        self.send_header("Content-type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        data = _parseRangeHeader(data, rangeHeader, self.send_header)
        self.end_headers()

        self.wfile.write(data)
    
    def log_request(self, *args, **kwargs) -> None: ...

class JsApi:
    def __init__(self) -> None:
        self.things: dict[str, typing.Any] = {}

    def get_thing(self, name: str):
        return self.things[name]
    
    def set_thing(self, name: str, value: typing.Any):
        self.things[name] = value
    
    def get_attr(self, name: str):
        return getattr(self, name)
    
    def set_attr(self, name: str, value: typing.Any):
        setattr(self, name, value)
    
    def call_attr(self, name: str, *args, **kwargs):
        return getattr(self, name)(*args, **kwargs)

class PILResourcePacker:
    def __init__(self, cv: WebCanvas):
        self.cv = cv
        self.imgs: list[tuple[str, Image.Image|bytes]] = []
        self._imgopted: dict[str, threading.Event] = {}
    
    def reg_img(self, img: Image.Image|bytes, name: str):
        logging.info(f'register image: {name}')
        self.imgs.append((name, img))
        
    def pack(self):
        logging.info('packing images...')
        datas = []
        dataindexs = []
        datacount = 0
        cache = {}
        for name, img in self.imgs:
            if isinstance(img, Image.Image):
                if hasattr(img, "byteData"):
                    data = img.byteData
                else:
                    if id(img) in cache:
                        data = cache[id(img)]
                    else:
                        btio = io.BytesIO()
                        img.save(btio, "png") # toooooooooooooo slow
                        data = btio.getvalue()
                        cache[id(img)] = data
            else:
                data = img
                
            datas.append(data)
            dataindexs.append([name, [datacount, len(data)]])
            datacount += len(data)
            logging.info(f'image {name} size: {len(data)}')
        
        logging.info('Packing Done')
        return b"".join(datas), dataindexs

    def load(self, data: bytes, indexs: list[list[str, list[int, int]]]):
        logging.info('webcv loading images...')
        rid = f"pilrespacker_{randint(0, 2 << 31)}"
        self.cv.reg_res(data, rid)
        
        logging.info('loading res package .')
        imnames = self.cv.wait_jspromise(f"loadrespackage('{self.cv.get_resource_path(rid)}', {indexs});")
        
        logging.info('get imgcomplete jseval')
        self.cv.wait_loadimgs(self.cv.get_imgcomplete_jseval(imnames))
        self.cv.unreg_res(rid)
        
        logging.info('revoke img urls')
        self.cv.run_js_code(f"""[{",".join(map(self.cv.get_img_jsvarname, imnames))}].forEach(im => URL.revokeObjectURL(im.src));""")
        
        def optimize():
            logging.info('cache image to optimize')
            codes = []
            codes.append(f"cachecv = document.createElement('canvas');")
            codes.append(f"cachecv.width = cachecv.height = 1;")
            codes.append(f"cachectx = cachecv.getContext('2d');")
            for im in imnames:
                codes.append(f"cachectx.drawImage({self.cv.get_img_jsvarname(im)}, 0, 0);")
            codes.append(f"delete cachecv; delete cachectx;")
            logging.info('run_js_code imnames')
            self.cv.run_js_code("".join(codes))
            
            for im in imnames:
                self._imgopted[im].set()
        
        logging.info('start _imgopted update')
        self._imgopted.update({im: threading.Event() for im in imnames})
        threading.Thread(target=optimize, daemon=True).start()
    
    def getnames(self):
        return [name for name, _ in self.imgs]

    def unload(self, names: list[str]):
        for name in names:
            self._imgopted[name].wait()
            self._imgopted.pop(name)
            
        self.cv.run_js_code(f"""{";".join(map(lambda x: f"delete {self.cv.get_img_jsvarname(x)}", names))};""")

class WebCanvas:
    def __init__(
        self,
        width: int, height: int,
        x: int, y: int,
        debug: bool = False,
        title: str = "WebCanvas",
        resizable: bool = True,
        frameless: bool = False,
        html_path: str = "web_canvas.html",
        renderdemand: bool = False,
        renderasync: bool = False,
        hidden: bool = False,
        jslog: bool = False,
        jslog_path: str = "web_canvas.jslog.txt",
    ):
        self.jsapi = JsApi()
        self._destroyed = threading.Event()
        self._regims: dict[str, Image.Image] = {}
        self._regres: dict[str, bytes] = {}
        self._is_loadimg: dict[str, bool] = {}
        self._jscodes: list[str] = []
        self._framerate: int|float = -1
        self._jscode_orders: dict[int, list[tuple[str, bool]]] = {}
        
        self._rdevent = threading.Event()
        self._raevent = threading.Event()
        self.renderdemand = renderdemand
        self.renderasync = renderasync
        
        self.jslog = jslog
        self.jslog_path = jslog_path
        self.jslog_f = open(jslog_path, "w", encoding="utf-8") if self.jslog else None
        
        html_path = abspath(html_path)
        self.web = webview.create_window(
            title = title,
            url = html_path,
            resizable = resizable,
            js_api = self.jsapi,
            frameless = frameless,
            hidden = hidden
        )
        self.preloadarg = (width, height, x, y)
        self.evaljs = lambda x, *args, **kwargs: self.web.evaluate_js(x)
        self.start = lambda: webview.start(self.preload, self.web, debug=debug)
    
    def preload(self, window):
        self.web = window
        self._init(*self.preloadarg)
        self.maininit()
    
    def receive(self, func):
        self.maininit = func
    
    def _init(self, width: int, height: int, x: int, y: int):
        logging.info('Webview starting init in webcv')
        """
        if checksys.main == 'Android':
            while True:
                try:
                    self.web.native.webview
                except:
                    continue
                break
            logging.info('Android Webview inited')
        """
        
        self.web.events.closed += self._destroyed.set
        
        if checksys.main != 'Android':
            self.web.resize(width, height)
            self.web.move(x, y)
            self.web.resize(width, height)
            self.web.move(x, y)
            title = self.web.title
            temp_title = self.web.title + " " * randint(0, 4096)
            self.web.set_title(temp_title)
            
            self.web_hwnd = None
            if checksys.main == "Windows":
                while not self.web_hwnd:
                    self.web_hwnd = windll.user32.FindWindowW(None, temp_title)
                    time.sleep(0.01)
                logging.info('Webview start')
            self.web.set_title(title)
        
        """
        else:
            while True:
                try:
                    self.web._server.address
                except:
                    continue
                logging.info('Get web._server.address successful')
                break
        """
        self.web_port = int(self.web._server.address.split(":")[2].split("/")[0])
        WebCanvas_FileServerHandler._canvas = self
        self.file_server = http.server.HTTPServer(("0.0.0.0", self.web_port + 1), WebCanvas_FileServerHandler)
        logging.info('Starting file server')
        threading.Thread(target=self.file_server.serve_forever, daemon=True).start()
        self.jsapi.set_attr("_rdcallback", self._rdevent.set)
        self._raevent.set()
        
        graplib_webview.root = self
    
    def title(self, title: str) -> str: self.web.set_title(title)
    def winfo_screenwidth(self) -> int: return screen_width
    def winfo_screenheight(self) -> int: return screen_height
    def winfo_hwnd(self) -> int: return self.web_hwnd if checksys.main != 'Android' else None
    def winfo_legacywindowwidth(self) -> int: return self.run_js_code("window.innerWidth;")
    def winfo_legacywindowheight(self) -> int: return self.run_js_code("window.innerHeight;")

    def destroy(self): self.web.destroy()
    def resize(self, width: int, height: int): self.web.resize(width, height)
    def move(self, x: int, y:int): self.web.move(x, y)
    
    def run_js_code(self, code: str, add_code_array: bool = False, order: int|None = None, needresult: bool = True):
        logging.debug(f"run_js_code: {code}, repr of the code: {repr(code)}")
        if self.jslog and not code.endswith(";"): code += ";"
        
        if order is None:
            return self._jscodes.append(code) if add_code_array else self.evaljs(code, needresult)
        
        if order not in self._jscode_orders:
            self._jscode_orders[order] = []
        self._jscode_orders[order].append((code, add_code_array))
    
    def _rjwc(self, codes: list[str]):
        framerate: int|float = self.run_js_code(f"{codes}.forEach(r2eval);\nframerate;")
        
        if self.renderdemand:
            self._rdevent.wait()
            self._rdevent.clear()
        
        self._framerate = framerate
        
        if self.renderasync:
            self._raevent.set()
    
    def run_jscode_orders(self):
        if self._jscode_orders:
            for _, i in sorted(self._jscode_orders.items(), key=lambda x: x[0]):
                for c, w in i: 
                    if w: self._jscodes.append(c)
                    else: self.run_js_code(c)
            self._jscode_orders.clear()
        
    def run_js_wait_code(self):
        if self._jscode_orders: self.run_jscode_orders() # not to create a new pyframe
        self.run_js_code("requestAnimationFrame(() => pywebview.api.call_attr('_rdcallback'));", add_code_array=True)
        self.run_js_code("if (!('_frame_counter' in window)) {&FRAMERATE_CODE&};".replace("&FRAMERATE_CODE&", framerate_counter), add_code_array=True)
        
        codes = self._jscodes.copy()
        self._jscodes.clear()
        
        if self.jslog:
            self.jslog_f.write("\n// JSCODE - FRAME - START //\n")
            self.jslog_f.writelines(codes)
            self.jslog_f.write("\n// JSCODE - FRAME - END //\n")
        
        if not self.renderasync:
            return self._rjwc(codes)
        else:
            self._raevent.wait()
            self._raevent.clear()
            threading.Thread(target=self._rjwc, args=(codes, ), daemon=True).start()
    
    def string2cstring(self, code: str): return code.replace("\\", "\\\\").replace("'", "\\'").replace("\"", "\\\"").replace("`", "\\`").replace("\n", "\\n")
    def string2sctring_hqm(self, code: str): return f"'{self.string2cstring(code)}'"
    def get_framerate(self) -> int|float: return self._framerate
    
    def get_img_jsvarname(self, imname: str):
        return f"{imname}_img"
    
    def reg_img(self, im: Image.Image, name: str) -> None:
        self._regims[name] = im
        self._is_loadimg[name] = False
    
    def reg_res(self, res_data: bytes, name: str) -> None:
        self._regres[name] = res_data
    
    def unreg_res(self, name: str) -> None:
        self._regres.pop(name)
    
    def get_imgcomplete_jseval(self, ns: list[str]) -> str:
        return f"""[{",".join([f"{self.get_img_jsvarname(item)}.complete" for item in ns])}]"""
    
    def wait_loadimgs(self, complete_code: str) -> None:
        while not all(self.run_js_code(complete_code)):
            time.sleep(0.01)
        
    def load_allimg(self) -> None:
        for imgname in self._regims: self._load_img(imgname)
        self.wait_loadimgs(self.get_imgcomplete_jseval(self._regims))
    
    def reg_event(self, name: str, callback: typing.Callable) -> None:
        setattr(self.web.events, name, getattr(self.web.events, name) + callback)
    
    def wait_for_close(self) -> None:
        while not self._destroyed.wait(0.1):
            pass
        
        if self.jslog:
            self.jslog_f.write(f"\n\n// Webview closed.\n")
            self.jslog_f.flush()
            self.jslog_f.close()
    
    def get_resource_path(self, name: str) -> str:
        logging.info(f"Get resource path: {name}")
        return f"http://{host}:{self.web_port + 1}/{name}"

    def wait_jspromise(self, code: str, timeout=10) -> typing.Any:
        eid = f"wait_jspromise_{randint(0, 2 << 31)}"
        ete = threading.Event()
        ecbname = f"{eid}_callback"
        result = None
        error_info = None  # 存储错误详细信息

        def _callback(jsresult):
            nonlocal result, error_info
            if isinstance(jsresult, dict) and 'error' in jsresult:
                error_info = {
                    'message': jsresult.get('error', 'Unknown error'),
                    'stack': jsresult.get('stackTrace', 'No stack trace')
                }
            else:
                result = jsresult
            ete.set()

        self.jsapi.set_attr(ecbname, _callback)
        
        # 包裹代码在async函数中以捕获同步错误
        wrapped_code = f"""
        (async function() {{
            try {{
                const result = await (function() {{ 
                    try {{ 
                        return eval({self.string2sctring_hqm(code)}); 
                    }} catch (e) {{ 
                        return Promise.reject(e); 
                    }}
                }})();
                return result;
            }} catch (e) {{
                return {{ 
                    error: e.message,
                    stackTrace: e.stack 
                }};
            }}
        }})()
        """

        try:
            self.run_js_code(
                f"{wrapped_code}"
                f".then(res => pywebview.api.call_attr('{ecbname}', res))"
                f".catch(err => pywebview.api.call_attr('{ecbname}', {{ error: err }}));"
            )
            
            if not ete.wait(timeout):
                raise TimeoutError(f"JS操作超时（{timeout}秒）未响应")

        finally:
            if hasattr(self.jsapi, ecbname):
                delattr(self.jsapi, ecbname)

        if error_info:
            error_msg = f"JavaScript错误: {error_info['message']}\n调用栈:\n{error_info['stack']}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

        return result
    
    def _load_img(self, imgname: str) -> None:
        jsvarname = self.get_img_jsvarname(imgname)
        code = f"""\
        if (!window.{jsvarname}){chr(123)}\
            {jsvarname} = document.createElement('img');\
            {jsvarname}.crossOrigin = \"Anonymous\";\
            {jsvarname}.src = 'http://{host}:{self.web_port + 1}/{imgname}';\
            {jsvarname}.loading = \"eager\";\
        {chr(125)}\
        """
        self.run_js_code(code)
        self._is_loadimg[imgname] = True
