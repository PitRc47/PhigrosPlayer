import checksys
import zipfile
import json
import sys
import time
import logging
import typing

import load_extended as _

from graplib_webview import *

from threading import Thread
from os.path import exists, basename, abspath

if checksys.main == 'Windows':
    from ctypes import windll

if checksys.main == 'Android':
    from android.permissions import request_permissions, Permission # type: ignore
    from android import activity # type: ignore
    from jnius import autoclass # type: ignore
    def _androidPermissionwait(permissions, grant_results):
        pass
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], _androidPermissionwait)
    sys.argv = ['main.py', 'Re_NascencePsystyleVer.Rinth_live.0-IN.pez', "--fullscreen", '--usu169']

enable_clicksound = "--noclicksound" not in sys.argv
debug = "--debug" in sys.argv
debug_noshow_transparent_judgeline = "--debug-noshow-transparent-judgeline" in sys.argv
clickeffect_randomblock = "--noclickeffect-randomblock" not in sys.argv
loop = "--loop" in sys.argv
lfdaot = "--lfdaot" in sys.argv
lfdoat_file = "--lfdaot-file" in sys.argv
render_range_more = "--render-range-more" in sys.argv

render_range_more_scale = 2.0 if "--render-range-more-scale" not in sys.argv else eval(sys.argv[sys.argv.index("--render-range-more-scale") + 1])
noautoplay = "--noautoplay" in sys.argv
rtacc = "--rtacc" in sys.argv
lowquality = "--lowquality" in sys.argv
lowquality_scale = float(sys.argv[sys.argv.index("--lowquality-scale") + 1]) ** 0.5 if "--lowquality-scale" in sys.argv else 2.0 ** 0.5
showfps = "--showfps" in sys.argv
lfdaot_start_frame_num = int(eval(sys.argv[sys.argv.index("--lfdaot-start-frame-num") + 1])) if "--lfdaot-start-frame-num" in sys.argv else 0
lfdaot_run_frame_num = int(eval(sys.argv[sys.argv.index("--lfdaot-run-frame-num") + 1])) if "--lfdaot-run-frame-num" in sys.argv else float("inf")
speed = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.0
clickeffect_randomblock_roundn = eval(sys.argv[sys.argv.index("--clickeffect-randomblock-roundn") + 1]) if "--clickeffect-randomblock-roundn" in sys.argv else 0.0
noplaychart = "--noplaychart" in sys.argv
clicksound_volume = float(sys.argv[sys.argv.index("--clicksound-volume") + 1]) if "--clicksound-volume" in sys.argv else 1.0
musicsound_volume = float(sys.argv[sys.argv.index("--musicsound-volume") + 1]) if "--musicsound-volume" in sys.argv else 1.0
lowquality_imjscvscale_x = float(sys.argv[sys.argv.index("--lowquality-imjscvscale-x") + 1]) if "--lowquality-imjscvscale-x" in sys.argv else 1.0
lowquality_imjs_maxsize = float(sys.argv[sys.argv.index("--lowquality-imjs-maxsize") + 1]) if "--lowquality-imjs-maxsize" in sys.argv else 256
enable_controls = "--enable-controls" in sys.argv
wl_more_chinese = "--wl-more-chinese" in sys.argv
skip_time = float(sys.argv[sys.argv.index("--skip-time") + 1]) if "--skip-time" in sys.argv else 0.0
enable_jscanvas_bitmap = "--enable-jscanvas-bitmap" in sys.argv
respath = sys.argv[sys.argv.index("--res") + 1] if "--res" in sys.argv else "resources/resource_packs/default"
disengage_webview = "--disengage-webview" in sys.argv
usu169 = "--usu169" in sys.argv
render_video = "--render-video" in sys.argv
render_video_fps = float(sys.argv[sys.argv.index("--render-video-fps") + 1]) if "--render-video-fps" in sys.argv else 60.0
render_video_fourcc = sys.argv[sys.argv.index("--render-video-fourcc") + 1] if "--render-video-fourcc" in sys.argv else "mp4v"

if lfdaot and noautoplay:
    noautoplay = False
    logging.warning("if use --lfdaot, you cannot use --noautoplay")

if lfdaot and speed != 1.0:
    speed = 1.0
    logging.warning("if use --lfdaot, you cannot use --speed")

if lfdaot and skip_time != 0.0:
    skip_time = 0.0
    logging.warning("if use --lfdaot, you cannot use --skip-time")

if render_video and noautoplay:
    noautoplay = False
    logging.warning("if use --render-video, you cannot use --noautoplay")

if render_video and showfps:
    showfps = False
    logging.warning("if use --render-video, you cannot use --showfps")

combotips = ("AUTOPLAY" if not noautoplay else "COMBO") if "--combotips" not in sys.argv else sys.argv[sys.argv.index("--combotips") + 1]
def main():
    import webcv
    import dxsound
    import chartobj_phi
    import chartobj_rpe
    import chartfuncs_phi
    import chartfuncs_rpe
    import const
    import console_window
    import tool_funcs
    import dialog
    import info_loader
    import ppr_help
    import file_loader
    import phira_resource_pack
    import phicore
    import tempdir
    import socket_webviewbridge
    import needrelease
    from pydub import AudioSegment
    from dxsmixer import mixer
    
    import cv2
    import requests
    from PIL import Image, ImageFilter, ImageEnhance
    

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    mixer.init()

    if "--clickeffect-easing" in sys.argv:
        phicore.clickEffectEasingType = int(sys.argv[sys.argv.index("--clickeffect-easing") + 1])

    if checksys.main == 'Windows':
        from os import add_dll_directory
        add_dll_directory(abspath('../lib'))

    if len(sys.argv) == 1:
        print(ppr_help.HELP_ZH)
        raise SystemExit
    
    if "--clickeffect-easing" in sys.argv:
        phicore.clickEffectEasingType = int(sys.argv[sys.argv.index("--clickeffect-easing") + 1])

    console_window.Hide() if "--hideconsole" in sys.argv else None

    tempdir.clearTempDir()
    temp_dir = tempdir.createTempDir()

    mixer.init()

    if "--phira-chart" in sys.argv:
        logging.info("Downloading phira chart...")
        pctid = sys.argv[sys.argv.index("--phira-chart") + 1]
        apiresult = requests.get(f"https://phira.5wyxi.com/chart/{pctid}").json()
        if "error" in apiresult:
            logging.error(f"""phira api: {apiresult["error"]}""")
            raise SystemExit
        
        sys.argv.insert(1, f"{temp_dir}/phira-temp-chart.zip" if "--phira-chart-save" not in sys.argv else sys.argv[sys.argv.index("--phira-chart-save") + 1])
        with open(sys.argv[1], "wb") as f:
            with requests.get(apiresult["file"], stream=True) as reqs:
                for content in reqs.iter_content(chunk_size=1024):
                    f.write(content)
        logging.info("Downloaded phira chart.")

    logging.info("Unpack Chart...")

    with zipfile.ZipFile(sys.argv[1], 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    logging.info("Loading All Files of Chart...")
    files_dict = {
        "charts": [],
        "images": [],
        "audio": [],
    }
    cfrfp_procer: typing.Callable[[str], str] = lambda x: x.replace(f"{temp_dir}/", "")

    for item in tool_funcs.getAllFiles(temp_dir):
        if item.endswith("info.txt") or item.endswith("info.csv") or item.endswith("info.yml") or item.endswith("extra.json"):
            continue
        
        item_rawname = cfrfp_procer(item)
        loadres = file_loader.loadfile(item)
        
        match loadres.filetype:
            case file_loader.FILE_TYPE.CHART:
                files_dict["charts"].append([item, loadres.data])
                
            case file_loader.FILE_TYPE.IMAGE:
                files_dict["images"].append([item, loadres.data])
                
            case file_loader.FILE_TYPE.SONG:
                files_dict["audio"].append(item)
            
            case file_loader.FILE_TYPE.UNKNOW:
                logging.warning(f"Unknow resource type. path = {item_rawname}") # errors: ")
                # for e in loadres.errs: logging.warning(f"\t{repr(e)}")
                        
    if not files_dict["charts"]:
        logging.fatal("No Chart File Found")
        raise SystemExit

    if not files_dict["audio"]:
        logging.fatal("No Audio File Found")
        raise SystemExit

    if not files_dict["images"]:
        logging.warning("No Image File Found")
        files_dict["images"].append(["default", Image.new("RGB", (16, 9), "#0078d7")])

    chart_fp: str
    chart_json: dict
    cimg_fp: str
    chart_image: Image.Image
    audio_fp: str

    chart_index = file_loader.choosefile(
        fns = map(lambda x: x[0], files_dict["charts"]),
        prompt = "请选择谱面文件: ", rawprocer = cfrfp_procer
    )
    chart_fp, chart_json = files_dict["charts"][chart_index]

    if "formatVersion" in chart_json:
        CHART_TYPE = const.CHART_TYPE.PHI
    elif "META" in chart_json:
        CHART_TYPE = const.CHART_TYPE.RPE
    else:
        logging.fatal("This is what format chart ???")
        raise SystemExit

    if exists(f"{temp_dir}/extra.json"):
        try:
            logging.info("found extra.json, loading...")
            extra = chartfuncs_rpe.loadextra(json.load(open(f"{temp_dir}/extra.json", "r", encoding="utf-8")))
            logging.info("loading extra.json successfully")
        except SystemExit as e:
            logging.error("loading extra.json failed")
            
    if "extra" not in globals():
        extra = chartfuncs_rpe.loadextra({})
        
    def LoadChartObject(first: bool = False):
        global chart_obj
        
        if CHART_TYPE == const.CHART_TYPE.PHI:
            chart_obj = chartfuncs_phi.Load_Chart_Object(chart_json)
        elif CHART_TYPE == const.CHART_TYPE.RPE:
            chart_obj = chartfuncs_rpe.Load_Chart_Object(chart_json)
            
            chart_obj.META.RPEVersion = (
                sys.argv[sys.argv.index("--rpeversion") + 1]
                if "--rpeversion" in sys.argv
                else chart_obj.META.RPEVersion
            )
            chart_obj.extra = extra
        
        if not first:
            updateCoreConfig()
            
    LoadChartObject(True)

    cimg_index = file_loader.choosefile(
        fns = map(lambda x: x[0], files_dict["images"]),
        prompt = "请选择背景图片: ", rawprocer = cfrfp_procer,
        default = chart_obj.META.background if CHART_TYPE == const.CHART_TYPE.RPE else None
    )
    cimg_fp, chart_image = files_dict["images"][cimg_index]
    chart_image = chart_image.convert("RGB")

    audio_index = file_loader.choosefile(
        fns = files_dict["audio"],
        prompt = "请选择音频文件: ", rawprocer = cfrfp_procer,
        default = chart_obj.META.song if CHART_TYPE == const.CHART_TYPE.RPE else None
    )
    audio_fp = files_dict["audio"][audio_index]

    raw_audio_fp = audio_fp
    if speed != 1.0:
        logging.info(f"Processing audio, rate = {speed}")
        seg: AudioSegment = AudioSegment.from_file(audio_fp)
        seg = seg._spawn(seg.raw_data, overrides = {
            "frame_rate": int(seg.frame_rate * speed)
        }).set_frame_rate(seg.frame_rate)
        audio_fp = f"{temp_dir}/ppr_temp_audio_{time.time()}.wav"
        seg.export(audio_fp, format="wav")

    mixer.music.load(audio_fp)
    raw_audio_length = mixer.music.get_length()
    audio_length = raw_audio_length + (chart_obj.META.offset / 1000 if CHART_TYPE == const.CHART_TYPE.RPE else 0.0)
    logging.info("Loading Chart Information...")

    ChartInfoLoader = info_loader.InfoLoader([f"{temp_dir}/info.csv", f"{temp_dir}/info.txt", f"{temp_dir}/info.yml"])
    chart_information = ChartInfoLoader.get(basename(chart_fp), basename(raw_audio_fp), basename(cimg_fp))

    if CHART_TYPE == const.CHART_TYPE.RPE and chart_information is ChartInfoLoader.default_info:
        chart_information["Name"] = chart_obj.META.name
        chart_information["Artist"] = chart_obj.META.composer
        chart_information["Level"] = chart_obj.META.level
        chart_information["Charter"] = chart_obj.META.charter

    logging.info("Loading Chart Information Successfully")
    logging.info("Informations: ")
    for k,v in chart_information.items():
        logging.info(f"              {k}: {v}")

    def Load_Resource():
        global globalNoteWidth
        global note_max_width, note_max_height
        global note_max_size_half
        global animation_image
        global WaitLoading, LoadSuccess
        global chart_res
        global ClickEffectFrameCount
        global cksmanager
        
        logging.info("Loading Resource...")
        LoadSuccess = mixer.Sound(abspath("resources/LoadSuccess.wav"))
        WaitLoading = mixer.Sound(abspath("resources/WaitLoading.wav"))
        Thread(target=WaitLoading_FadeIn, daemon = True).start()
        LoadSuccess.set_volume(0.75)
        WaitLoading.play(-1)
        noteWidth_raw = (0.125 * w + 0.2 * h) / 2
        globalNoteWidth = (noteWidth_raw) * (eval(sys.argv[sys.argv.index("--scale-note") + 1]) if "--scale-note" in sys.argv else 1.0)
        
        phi_rpack = phira_resource_pack.PhiraResourcePack(respath)
        phi_rpack.setToGlobal()
        ClickEffectFrameCount = phi_rpack.effectFrameCount
        
        Resource = {
            "levels":{
                "AP": Image.open("resources/Levels/AP.png"),
                "FC": Image.open("resources/Levels/FC.png"),
                "V": Image.open("resources/Levels/V.png"),
                "S": Image.open("resources/Levels/S.png"),
                "A": Image.open("resources/Levels/A.png"),
                "B": Image.open("resources/Levels/B.png"),
                "C": Image.open("resources/Levels/C.png"),
                "F": Image.open("resources/Levels/F.png")
            },
            "le_warn": Image.open("resources/le_warn.png"),
            "Retry": Image.open("resources/Retry.png"),
            "Arrow_Right": Image.open("resources/Arrow_Right.png"),
            "Over": mixer.Sound(abspath("resources/Over.wav")),
            "Pause": mixer.Sound(abspath("resources/Pause.wav")),
            "PauseImg": Image.open("resources/Pause.png"),
            "ButtonLeftBlack": Image.open("resources/Button_Left_Black.png"),
            "ButtonRightBlack": None
        }
        Resource.update(phi_rpack.createResourceDict())
        
        respacker = webcv.PILResourcePacker(root)
        background_image_blur = chart_image.resize((w, h)).filter(ImageFilter.GaussianBlur((w + h) / 50))
        background_image = ImageEnhance.Brightness(background_image_blur).enhance(1.0 - chart_information["BackgroundDim"])
        respacker.reg_img(background_image, "background")
        
        finish_animation_image_mask = Image.new("RGBA", (1, 5), (0, 0, 0, 0))
        finish_animation_image_mask.putpixel((0, 4), (0, 0, 0, 204))
        finish_animation_image_mask.putpixel((0, 3), (0, 0, 0, 128))
        finish_animation_image_mask.putpixel((0, 2), (0, 0, 0, 64))
        
        animation_image = chart_image.copy().convert("RGBA")
        tool_funcs.cutAnimationIllImage(animation_image)
        
        finish_animation_image = chart_image.copy().convert("RGBA")
        finish_animation_image_mask = finish_animation_image_mask.resize(finish_animation_image.size)
        finish_animation_image.paste(finish_animation_image_mask, (0, 0), finish_animation_image_mask)
        
        Resource["ButtonRightBlack"] = Resource["ButtonLeftBlack"].transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        const.set_NOTE_DUB_FIXSCALE(Resource["Notes"]["Hold_Body_dub"].width / Resource["Notes"]["Hold_Body"].width)
        
        for k, v in Resource["Notes"].items():
            respacker.reg_img(Resource["Notes"][k], f"Note_{k}")
        
        for i in range(ClickEffectFrameCount): # reg click effect
            respacker.reg_img(Resource["Note_Click_Effect"]["Perfect"][i], f"Note_Click_Effect_Perfect_{i + 1}")
            respacker.reg_img(Resource["Note_Click_Effect"]["Good"][i], f"Note_Click_Effect_Good_{i + 1}")
            
        for k,v in Resource["levels"].items(): # reg levels img
            respacker.reg_img(v, f"Level_{k}")
        
        respacker.reg_img(Resource["le_warn"], "le_warn")
        respacker.reg_img(chart_image, "begin_animation_image")
        respacker.reg_img(finish_animation_image, "finish_animation_image")
        respacker.reg_img(Resource["Retry"], "Retry")
        respacker.reg_img(Resource["Arrow_Right"], "Arrow_Right")
        respacker.reg_img(Resource["PauseImg"], "PauseImg")
        respacker.reg_img(Resource["ButtonLeftBlack"], "ButtonLeftBlack")
        respacker.reg_img(Resource["ButtonRightBlack"], "ButtonRightBlack")
        
        chart_res = {}
        
        if CHART_TYPE == const.CHART_TYPE.RPE:
            imfns: list[str] = list(map(lambda x: x[0], files_dict["images"]))
            imobjs: list[Image.Image] = list(map(lambda x: x[1], files_dict["images"]))
            
            for line in chart_obj.judgeLineList:
                if line.Texture == "line.png": continue
                if not line.isGif:
                    paths = [
                        f"{temp_dir}/{line.Texture}",
                        f"{temp_dir}/{line.Texture}.png",
                        f"{temp_dir}/{line.Texture}.jpg",
                        f"{temp_dir}/{line.Texture}.jpeg"
                    ]
                    
                    for p in paths:
                        if tool_funcs.fileinlist(p, imfns):
                            texture_index = tool_funcs.findfileinlist(p, imfns)
                            texture: Image.Image = imobjs[texture_index]
                            chart_res[line.Texture] = (texture.convert("RGBA"), texture.size)
                            logging.info(f"Loaded line texture {line.Texture}")
                            break
                    else:
                        logging.warning(f"Cannot find texture {line.Texture}")
                        texture = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
                        chart_res[line.Texture] = (texture, texture.size)
                        
                    respacker.reg_img(chart_res[line.Texture][0], f"lineTexture_{chart_obj.judgeLineList.index(line)}")
                else:
                    mp4data, size = tool_funcs.gif2mp4(f"{temp_dir}/{line.Texture}")
                    chart_res[line.Texture] = (None, size)
                    name = f"lineTexture_{chart_obj.judgeLineList.index(line)}"
                    root.reg_res(mp4data, f"{name}.mp4")
                    root.wait_jspromise(f"""loadvideo(URL.createObjectURL(new Blob([new Uint8Array({list(mp4data)})], {{type: 'application/octet-stream'}})), '{name}_img');""")
        
        respacker.load(*respacker.pack())

        with open("resources/font.ttf", "rb") as f:
            font = f.read()
            root.wait_jspromise(f"""loadFont('PhigrosFont',URL.createObjectURL(new Blob([new Uint8Array({list(font)})], {{type: 'application/octet-stream'}})));""")

        # root.file_server.shutdown()
        note_max_width = globalNoteWidth * const.NOTE_DUB_FIXSCALE
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
            "chromatic": open("shaders/chromatic.glsl", "r", encoding="utf-8").read(),
            "circleBlur": open("shaders/circle_blur.glsl", "r", encoding="utf-8").read(),
            "fisheye": open("shaders/fisheye.glsl", "r", encoding="utf-8").read(),
            "glitch": open("shaders/glitch.glsl", "r", encoding="utf-8").read(),
            "grayscale": open("shaders/grayscale.glsl", "r", encoding="utf-8").read(),
            "noise": open("shaders/noise.glsl", "r", encoding="utf-8").read(),
            "pixel": open("shaders/pixel.glsl", "r", encoding="utf-8").read(),
            "radialBlur": open("shaders/radial_blur.glsl", "r", encoding="utf-8").read(),
            "shockwave": open("shaders/shockwave.glsl", "r", encoding="utf-8").read(),
            "vignette": open("shaders/vignette.glsl", "r", encoding="utf-8").read()
        }
        
        if CHART_TYPE == const.CHART_TYPE.RPE:
            for line in chart_obj.judgeLineList:
                for note in line.notes:
                    if note.hitsound_reskey not in Resource["Note_Click_Audio"]:
                        try:
                            Resource["Note_Click_Audio"][note.hitsound_reskey] = dxsound.directSound(f"{temp_dir}/{note.hitsound}")
                            logging.info(f"Loaded note hitsound {note.hitsound}")
                        except Exception as e:
                            logging.warning(f"Cannot load note hitsound {note.hitsound} for note due to {e}")
            
            if chart_obj.extra is not None:
                for effect in chart_obj.extra.effects:
                    if effect.shader not in shaders.keys():
                        try:
                            shaders[effect.shader] = tool_funcs.fixShader(open(f"{temp_dir}/{effect.shader}", "r", encoding="utf-8").read())
                            const.EXTRA_DEFAULTS[effect.shader] = tool_funcs.getShaderDefault(shaders[effect.shader])
                        except Exception as e:
                            logging.warning(f"Cannot load shader {effect.shader} due to {e}")
                
                shadernames = list(set(effect.shader for effect in chart_obj.extra.effects))

                for name, glsl in shaders.items():
                    if name not in shadernames: continue
                    root.run_js_code(f"mainShaderLoader.load({repr(name)}, {repr(glsl)});")
                    if (glerr := root.run_js_code("GLERR;")) is not None:
                        logging.warning(f"Cannot compile shader {name} due to {glerr}")
                    else:
                        logging.info(f"Loaded shader {name}")
        
        cksmanager = phicore.ClickSoundManager(Resource["Note_Click_Audio"])
        logging.info("Load Resource Successfully")
        return Resource

    def WaitLoading_FadeIn():
        for i in range(100):
            WaitLoading.set_volume((i + 1) / 100)
            time.sleep(2 / 100)

    def Show_Start():
        WaitLoading.fadeout(450)
        
        def dle_warn(a: float):
            drawAlphaImage("le_warn", 0, 0, w, h, a, wait_execute=True)
        
        logging.info('enter show start')
        
        animationst = time.time()
        while time.time() - animationst < 1.0:
            clearCanvas(wait_execute=True)
            p = (time.time() - animationst) / 1.0
            dle_warn(1.0 - (1.0 - tool_funcs.fixorp(p)) ** 4)
            root.run_js_wait_code()
        
        logging.info('show start stage 2')
        time.sleep(0.35)
        
        animationst = time.time()
        while time.time() - animationst < 1.0:
            clearCanvas(wait_execute=True)
            phicore.drawBg()
            phicore.draw_ui(animationing=True)
            p = (time.time() - animationst) / 1.0
            dle_warn((tool_funcs.fixorp(p) - 1.0) ** 4)
            root.run_js_wait_code()
        
        logging.info('show start stage 3')
        time.sleep(0.25)
        clearCanvas(wait_execute=True)
        phicore.drawBg()
        phicore.draw_ui(animationing=True)
        logging.info('show start stage 4')
        root.run_js_wait_code()
        Thread(target=PlayerStart, daemon=True).start()

    def checkOffset(now_t: float):
        global show_start_time
        
        dt = tool_funcs.checkOffset(now_t, raw_audio_length, mixer)
        if dt != 0.0:
            show_start_time += dt
            updateCoreConfig()

    def getLfdaotFuncs():
        _getfuncs = lambda obj: {fn: getattr(obj, fn) for fn in dir(obj) if not fn.startswith("_")}
        maps = [
            _getfuncs(root),
            _getfuncs(phicore)
        ]
        result = {k: v for i in maps for k, v in i.items()}
        
        if len(result) != sum(len(i) for i in maps):
            assert False, "Duplicate function name detected"
            
        return result

    def PlayerStart():
        global show_start_time, cksmanager

        logging.info('enter player start')
        
        Resource["Over"].stop()
        
        phicore.loadingAnimation()
        phicore.lineOpenAnimation()
        show_start_time = time.time() - skip_time
        PhiCoreConfigObject.show_start_time = show_start_time

        logging.info("updateCoreConfig")
        updateCoreConfig()
        now_t = 0
        
        if not (lfdaot or render_video):
            mixer.music.play()
            mixer.music.set_pos(skip_time)
            while not mixer.music.get_busy(): pass
            if noautoplay:
                if CHART_TYPE == const.CHART_TYPE.PHI:
                    pplm_proxy = chartobj_phi.PPLMPHI_Proxy(chart_obj)
                elif CHART_TYPE == const.CHART_TYPE.RPE:
                    pplm_proxy = chartobj_rpe.PPLMRPE_Proxy(chart_obj)
                
                pppsm = tool_funcs.PhigrosPlayManager(chart_obj.note_num)
                pplm = tool_funcs.PhigrosPlayLogicManager(
                    pplm_proxy, pppsm,
                    enable_clicksound, lambda nt: Resource["Note_Click_Audio"][nt].play()
                )
                
                convertTime2Chart = lambda t: (t - show_start_time) * speed - (0.0 if CHART_TYPE == const.CHART_TYPE.PHI else chart_obj.META.offset / 1000)
                root.jsapi.set_attr("PhigrosPlay_KeyDown", lambda t, key: pplm.pc_click(convertTime2Chart(t) if not disengage_webview else now_t, key))
                root.jsapi.set_attr("PhigrosPlay_KeyUp", lambda t, key: pplm.pc_release(convertTime2Chart(t) if not disengage_webview else now_t, key))
                root.run_js_code("_PhigrosPlay_KeyDown = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyDown', new Date().getTime() / 1000, e.key)}, false);")
                root.run_js_code("_PhigrosPlay_KeyUp = PhigrosPlay_KeyEvent((e) => {pywebview.api.call_attr('PhigrosPlay_KeyUp', new Date().getTime() / 1000, e.key)}, false);")
                root.run_js_code("window.addEventListener('keydown', _PhigrosPlay_KeyDown);")
                root.run_js_code("window.addEventListener('keyup', _PhigrosPlay_KeyUp);")
                
            play_restart_flag = False
            pause_flag = False
            pause_st = float("nan")
            
            def _f(): nonlocal play_restart_flag; play_restart_flag = True
            
            @tool_funcs.NoJoinThreadFunc
            def space():
                global show_start_time
                nonlocal pause_flag, pause_st
                
                if not pause_flag:
                    pause_flag = True
                    mixer.music.pause()
                    Resource["Pause"].play()
                    pause_st = time.time()
                else:
                    mixer.music.unpause()
                    show_start_time += time.time() - pause_st
                    pause_flag = False
                    
            root.jsapi.set_attr("Noautoplay_Restart", _f)
            root.jsapi.set_attr("SpaceClicked", space)
            root.run_js_code("_Noautoplay_Restart = (e) => {if (e.altKey && e.ctrlKey && e.repeat && e.key.toLowerCase() == 'r') pywebview.api.call_attr('Noautoplay_Restart');};") # && e.repeat 为了判定长按
            root.run_js_code("_SpaceClicked = (e) => {if (e.key == ' ' && !e.repeat) pywebview.api.call_attr('SpaceClicked');};")
            root.run_js_code("window.addEventListener('keydown', _Noautoplay_Restart);")
            root.run_js_code("window.addEventListener('keydown', _SpaceClicked);")
            
            while True:
                while pause_flag: time.sleep(1 / 30)
                
                now_t = time.time() - show_start_time
                checkOffset(now_t - skip_time)
                if CHART_TYPE == const.CHART_TYPE.PHI:
                    Task = phicore.GetFrameRenderTask_Phi(now_t, pplm = pplm if noautoplay else None)
                elif CHART_TYPE == const.CHART_TYPE.RPE:
                    Task = phicore.GetFrameRenderTask_Rpe(now_t, pplm = pplm if noautoplay else None)
                    
                Task.ExecTask()
                
                break_flag = phicore.processExTask(Task.ExTask)
                
                if break_flag:
                    break
                
                if play_restart_flag:
                    break
            
            if noautoplay:
                root.run_js_code("window.removeEventListener('keydown', _PhigrosPlay_KeyDown);")
                root.run_js_code("window.removeEventListener('keyup', _PhigrosPlay_KeyUp);")
            
            root.run_js_code("window.removeEventListener('keydown', _Noautoplay_Restart);")
            root.run_js_code("window.removeEventListener('keydown', _SpaceClicked);")
            
            if play_restart_flag:
                mixer.music.fadeout(250)
                LoadChartObject()
                Thread(target=PlayerStart, daemon=True).start()
                return
        elif lfdaot:
            lfdaot_tasks: dict[int, chartobj_phi.FrameRenderTask] = {}
            frame_speed = 60
            if "--lfdaot-frame-speed" in sys.argv:
                frame_speed = eval(sys.argv[sys.argv.index("--lfdaot-frame-speed") + 1])
            frame_count = lfdaot_start_frame_num
            frame_time = 1 / frame_speed
            allframe_num = int(audio_length / frame_time) + 1
            
            if lfdaot and not lfdoat_file: # eq if not lfdoat_file
                while True:
                    if frame_count * frame_time > audio_length or frame_count - lfdaot_start_frame_num >= lfdaot_run_frame_num:
                        break
                    
                    now_t = frame_count * frame_time
                    
                    if CHART_TYPE == const.CHART_TYPE.PHI:
                        lfdaot_tasks.update({frame_count: phicore.GetFrameRenderTask_Phi(now_t, None)})
                    elif CHART_TYPE == const.CHART_TYPE.RPE:
                        lfdaot_tasks.update({frame_count: phicore.GetFrameRenderTask_Rpe(now_t, None)})
                    
                    frame_count += 1
                    
                    print(f"\rLoadFrameData: {frame_count} / {allframe_num}", end="")
                
                if "--lfdaot-file-savefp" in sys.argv:
                    lfdaot_fp = sys.argv[sys.argv.index("--lfdaot-file-savefp") + 1]
                    savelfdaot = True
                else:
                    lfdaot_fp = dialog.savefile(fn="Chart.lfdaot")
                    savelfdaot = lfdaot_fp != "Chart.lfdaot"
                
                if savelfdaot:
                    recorder = chartobj_phi.FrameTaskRecorder(
                        meta = chartobj_phi.FrameTaskRecorder_Meta(
                            frame_speed = frame_speed,
                            frame_num = len(lfdaot_tasks),
                            size = (w, h)
                        ),
                        data = lfdaot_tasks.values()
                    )
                    
                    with open(lfdaot_fp, "w", encoding="utf-8") as f:
                        recorder.stringify(f)
                        
                if "--lfdaot-file-output-autoexit" in sys.argv:
                    root.destroy()
                    return
                
            else: #--lfdaot-file
                fp = sys.argv[sys.argv.index("--lfdaot-file") + 1]
                with open(fp,"r",encoding="utf-8") as f:
                    data = json.load(f)
                frame_speed = data["meta"]["frame_speed"]
                frame_time = 1 / frame_speed
                allframe_num = data["meta"]["frame_num"]
                
                funcmap = getLfdaotFuncs()
                
                for index,Task_data in enumerate(data["data"]):
                    lfdaot_tasks.update({
                        index: chartobj_phi.FrameRenderTask(
                            RenderTasks = [
                                chartobj_phi.RenderTask(
                                    func = funcmap[render_task_data["func_name"]],
                                    args = tuple(render_task_data["args"]),
                                    kwargs = render_task_data["kwargs"]
                                )
                                for render_task_data in Task_data["render"]
                            ],
                            ExTask = tuple(Task_data["ex"])
                        )
                    })
                if data["meta"]["size"] != [w, h]:
                    logging.warning("The size of the lfdaot file is not the same as the size of the window")
            
            mixer.music.play()
            while not mixer.music.get_busy(): pass
            
            totm: tool_funcs.TimeoutTaskManager[chartobj_phi.FrameRenderTask] = tool_funcs.TimeoutTaskManager()
            totm.valid = lambda x: bool(x)
            
            for fc, task in lfdaot_tasks.items():
                totm.add_task(fc, task.ExTask)
            
            pst = time.time()
            
            while True:
                now_t = time.time() - pst
                music_play_fcount = int(now_t / frame_time)
                
                try:
                    Task: chartobj_phi.FrameRenderTask = lfdaot_tasks[music_play_fcount]
                except KeyError:
                    continue
                
                Task.ExecTask(clear=False)
                extasks = totm.get_task(music_play_fcount)
                
                break_flag_oside = False
                
                for extask in extasks:
                    break_flag = phicore.processExTask(extask)
                    
                    if break_flag:
                        break_flag_oside = True
                        break
                
                if break_flag_oside:
                    break
                
                pst += tool_funcs.checkOffset(now_t, raw_audio_length, mixer)
        elif render_video:
            video_fp = sys.argv[sys.argv.index("--render-video-savefp") + 1] if "--render-video-savefp" in sys.argv else dialog.savefile(
                fn = "render_video.mp4"
            )
            
            if "--render-video-savefp" not in sys.argv and video_fp == "render_video.mp4":
                root.destroy()
                return
            
        else: #--lfdaot-file
            fp = sys.argv[sys.argv.index("--lfdaot-file") + 1]
            with open(fp,"r",encoding="utf-8") as f:
                data = json.load(f)
            frame_speed = data["meta"]["frame_speed"]
            frame_time = 1 / frame_speed
            allframe_num = data["meta"]["frame_num"]
            
            funcmap = getLfdaotFuncs()
            
            for index,Task_data in enumerate(data["data"]):
                lfdaot_tasks.update({
                    index: chartobj_phi.FrameRenderTask(
                        RenderTasks = [
                            chartobj_phi.RenderTask(
                                func = funcmap[render_task_data["func_name"]],
                                args = tuple(render_task_data["args"]),
                                kwargs = render_task_data["kwargs"]
                            )
                            for render_task_data in Task_data["render"]
                        ],
                        ExTask = tuple(Task_data["ex"])
                    )
                })
            if data["meta"]["size"] != [w, h]:
                logging.warning("The size of the lfdaot file is not the same as the size of the window")
        
        mixer.music.play()
        while not mixer.music.get_busy(): pass
        
        totm: tool_funcs.TimeoutTaskManager[chartobj_phi.FrameRenderTask] = tool_funcs.TimeoutTaskManager()
        totm.valid = lambda x: bool(x)
        
        for fc, task in lfdaot_tasks.items():
            totm.add_task(fc, task.ExTask)
        
        pst = time.time()
        
        while True:
            now_t = time.time() - pst
            music_play_fcount = int(now_t / frame_time)
            
            try:
                Task: chartobj_phi.FrameRenderTask = lfdaot_tasks[music_play_fcount]
            except KeyError:
                continue
            
            Task.ExecTask(clear=False)
            extasks = totm.get_task(music_play_fcount)
            
            break_flag_oside = False
            
            for extask in extasks:
                break_flag = phicore.processExTask(extask)
                
                if break_flag:
                    break_flag_oside = True
                    break
            
            if break_flag_oside:
                break
            
            pst += tool_funcs.checkOffset(now_t, raw_audio_length, mixer)
    
    
    def updateCoreConfig():
        global PhiCoreConfigObject
        
        PhiCoreConfigObject = phicore.PhiCoreConfig(
            SETTER = lambda vn, vv: globals().update({vn: vv}),
            root = root, w = w, h = h,
            chart_information = chart_information,
            chart_obj = chart_obj, CHART_TYPE = CHART_TYPE,
            Resource = Resource,
            ClickEffectFrameCount = ClickEffectFrameCount,
            globalNoteWidth = globalNoteWidth,
            note_max_size_half = note_max_size_half, audio_length = audio_length,
            raw_audio_length = raw_audio_length, show_start_time = float("nan"),
            chart_image = chart_image,
            clickeffect_randomblock = clickeffect_randomblock,
            clickeffect_randomblock_roundn = clickeffect_randomblock_roundn,
            LoadSuccess = LoadSuccess, chart_res = chart_res,
            cksmanager = cksmanager,
            enable_clicksound = enable_clicksound, rtacc = rtacc,
            noautoplay = noautoplay, showfps = showfps, lfdaot = lfdaot,
            speed = speed, render_range_more = render_range_more,
            render_range_more_scale = render_range_more_scale,
            debug = debug, combotips = combotips, noplaychart = noplaychart,
            clicksound_volume = clicksound_volume,
            musicsound_volume = musicsound_volume,
            enable_controls = enable_controls
        )
        phicore.CoreConfigure(PhiCoreConfigObject)

    def atexit_run():
        tempdir.clearTempDir()
        needrelease.run()
        sys.exit(0)

    def init():
        global disengage_webview
        global webdpr
        global lowquality, lowquality_scale
        global w, h
        global Resource
        global errFlag
        
        if checksys.main == 'Android':
            time.sleep(0.1)
        if disengage_webview:
            socket_webviewbridge.hook(root)

        webdpr = float(root.run_js_code("window.devicePixelRatio;"))
        if webdpr != 1.0:
            lowquality = True
            lowquality_scale *= 1.0 / webdpr # ...?

        if lowquality:
            root.run_js_code(f"lowquality_scale = {lowquality_scale};")

        if disengage_webview:
            w, h = root.run_js_code("window.innerWidth;"), root.run_js_code("window.innerHeight;")
        else:
            if "--window-host" in sys.argv and checksys.main == 'Windows':
                windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))
            if "--fullscreen" in sys.argv:
                w, h = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
                root.web.toggle_fullscreen()
            if disengage_webview:
                w, h = root.run_js_code("window.innerWidth;"), root.run_js_code("window.innerHeight;")
            else:
                if "--window-host" in sys.argv and checksys.main == 'Windows':
                    windll.user32.SetParent(root.winfo_hwnd(), eval(sys.argv[sys.argv.index("--window-host") + 1]))
                if "--fullscreen" in sys.argv:
                    w, h = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
                    root.web.toggle_fullscreen()
                else:
                    if checksys.main != 'Android':
                        if "--size" not in sys.argv:
                            w, h = int(root.winfo_screenwidth() * 0.6), int(root.winfo_screenheight() * 0.6)
                        else:
                            w, h = int(eval(sys.argv[sys.argv.index("--size") + 1])), int(eval(sys.argv[sys.argv.index("--size") + 2]))
                            
                        winw, winh = (
                            w if w <= root.winfo_screenwidth() else int(root.winfo_screenwidth() * 0.75),
                            h if h <= root.winfo_screenheight() else int(root.winfo_screenheight() * 0.75)
                        )
                        root.resize(winw, winh)
                        w_legacy, h_legacy = root.winfo_legacywindowwidth(), root.winfo_legacywindowheight()
                        logging.info(f'w_legacy {w_legacy}, h_legacy {h_legacy}')
                        logging.info(f'winw {winw},  winh {winh}')
                        winw = int(winw)
                        winh = int(winh)
                        w_legacy = int(w_legacy)
                        h_legacy = int(h_legacy)
                        dw_legacy, dh_legacy = winw - w_legacy, winh - h_legacy
                        dw_legacy *= webdpr; dh_legacy *= webdpr
                        dw_legacy, dh_legacy = int(dw_legacy), int(dh_legacy)
                        del w_legacy, h_legacy
                        root.resize(winw + dw_legacy, winh + dh_legacy)
                        root.move(int(root.winfo_screenwidth() / 2 - (winw + dw_legacy) / webdpr / 2), int(root.winfo_screenheight() / 2 - (winh + dh_legacy) / webdpr / 2))

            w *= webdpr; h *= webdpr; w = int(w); h = int(h)

            root.run_js_code(f"lowquality_imjscvscale_x = {lowquality_imjscvscale_x};")
            root.run_js_code(f"lowquality_imjs_maxsize = {lowquality_imjs_maxsize};")
            root.run_js_code(f"enable_jscanvas_bitmap = {enable_jscanvas_bitmap};")
            root.run_js_code(f"RPEVersion = {chart_obj.META.RPEVersion if CHART_TYPE == const.CHART_TYPE.RPE else -1};")
            root.run_js_code(f"resizeCanvas({w}, {h});")
            Resource = Load_Resource()

            if wl_more_chinese:
                root.run_js_code("setWlMoreChinese();")

            updateCoreConfig()

            Thread(target=Show_Start, daemon=True).start()
            root.wait_for_close()
            logging.info('main.py at exit 2')
            atexit_run()

    logging.info("Loading Window...")
    root = webcv.WebCanvas(
        width = 1, height = 1,
        x = 0, y = 0,
        title = "PhigrosPlayer - Simulator",
        debug = "--debug" in sys.argv,
        resizable = False,
        frameless = "--frameless" in sys.argv,
        renderdemand = "--renderdemand" in sys.argv,
        renderasync = "--renderasync" in sys.argv,
        jslog = "--enable-jslog" in sys.argv,
        jslog_path = sys.argv[sys.argv.index("--jslog-path")] if "--jslog-path" in sys.argv else "./ppr-jslog-nofmt.js"
    )
    Thread(target=root.init, args=(init, ), daemon=True).start()
    root.start()
    logging.info('main.py at exit')
    atexit_run()

if checksys.main != 'Android':
    try:
        logger = logging.getLogger('main.py')
        main()
    except SystemExit:
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except BaseException as e:
        import traceback
        logging.error(f'{traceback.format_exc()}')
else:
    try:
        logger = logging.getLogger('main.py')
        main()
    except Exception as e:
        import traceback
        logging.error(f'{traceback.format_exc()}')