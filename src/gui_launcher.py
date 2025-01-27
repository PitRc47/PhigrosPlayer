import fix_workpath as _

import ctypes
import tkinter
import tkinter.ttk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showerror
from os import popen
from os.path import exists, isfile, isdir
from sys import executable

if exists("./main.py") and isfile("./main.py"):
    target_path = f"\"PhigrosPlayer\" \"{executable}\" ./main.py"
elif exists("./main.exe") and isfile("./main.exe"):
    target_path = "./main.exe"
else:
    print("Can't find main.py or main.exe.")
    raise SystemExit

def hook_dropfiles_first(hwnd, callback):
    globals()[f"hook_dropfiles_dropfunc_prototype_{hwnd}"] = ctypes.WINFUNCTYPE(*(ctypes.c_uint64,) * 5)(lambda hwnd,msg,wp,lp: [callback([ctypes.windll.shell32.DragQueryFileW(ctypes.c_uint64(wp),0,szFile := ctypes.create_unicode_buffer(260),ctypes.sizeof(szFile)),szFile.value][1]) if msg == 0x233 else None,ctypes.windll.user32.CallWindowProcW(*map(ctypes.c_uint64,(lptr,hwnd,msg,wp,lp)))][1]);ctypes.windll.shell32.DragAcceptFiles(hwnd,True);lptr = ctypes.windll.user32.GetWindowLongPtrA(hwnd,-4);ctypes.windll.user32.SetWindowLongPtrA(hwnd,-4,globals()[f"hook_dropfiles_dropfunc_prototype_{hwnd}"])

def openfile_callback(widget: tkinter.Entry):
    fp = askopenfilename(parent=root, title="选择文件")
    if fp == "":
        return
    
    if not (exists(fp) and isfile(fp)):
        showerror(title="错误", message="选择的文件不存在或不为文件")
    
    widget.delete(0, "end")
    widget.insert(0, fp)

def opendir_callback(widget: tkinter.Entry):
    dp = askdirectory(parent=root, title="选择文件夹")
    if dp == "":
        return

    if not exists(dp):
        showerror(title="错误", message="选择的文件夹不存在")

    widget.delete(0, "end")
    widget.insert(0, dp)

def launch():
    launch_args = []
    chartfp = file_input_entry.get()
    
    if exists(chartfp):
        launch_args.append(chartfp)
    else:
        showerror(title="错误", message="谱面文件不存在或不为文件")
        return
    
    for var, arg in zip(arg_widgets, arg_setting):
        if var.get():
            launch_args.append(f"--{arg[1]}")

    for entry, kwarg in zip(kwarg_widgets, kwarg_setting):
        userinput = entry.get()
        if not userinput: continue
        match kwarg[3]:
            case "int":
                try: userinput = int(float(userinput))
                except ValueError:
                    showerror(title="错误", message=f"参数 {kwarg[1]} 的值应为整数")
                    return
            
            case "float":
                try: userinput = float(userinput)
                except ValueError:
                    showerror(title="错误", message=f"参数 {kwarg[1]} 的值应为浮点数")
                    return

            case "string":
                pass
            
            case "path":
                if not (exists(userinput) or isfile(userinput)):
                    showerror(title="错误", message=f"参数 {kwarg[1]} 的值应为存在的文件")
                    return
            
            case "path-dir":
                if not (exists(userinput) or isdir(userinput)):
                    showerror(title="错误", message=f"参数 {kwarg[1]} 的值应为存在的文件夹")
                    return
            
            case "choice":
                if userinput not in kwarg[4]:
                    showerror(title="错误", message=f"参数 {kwarg[1]} 的值应为以下之一: {kwarg[4]}")
                    return
                
        if userinput != kwarg[2]:
            launch_args.append(f"--{kwarg[1]}")
            launch_args.append(f"{userinput}")
    
    command = "start " + target_path + " " + " ".join(map(lambda x: f"\"{x}\"", launch_args))
    print(command)
    popen(command)
    
root = tkinter.Tk()
root.withdraw()
root.title("Phigros Player Launcher")
root.iconbitmap("icon.ico")
root.resizable(False, False)
screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
file_input_label = tkinter.Label(root, text="谱面文件: ")
file_input_label.grid(row=0, column=0, columnspan=100, padx=12, sticky="w")
file_input_entry = tkinter.ttk.Entry(root, width=int(screen_width / 35))
file_input_entry.grid(row=0, column=101, columnspan=100, sticky="w")
file_input_filedialog_button = tkinter.ttk.Button(root, text="选择", command=lambda: openfile_callback(file_input_entry))
file_input_filedialog_button.grid(row=0, column=202, sticky="w")

arg_setting = [
    ("隐藏控制台窗口", "hideconsole"),
    ("调试", "debug"),
    ("全屏", "fullscreen"),
    ("自动循环", "loop"),
    ("生成lfdaot文件", "lfdaot"),
    ("禁用点击音效", "noclicksound"),
    ("扩展渲染范围", "render-range-more"),
    ("使用lfdaot文件渲染视频", "lfdaot-render-video"),
    ("窗口无边框", "frameless"),
    ("禁用自动游玩", "noautoplay"),
    ("启用实时准度", "rtacc"),
    ("生成lfdaot文件后自动退出", "lfdaot-file-output-autoexit"),
    ("低画质模式", "lowquality"),
    ("显示帧率", "showfps"),
    ("不播放谱面, 立即结算", "noplaychart"),
    ("启用rpe谱面control类字段", "rpe-control", "有极大的性能开销"),
    ("替换文本为中文 (wl)", "wl-more-chinese"),
    ("使用 raf 限制帧率", "renderdemand"),
    ("异步渲染", "renderasync"),
    ("保留渲染的 JavaScript 代码", "enable-jslog"),
    ("启用 BitmapImage", "enable-jscanvas-bitmap"),
    ("降级音频API", "soundapi-downgrade"),
    ("lfdaot渲染完成视频后自动退出", "lfdaot-render-video-autoexit"),
    ("不清理临时文件", "nocleartemp"),
    ("脱离 WebView", "disengage-webview")
]

kwarg_setting = [
    ("连击提示文本", "combotips", "AUTOPLAY", "string"),
    ("打击特效随机块数量", "random-block-num", 4, "int"),
    ("设置音符缩放", "scale-note", 1.0, "float"),
    ("设置 lfdaot 文件路径", "lfdaot-file", None, "path"),
    ("设置窗口大小 (如: \"1920 1080\")", "size", None, "string"),
    ("设置生成 lfdaot 文件的帧速度", "lfdaot-frame-speed", 60, "int"),
    ("设置渲染范围更多的缩放", "render-range-more-scale", 2.0, "float"),
    ("设置窗口宿主 (hwnd)", "window-host", None, "int"),
    ("生成lfdaot文件的变成路径", "lfdaot-file-savefp", None, "path"),
    ("设置lfdaot渲染视频输出路径", "lfdaot-render-video-savefp", None, "path"),
    ("设置低画质渲染缩放", "lowquality-scale", 2.0, "float"),
    ("设置资源路径", "res", None, "path-dir"),
    ("设置生成 lfdaot 文件的开始帧数", "lfdaot-start-frame-num", 0, "int"),
    ("设置生成 lfdaot 文件的总帧数", "lfdaot-run-frame-num", None, "int"),
    ("设置谱面速度", "speed", 1.0, "float"),
    ("设置打击特效方块的圆角系数", "clickeffect-randomblock-roundn", 0.0, "float"),
    ("设置打击音效音量", "clicksound-volume", 1.0, "float"),
    ("设置音乐音量", "musicsound-volume", 1.0, "float"),
    ("设置低画质渲染缩放 (js调用层)", "lowquality-imjscvscale-x", 1.0, "float"),
    ("设置 lfdaot 文件生成的视频编码", "lfdaot-video-fourcc", "mp4v", "string"),
    ("使用 phira 谱面 (id)", "phira-chart", None, "int"),
    ("保存 phira 谱面路径", "phira-chart-save", None, "path"),
    ("播放时跳过的时间", "skip-time", 0.0, "float"),
    ("设置 渲染JavaScript 代码输出路径", "jslog-path", None, "path"),
    ("设置低画质渲染最大尺寸 (js调用层)", "lowquality-imjs-maxsize", 256, "int"),
    ("设置 rpe 谱面纹理缩放方法", "rpe-texture-scalemethod", "by-width", "choice", ["by-width", "by-height"]),
    ("扩展", "extended", None, "path")
]

arg_widgets = []
kwarg_widgets = []

arg_canvas = tkinter.Canvas(root)
arg_sbary = tkinter.ttk.Scrollbar(root, orient="vertical", command=arg_canvas.yview)
arg_sbarx = tkinter.ttk.Scrollbar(root, orient="horizontal", command=arg_canvas.xview)
arg_canvas.configure(yscrollcommand=arg_sbary.set)
arg_canvas.configure(xscrollcommand=arg_sbarx.set)

arg_frame = tkinter.Frame(arg_canvas)
arg_canvas.create_window((0, 0), window=arg_frame, anchor="nw")

for index, data in enumerate(arg_setting):
    var = tkinter.BooleanVar()
    var.set(False)
    checkbut = tkinter.ttk.Checkbutton(arg_frame, text=data[0], variable=var)
    checkbut.grid(row=index, column=0, sticky="w")
    arg_widgets.append(var)

arg_frame.update_idletasks()
arg_canvas.configure(scrollregion=arg_canvas.bbox("all"))

arg_canvas.grid(row=1, column=0, columnspan=3000, sticky="nw")
arg_sbary.grid(row=1, column=3001, sticky="ns")
arg_sbarx.grid(row=2, column=0, columnspan=1000, sticky="ew")
arg_canvas.bind("<MouseWheel>", lambda e: arg_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
arg_canvas.bind("<Shift-MouseWheel>", lambda e: arg_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))

kwarg_canvas = tkinter.Canvas(root, width=root.winfo_width())
kwarg_sbary = tkinter.ttk.Scrollbar(root, orient="vertical", command=kwarg_canvas.yview)
kwarg_sbarx = tkinter.ttk.Scrollbar(root, orient="horizontal", command=kwarg_canvas.xview)
kwarg_canvas.configure(yscrollcommand=kwarg_sbary.set)
kwarg_canvas.configure(xscrollcommand=kwarg_sbarx.set)

kwarg_frame = tkinter.Frame(kwarg_canvas)
kwarg_canvas.create_window((0, 0), window=kwarg_frame, anchor="nw")

for i, data in enumerate(kwarg_setting):
    label = tkinter.Label(kwarg_frame, text=f"{data[0]} ({data[3]}): ")
    label.grid(row=i, column=0, sticky="w")
    match data[3]:
        case "int" | "float" | "string":
            entry = tkinter.Entry(kwarg_frame)
            entry.grid(row=i, column=1, sticky="w")
            kwarg_widgets.append(entry)
            if data[2] is not None:
                entry.insert(0, str(data[2]))
        case "path":
            entry = tkinter.Entry(kwarg_frame)
            entry.grid(row=i, column=1, sticky="w")
            button = tkinter.ttk.Button(kwarg_frame, text="浏览", command=lambda entry=entry: openfile_callback(entry))
            button.grid(row=i, column=2, sticky="w")
            kwarg_widgets.append(entry)
        case "path-dir":
            entry = tkinter.Entry(kwarg_frame)
            entry.grid(row=i, column=1, sticky="w")
            button = tkinter.ttk.Button(kwarg_frame, text="浏览", command=lambda entry=entry: opendir_callback(entry))
            button.grid(row=i, column=2, sticky="w")
            kwarg_widgets.append(entry)
        case "choice":
            entry = tkinter.ttk.Combobox(kwarg_frame, values=data[4])
            entry.grid(row=i, column=1, sticky="w")
            kwarg_widgets.append(entry)
            entry.current(0)

kwarg_frame.update_idletasks()
kwarg_canvas.configure(scrollregion=kwarg_canvas.bbox("all"))

kwarg_canvas.grid(row=3, column=2, columnspan=3000, sticky="nw")
kwarg_sbary.grid(row=3, column=3001, sticky="ns")
kwarg_sbarx.grid(row=4, column=2, columnspan=1000, sticky="ew")
kwarg_canvas.bind("<MouseWheel>", lambda e: kwarg_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
kwarg_canvas.bind("<Shift-MouseWheel>", lambda e: kwarg_canvas.xview_scroll(int(-1*(e.delta/120)), "units"))

launchButton = tkinter.ttk.Button(root, text="启动", command=launch)
launchButton.grid(row=5, column=0, columnspan=5000, padx=12, pady=5, sticky="w")

root.deiconify()
root.update()
arg_frame["width"] = root.winfo_width()
kwarg_frame["width"] = root.winfo_width()
arg_canvas["width"] = root.winfo_width()
kwarg_canvas["width"] = root.winfo_width()
hook_dropfiles_first(root.winfo_id(), lambda file:([file_input_entry.delete(0, "end"),file_input_entry.insert(0, file)] if isfile(file) else None))
root.mainloop()