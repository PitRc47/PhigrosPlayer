import sys
import time
from json import load
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from pydub import AudioSegment

import const
import chartfuncs_rpe

NoteClickAudios: dict[int, AudioSegment] = {
    const.NOTE_TYPE.TAP: AudioSegment.from_file("./resources/resource_default/click.ogg"),
    const.NOTE_TYPE.DRAG: AudioSegment.from_file("./resources/resource_default/drag.ogg"),
    const.NOTE_TYPE.HOLD: AudioSegment.from_file("./resources/resource_default/click.ogg"),
    const.NOTE_TYPE.FLICK: AudioSegment.from_file("./resources/resource_default/flick.ogg")
}

with open(sys.argv[1], "r", encoding="utf-8") as f:
    Chart = load(f)

if "META" in Chart and "formatVersion" not in Chart:
    rpeobj = chartfuncs_rpe.Load_Chart_Object(Chart)
    Chart = {
        "formatVersion": 3,
        "offset": rpeobj.META.offset / 1000,
        "judgeLineList": [
            {
                "bpm": 1.875,
                "notesAbove": [
                    {
                        "time": note.secst,
                        "type": note.phitype
                    }
                    for note in line.notes if not note.isFake
                ],
                "notesBelow": []
            }
            for line in rpeobj.judgeLineList
        ]
    }

delay = (-float(sys.argv[sys.argv.index("--delay") + 1])) if "--delay" in sys.argv else 0.0
delay += Chart["offset"]
Chart["offset"] = 0.0
for line in Chart["judgeLineList"]:
    for note in line["notesAbove"]:
        note["time"] += delay / (1.875 / line["bpm"])
    for note in line["notesBelow"]:
        note["time"] += delay / (1.875 / line["bpm"])

chartAudio: AudioSegment = AudioSegment.from_file(sys.argv[2])
allLength = chartAudio.duration_seconds

# 分割次数为 note 数量开根号时, 性能最好
notesNum = sum(len(l["notesAbove"] + l["notesBelow"]) for l in Chart["judgeLineList"])
blockLength = chartAudio.duration_seconds * 1000 / max(1.0, notesNum ** 0.5) # ms
maxCksLength = max(i.duration_seconds for i in NoteClickAudios.values()) * 1000
blockNum = int(allLength / (blockLength / 1000)) + 1
blocks = [AudioSegment.silent(blockLength + maxCksLength) for _ in range(blockNum)]
getIndexBySec = lambda sec: int(sec / (blockLength / 1000))
tasks = [list() for _ in range(blockNum)]

for line_index, line in enumerate(Chart["judgeLineList"]):
    T = 1.875 / line["bpm"]
    notes = (line["notesAbove"] + line["notesBelow"]) if (line["notesAbove"] and line["notesBelow"]) else (
        line["notesAbove"] if line["notesAbove"] else line["notesBelow"]
    )
    for note_index, note in enumerate(notes):
        try:
            nt = note["time"] * T
            t_index = getIndexBySec(nt)
            nt %= blockLength / 1000
            tasks[t_index].append((note["type"], nt * 1000))
        except IndexError:
            notesNum -= 1

gilenable = hasattr(sys, "_is_gil_enabled") and sys._is_gil_enabled()
processed = 0

def merge_seg(raw: AudioSegment, task: list[tuple[int, float]]):
    global processed
    
    for ntype, nt in task:
        raw = raw.overlay(NoteClickAudios[ntype], nt)
        processed += 1
    
    return raw

def print_progress():
    gettext = lambda n: f"\rprogress: {(n / notesNum * 100):.2f}%    {n}/{notesNum}"
    maxlength = len(gettext(notesNum))
    print_once = lambda n, end="": print((text := gettext(n)) + " " * (maxlength - len(text)), end=end)
        
    while processed < notesNum:
        print_once(processed)
        time.sleep(1 / 15)
    
    print_once(processed, end="\n")

printer = Thread(target=print_progress, daemon=True)
printer.start()
st = time.perf_counter()

if gilenable:
    executor = ThreadPoolExecutor(max_workers=min(16, blockNum))
    futures = [executor.submit(merge_seg, blocks[i], task) for i, task in enumerate(tasks)]
    for i, future in enumerate(futures): blocks[i] = future.result()
else:
    for i, task in enumerate(tasks):
        blocks[i] = merge_seg(blocks[i], task)

printer.join()
print(f"Usage time: {(time.perf_counter() - st):.2f}s")

class SegMerger:
    def __init__(self, segs: list[AudioSegment]):
        self.segs = segs
    
    def merge(self, chartAudio: AudioSegment, rawlen: float):
        for i, seg in enumerate(self.segs):
            chartAudio = chartAudio.overlay(seg, i * rawlen)
        return chartAudio

print("Merge...")
SegMerger(blocks).merge(chartAudio, blockLength).export(sys.argv[3])
print("Done.")