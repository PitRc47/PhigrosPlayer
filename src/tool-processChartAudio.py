from sys import argv
from json import load

from pydub import AudioSegment

import const
import chartfuncs_rpe

NoteClickAudios = {
    const.NOTE_TYPE.TAP: AudioSegment.from_file("resources/resource_default/click.ogg"),
    const.NOTE_TYPE.DRAG: AudioSegment.from_file("resources/resource_default/drag.ogg"),
    const.NOTE_TYPE.HOLD: AudioSegment.from_file("resources/resource_default/click.ogg"),
    const.NOTE_TYPE.FLICK: AudioSegment.from_file("resources/resource_default/flick.ogg")
}

with open(argv[1], "r", encoding="utf-8") as f:
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

delay = (-float(argv[argv.index("--delay") + 1])) if "--delay" in argv else 0.0
delay += Chart["offset"]
Chart["offset"] = 0.0
for line in Chart["judgeLineList"]:
    for note in line["notesAbove"]:
        note["time"] += delay / (1.875 / line["bpm"])
    for note in line["notesBelow"]:
        note["time"] += delay / (1.875 / line["bpm"])

chartAudio: AudioSegment = AudioSegment.from_file(argv[2])
allLength = chartAudio.duration_seconds

# 分割次数为 note 数量开根号时, 性能最好
blockLength = chartAudio.duration_seconds * 1000 / max(1.0, sum(len(l["notesAbove"] + l["notesBelow"]) for l in Chart["judgeLineList"]) ** 0.5) # ms
blockNum = int(allLength / (blockLength / 1000)) + 1
blocks = [AudioSegment.silent(blockLength + 500) for _ in [None] * blockNum]

for line_index, line in enumerate(Chart["judgeLineList"]):
    T = 1.875 / line["bpm"]
    notes = (line["notesAbove"] + line["notesBelow"]) if (line["notesAbove"] and line["notesBelow"]) else (
        line["notesAbove"] if line["notesAbove"] else line["notesBelow"]
    )
    for note_index, note in enumerate(notes):
        try:
            nt = note["time"] * T
            t_index = int(nt / (blockLength / 1000))
            seg: AudioSegment = blocks[t_index]
            nt %= blockLength / 1000
            blocks[t_index] = seg.overlay(NoteClickAudios[note["type"]], nt * 1000)
            print(f"Process Note: {line_index}+{note_index}")
        except IndexError:
            pass

class SegMerger:
    def __init__(self, segs: list[AudioSegment]):
        self.segs = segs
    
    def merge(self, chartAudio: AudioSegment, rawlen: float):
        for i, seg in enumerate(self.segs):
            chartAudio = chartAudio.overlay(seg, i * rawlen)
        return chartAudio

print("Merge...")
SegMerger(blocks).merge(chartAudio, blockLength).export(argv[3])
print("Done.")