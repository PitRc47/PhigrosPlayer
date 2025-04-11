import fix_workpath as _

import json
import random
import string
from os import mkdir, listdir
from os.path import isdir, normpath
from sys import argv
from shutil import rmtree, copyfile

if len(argv) < 3:
    print("Usage: tool-make-pgrassets-byunpack <unpack-result> <output-dir>")
    raise SystemExit

unpack_result = argv[1]
output_dir = argv[2]

try: rmtree(output_dir)
except FileNotFoundError: pass

try: mkdir(output_dir)
except FileExistsError: pass
try: mkdir(f"{output_dir}/res")
except FileExistsError: pass

if not isdir(f"{unpack_result}/other_res"):
    print("fatal: unpack result need other res (--need-other-res in unpack).")
    raise SystemExit

if not isdir(f"{unpack_result}/IllustrationLowRes"):
    print("fatal: unpack result need other illu (--need-other-illu in unpack).")
    raise SystemExit

pgr_chapters_info = json.load(open("./resources/pgr_chapters.json", "r", encoding="utf-8"))
upk_info = json.load(open(f"{unpack_result}/info.json", "r", encoding="utf-8"))
unp_all_ids = [i["songIdBak"] for i in upk_info]

for i in pgr_chapters_info:
    if i["split"] not in unp_all_ids:
        print(f"fatal: cannot find {i["split"]} in unpack result, please check your version.")
        raise SystemExit

class splitSongManager:
    def __init__(self, songs: list[dict]):
        self.songs = songs
    
    def get_songs(self, point: str, count: int, jumps: list[str]):
        jumps = jumps.copy()
        jumps.insert(0, point)
        result = []
        
        for i, point in enumerate(jumps):
            if i != len(jumps) - 1:
                result.extend([i for i in self.songs if i["songIdBak"] == point])
                count -= 1
            else:
                i = self.songs.index([i for i in self.songs if i["songIdBak"] == point][0])
                result.extend(self.songs[i:i + count])

        for i in self.songs.copy():
            if i["songIdBak"] in [j["songIdBak"] for j in result]:
                self.songs.remove(i)

        return result

class resourceManager:
    def __init__(self):
        self.resmap: dict[str, str] = {}
    
    def getres(self, path: str):
        path = normpath(path)
        
        if path in self.resmap:
            return self.resmap[path]
        
        newpath = f"/res/{"".join(random.sample(string.ascii_letters, 8))}." + path.split(".")[-1]
        copyfile(f"{unpack_result}{path}", f"{output_dir}{newpath}")
        self.resmap[path] = newpath
        return newpath
        
ssm = splitSongManager(upk_info.copy())
resm = resourceManager()
chapters = {
    "chapters": []
}

for cinfo in pgr_chapters_info:
    songs = ssm.get_songs(cinfo["split"], cinfo["count"], cinfo.get("jumps", []))

    if cinfo.get("reverse", False):
        songs.reverse()
    
    chapters_item = {
        "name": cinfo["name"],
        "cn-name": cinfo["cn-name"],
        "o-name": cinfo["o-name"],
        "image": resm.getres(cinfo["image"]),
        "songs": []
    }
    
    for s in songs:
        chapters_item["songs"].append({
            "name": s["songName"],
            "composer": s["composer"],
            "iller": s["illustrator"],
            "image": resm.getres(f"/Illustration/{s["songIdBak"]}.png"),
            "image_lowres": resm.getres(f"/IllustrationLowRes/{s["songIdBak"]}.png"),
            "preview": resm.getres(f"/music/{s["songIdBak"]}.ogg"),
            "preview_start": s["previewTimeStart"],
            "preview_end": s["previewTimeEnd"],
            "import_archive_alias": s["songId"],
            "difficlty": [
                {
                    "name": level,
                    "level": s["difficulty"][level_i],
                    "chart_audio": resm.getres(f"/music/{s["songIdBak"]}.ogg"),
                    "chart_image": resm.getres(f"/Illustration/{s["songIdBak"]}.png"),
                    "chart_file": resm.getres(f"/Chart_{level}/{s["songIdBak"]}.json"),
                    "charter": s["charter"][level_i]
                }
                for level_i, level in enumerate(s["levels"])
            ]
        })
    
    if cinfo.get("insert", None) is not None:
        chapters["chapters"].insert(cinfo["insert"], chapters_item)
    else:
        chapters["chapters"].append(chapters_item)

json.dump(chapters, open(f"{output_dir}/chapters.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

config = {
    "avatars": [],
    "backgrounds": [],
    "isfromunpack": True,
    "background-file-map": {}
}

default_avatar = "Introduction.png"
default_bg = "Introduction.png"

avatar_files = listdir(f"{unpack_result}/avatars")
for i in avatar_files:
    config["avatars"].append(resm.getres(f"/avatars/{i}"))
    
if default_avatar in avatar_files:
    config["default-avatar"] = resm.getres(f"/avatars/{default_avatar}")
else:
    config["default-avatar"] = config["avatars"][0]

bg_files = listdir(f"{unpack_result}/IllustrationLowRes")
for song in upk_info:
    bgpath = f"/IllustrationLowRes/{song["songIdBak"]}.png"
    config["background-file-map"][song["songKey"]] = bgpath
    config["backgrounds"].append(resm.getres(bgpath))

if default_bg in bg_files:
    config["default-background"] = resm.getres(f"/IllustrationLowRes/{default_bg}")
else:
    config["default-background"] = config["backgrounds"][0]

json.dump(config, open(f"{output_dir}/config.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
