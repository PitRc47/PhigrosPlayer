import fix_workpath as _

import zipfile
import json
import struct
import base64

from os import mkdir, popen, listdir
from os.path import exists, isfile, basename
from shutil import rmtree
from threading import Thread
from time import sleep
from uuid import uuid4

import UnityPy
import UnityPy.files
import UnityPy.classes
from UnityPy.enums import ClassIDType
from fsb5 import FSB5
    
class ByteReaderA:
    def __init__(self, data: bytes):
        self.data = data
        self.position = 0
        self.d = {int: self.readInt, float: self.readFloat, str: self.readString}

    def readInt(self):
        self.position += 4
        return self.data[self.position - 4] ^ self.data[self.position - 3] << 8

    def readFloat(self):
        self.position += 4
        return struct.unpack("f", self.data[self.position - 4 : self.position])[0]

    def readString(self):
        length = self.readInt()
        result = self.data[self.position : self.position + length].decode()
        self.position += length // 4 * 4
        if length % 4 != 0:
            self.position += 4
        return result
    
    def readSchema(self, schema: dict):
        pbak = self.position
        try:
            result = []
            for _ in range(self.readInt()):
                item = {}
                for key, value in schema.items():
                    if value in (int, str, float):
                        item[key] = self.d[value]()
                    elif type(value) == list:
                        item[key] = [self.d[value[0]]() for _ in range(self.readInt())]
                    elif type(value) == tuple:
                        for t in value: self.d[t]()
                    elif type(value) == dict:
                        item[key] = self.readSchema(value)
                    else:
                        raise Exception("null")
                result.append(item)
            return result
        except Exception as e:
            self.position = pbak
            raise e

class ByteReaderB:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def readInt(self):
        self.position += 4
        return int.from_bytes(self.data[self.position - 4 : self.position], "little")

def getZipItem(path: str) -> str:
    while path[0] in ("/", "\\"): path = path[1:]
    with zipfile.ZipFile(pgrapk, 'r') as zip_ref:
        zip_ref.extract(path, './unpack-temp')
    return f"./unpack-temp/{path}"

def run(rpe: bool):
    try: rmtree("unpack-temp")
    except Exception: pass
    try: mkdir("unpack-temp")
    except FileExistsError: pass
    
    print("generate info.json...")
    infoResult = generate_info()
    print("generated info.json")
    
    print("unpack...")
    generate_resources()
    print("unpacked")
    
    print("pack charts...")
    pack_charts(infoResult, rpe)
    print("packed charts")
    
    try: rmtree("unpack-temp")
    except Exception: pass

def generate_info():
    try: rmtree("unpack-result")
    except Exception: pass
    try: mkdir("unpack-result")
    except FileExistsError: pass
    
    env = UnityPy.Environment()
    env.load_file(
        open(getZipItem("/assets/bin/Data/globalgamemanagers.assets"), "rb").read(),
        name = "assets/bin/Data/globalgamemanagers.assets"
    )
    env.load_file(open(getZipItem("/assets/bin/Data/level0"), "rb").read())
            
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour": continue
        
        try:
            data = obj.read()
            match data.m_Script.get_obj().read().name:
                case "GameInformation":
                    information = data.raw_data.tobytes()
                case "GetCollectionControl":
                    collection = data.raw_data.tobytes()
                case "TipsProvider":
                    tips = data.raw_data.tobytes()
        except Exception as e:
            print(e)

    reader = ByteReaderA(information)
    reader.position = information.index(b"\x16\x00\x00\x00Glaciaxion.SunsetRay.0\x00\x00\n") - 4
    
    songBase_schema = {
        "songId": str,
        "songKey": str,
        "songName": str,
        "songTitle": str,
        "difficulty": [float],
        "illustrator": str,
        "charter": [str],
        "composer": str,
        "levels": [str],
        "previewTimeStart": float,
        "previewTimeEnd": float,
        "unlockList": {
            "unlockType": int,
            "unlockInfo": [str]
        },
        "levelMods": {
            "n": [str],
            "magic": int
        },
        "magic": int
    }
    
    chartItems = []
    
    while True:
        try:
            for item in reader.readSchema(songBase_schema):
                while 0.0 in item["difficulty"]:
                    i = item["difficulty"].index(0.0)
                    item["difficulty"].pop(i)
                    item["charter"].pop(i)
                    item["levels"].pop(i)

                item["soundIdBak"] = item["songId"]
                if item["songId"][-2:] == ".0": item["songId"] = item["songId"][:-2]
                item["difficulty"] = list(map(lambda x: round(x, 1), item["difficulty"]))
                del item["songTitle"]
                del item["unlockList"]
                del item["levelMods"]
                del item["magic"]
                
                chartItems.append(item)
        except struct.error:
            break
        except Exception as e:
            print(e)
    
    with open("./unpack-result/info.json", "w", encoding="utf-8") as f:
        json.dump(chartItems, f, ensure_ascii=False, indent=4)
    
    return chartItems

def generate_resources():
    with open(getZipItem("/assets/aa/catalog.json"), "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    for i in [
        "Chart_EZ", "Chart_HD", "Chart_IN", "Chart_AT", "Chart_Legacy",
        "IllustrationBlur", "IllustrationLowRes", "Illustration", "music"
    ]:
        try: rmtree(f"./unpack-result/{i}")
        except Exception: pass
        try: mkdir(f"./unpack-result/{i}")
        except FileExistsError: pass
    
    key = base64.b64decode(catalog["m_KeyDataString"])
    bucket = base64.b64decode(catalog["m_BucketDataString"])
    entry = base64.b64decode(catalog["m_EntryDataString"])
    
    table = []
    reader = ByteReaderB(bucket)
    
    for _ in range(reader.readInt()):
        key_position = reader.readInt()
        key_type = key[key_position]
        key_position += 1
        
        match key_type:
            case 0:
                length = key[key_position]
                key_position += 4
                key_value = key[key_position:key_position + length].decode()
            case 1:
                length = key[key_position]
                key_position += 4
                key_value = key[key_position:key_position + length].decode("utf16")
            case 4:
                key_value = key[key_position]
        
        for _ in range(reader.readInt()):
            entry_position = reader.readInt()
            entry_value = int.from_bytes(entry[4 + 28 * entry_position : 4 + 28 * entry_position + 28][8:10], "little")
            
        table.append([key_value, entry_value])
        
    for i in range(len(table)):
        if table[i][1] != 65535:
            table[i][1] = table[table[i][1]][0]
            
    for i in range(len(table) - 1, -1, -1):
        if type(table[i][0]) == int or table[i][0][:15] == "Assets/Tracks/#" or table[i][0][:14] != "Assets/Tracks/":
            del table[i]
        elif table[i][0][:14] == "Assets/Tracks/":
            table[i][0] = table[i][0][14:]
    
    def save(key: str, entry: UnityPy.files.BundleFile, fn: str):
        obj: UnityPy.classes.TextAsset | UnityPy.classes.Sprite | UnityPy.classes.AudioClip
        obj = next(entry.get_filtered_objects((ClassIDType.TextAsset, ClassIDType.Sprite, ClassIDType.AudioClip))).read()
        extended_info.append({
            "key": key,
            "fn": fn,
            "type": obj.type.value,
            "type_string": obj.type.name,
            "path_id": obj.path_id,
            "name": obj.name
        })
        
        if key[-14:-7] == "/Chart_" and key.endswith(".json"):
            name = key[:-14]
            iocommands.append(("save-string", f"Chart_{key[-7:-5]}/{name}.json", obj.script))
            
        elif key[-18:-11] == "/Chart_" and key.endswith(".json"):
            name = key[:-18]
            iocommands.append(("save-string", f"Chart_{key[-11:-5]}/{name}.json", obj.script))
            
        elif key.endswith("/IllustrationBlur.png"):
            name = key[:-21]
            iocommands.append(("save-pilimg", f"IllustrationBlur/{name}.png", obj.image))
            
        elif key.endswith("/IllustrationLowRes.png"):
            name = key[:-23]
            iocommands.append(("save-pilimg", f"IllustrationLowRes/{name}.png", obj.image))
            
        elif key.endswith("/Illustration.png"):
            name = key[:-17]
            iocommands.append(("save-pilimg", f"Illustration/{name}.png", obj.image))
            
        elif key.endswith("/music.wav"):
            name = key[:-10]
            fsb = FSB5(memoryview(obj.m_AudioData).tobytes())
            iocommands.append(("save-music", f"music/{name}.ogg", fsb.rebuild_sample(fsb.samples[0])))
    
    def io():
        nonlocal keunpack_count, save_string_count
        nonlocal save_pilimg_count, save_music_count
        nonlocal stopthread_count
        
        while True:
            try:
                item = iocommands.pop()
                if item is None: break
            except IndexError:
                break
            
            try:
                match item[0]:
                    case "ke-unpack":
                        env = UnityPy.Environment()
                        env.load_file(open(getZipItem(f"/assets/aa/Android/{item[2]}"), "rb").read(), name = item[1])
                        for ikey, ientry in env.files.items():
                            save(ikey, ientry, item[2])
                        keunpack_count += 1
                    case "save-string":
                        with open(f"./unpack-result/{item[1]}", "wb") as f:
                            f.write(item[2].tobytes())
                        save_string_count += 1
                    case "save-pilimg":
                        item[2].save(f"./unpack-result/{item[1]}", "png")
                        save_pilimg_count += 1
                    case "save-music":
                        with open(f"./unpack-result/{item[1]}", "wb") as f:
                            f.write(item[2])
                        save_music_count += 1
            except Exception as e:
                raise e
        
        stopthread_count += 1
    
    keunpack_count = 0
    save_string_count = 0
    save_pilimg_count = 0
    save_music_count = 0
    
    iothread_num = 32
    stopthread_count = 0
    iocommands = [None] * iothread_num
    extended_info = []
    
    for key, entry in table:
        iocommands.append(("ke-unpack", key, entry))

    iots = [Thread(target=io, daemon=True) for _ in range(iothread_num)]
    (*map(lambda x: x.start(), iots), )
    
    while stopthread_count != iothread_num:
        print(f"\r{keunpack_count} | {save_string_count} | {save_pilimg_count} | {save_music_count}", end="")
        sleep(0.1)
    
    with open(f"./unpack-result/extended_info.json", "w", encoding="utf-8") as f:
        json.dump(extended_info, f, indent=4, ensure_ascii=False)
    
    print()

def pack_charts(infos: list[dict], rpe: bool):
    try: rmtree(f"./unpack-result/packed")
    except Exception: pass
    try: mkdir(f"./unpack-result/packed")
    except FileExistsError: pass
        
    charts = []
    allcount = 0
    for info in infos:
        for li, l in enumerate(info["levels"]):
            chartFile = f'./unpack-result/Chart_{l}/{info["soundIdBak"]}.json'
            audioFile = f'./unpack-result/music/{info["soundIdBak"]}.ogg'
            imageFile = f'./unpack-result/Illustration/{info["soundIdBak"]}.png'
            csvData = "\n".join([
                "Chart,Music,Image,Name,Artist,Level,Illustrator,Charter,AspectRatio,NoteScale,GlobalAlpha",
                ",".join(map(lambda x: f'"{x}"' if " " in x else x, [
                    f'{info["soundIdBak"]}.json',
                    f'{info["soundIdBak"]}.ogg',
                    f'{info["soundIdBak"]}.png',
                    info["songName"],
                    info["composer"],
                    f'{l} Lv.{int(info["difficulty"][li])}',
                    info["illustrator"],
                    info["charter"][li]
                ]))
            ])
            charts.append((info["soundIdBak"], l, chartFile, audioFile, imageFile, csvData))
            allcount += 1
    
    packthread_num = 32
    stopthread_count = 0
    packed_num = 0
    charts_bak = charts.copy()
    
    def packworker(p2r: bool = False):
        nonlocal packed_num, stopthread_count
        
        while charts:
            try:
                item = charts.pop()
            except IndexError:
                break
            
            try:
                rid = uuid4()
                
                with open(f"./unpack-temp/pack-{rid}/info.csv", "w", encoding="utf-8") as f:
                    f.write(item[5])
                
                with zipfile.ZipFile('./unpack-result/packed/{}_{}{}.zip'.format(item[0], item[1], '_RPE' if p2r else ''), 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for file_path in (item[2], item[3], item[4], f"./unpack-temp/pack-{rid}/info.csv"):
                        zip_ref.write(file_path, arcname = basename(file_path))
                packed_num += 1
            except Exception:
                pass
        
        stopthread_count += 1
        
    ts = [Thread(target=packworker, daemon=True) for _ in range(packthread_num)]
    (*map(lambda x: x.start(), ts),)
    
    while stopthread_count != packthread_num:
        print(f"\r{packed_num} / {allcount}", end="")
        sleep(0.1)
    print(f"\r{packed_num} / {allcount}")
    
    if not rpe: return
    
    p2r = "tool-phi2rpe.py" if exists("tool-phi2rpe.py") and isfile("tool-phi2rpe.py") else "tool-phi2rpe.exe"
    phicharts = [f"./unpack-result/Chart_{l}/{i}" for l in ["EZ", "HD", "IN", "AT", "Legacy"] for i in listdir(f"./unpack-result/Chart_{l}")]
    p2rthread_num = 4
    p2red_num = 0
    stopthread_count = 0
    
    def p2rworker():
        nonlocal p2red_num, stopthread_count
        
        while phicharts:
            try:
                item = phicharts.pop()
            except IndexError:
                break
            
            try:
                popen(f"{p2r} {item} {item}").read()
                p2red_num += 1
            except Exception:
                pass
        
        stopthread_count += 1
    
    ts = [Thread(target=p2rworker, daemon=True) for _ in range(p2rthread_num)]
    (*map(lambda x: x.start(), ts),)
    
    while stopthread_count != p2rthread_num:
        print(f"\rp2r: {p2red_num} / {allcount}", end="")
        sleep(0.1)
    print(f"\rp2r: {p2red_num} / {allcount}")
    
    stopthread_count = 0
    packed_num = 0
    charts = charts_bak
    
    ts = [Thread(target=packworker, daemon=True, args=(True, )) for _ in range(packthread_num)]
    (*map(lambda x: x.start(), ts),)
    
    while stopthread_count != packthread_num:
        print(f"\rp2r pack: {packed_num} / {allcount}", end="")
        sleep(0.1)
    print(f"\rp2r pack: {packed_num} / {allcount}")

if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2:
        print("Usage: tool-unpack <apk>")
        raise SystemExit
    
    pgrapk = argv[1]
    run("--rpe" in argv)