import init_logging as _

import csv
import logging
from os.path import exists

class InfoLoader:
    default_info = {
        "Name": "Unknow",
        "Artist": "Unknow",
        "Level": "SP Lv.?",
        "Illustrator": "Unknow",
        "Charter": "Unknow",
        "BackgroundDim": 0.6
    }
    
    def __init__(self, infofiles):
        self.infomap = {}
        for file in infofiles:
            self.load(file)
    
    def load(self, filename, encoding="utf-8", _failed=False):
        "if load failed, return. else return True"
        
        if not exists(filename):
            return
        
        with open(filename, "r", encoding=encoding) as f:
            try:
                raw_data = f.read().replace("\ufeff", "")
            except Exception:
                if not _failed:
                    try:
                        return self.load(filename, "gbk", True)
                    except Exception:
                        pass
                return
            file_type = filename.split(".")[-1]
            
            try:
                match file_type:
                    case "csv":
                        csv_reader = csv.reader(raw_data.splitlines())
                        lines = list(filter(lambda x: x != "", csv_reader))
                        
                        meta_line = lines[0]
                        info_lines = lines[1:]
                        
                        for line in info_lines:
                            key = (
                                line[meta_line.index("Chart")],
                                line[meta_line.index("Music")],
                                line[meta_line.index("Image")]
                            )
                            value = {}
                            for i in self.default_info.keys():
                                try:
                                    value[i] = line[meta_line.index(i)]
                                except Exception:
                                    pass
                                
                            self.infomap[key] = value
                            
                    case "txt":
                        lines = [i for i in raw_data.splitlines() if ":" in i]
                        info = {i.split(":")[0]: i[i.index(":") + 1:] for i in lines}
                        info = {k: v if v[0] != " " else v[1:] for k, v in info.items()}
                        keymap = {
                            "Song": "Music",
                            "Picture": "Image",
                            "Composer": "Artist"
                        }
                        info = {keymap.get(k, k): v for k, v in info.items()}
                        
                        key = (
                            info["Chart"],
                            info["Music"],
                            info["Image"]
                        )
                        value = {}
                        for i in self.default_info.keys():
                            try:
                                value[i] = info[i]
                            except Exception:
                                pass
                        
                        self.infomap[key] = value
                        
                    case "yml":
                        return #  i think ... we don't need process yml, becasuse: normal, if yml file is exists, it can process info.txt!
                    
                    case _:
                        return
            except Exception:
                return
            
            return True
    
    def get(self, chart, music, image):
        info = self.infomap.get((chart, music, image), self.default_info)
        
        if info is self.default_info: # 谱师们别写错了啊啊啊啊啊啊啊啊啊啊
            info = self.infomap.get((chart, music, image.replace(".jpg", ".png")), self.default_info)
        if info is self.default_info:
            info = self.infomap.get((chart, music, image.replace(".png", ".jpg")), self.default_info)
            
        res = self.default_info.copy()
        res.update(info)
        
        try:
            res["BackgroundDim"] = float(res["BackgroundDim"])
        except ValueError as e:
            logging.error(f"BackgroundDim convert to float error: {e} ({res["BackgroundDim"]})")
            
        return res