from sys import argv
from json import load

from pydub import AudioSegment

import const
import chartfuncs_rpe

NoteClickAudios = {
    const.NOTE_TYPE.TAP: AudioSegment.from_file("./resources/resource_default/click.ogg"),
    const.NOTE_TYPE.DRAG: AudioSegment.from_file("./resources/resource_default/drag.ogg"),
    const.NOTE_TYPE.HOLD: AudioSegment.from_file("./resources/resource_default/click.ogg"),
    const.NOTE_TYPE.FLICK: AudioSegment.from_file("./resources/resource_default/flick.ogg")
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

ChartAudio: AudioSegment = AudioSegment.from_file(argv[2])
ChartAudio_Length = ChartAudio.duration_seconds

ChartAudio_Split_Audio_Block_Length = ChartAudio.duration_seconds * 1000 / 85 #ms
ChartAudio_Split_Length = int(ChartAudio_Length / (ChartAudio_Split_Audio_Block_Length / 1000)) + 1
ChartAudio_Split_Audio_List = [AudioSegment.silent(ChartAudio_Split_Audio_Block_Length + 500) for _ in [None] * ChartAudio_Split_Length]
JudgeLine_cut = 0

for JudgeLine in Chart["judgeLineList"]:
    t_dw = 1.875 / JudgeLine["bpm"]
    Note_cut = 0
    notes = (JudgeLine["notesAbove"] + JudgeLine["notesBelow"]) if (JudgeLine["notesAbove"] and JudgeLine["notesBelow"]) else (
        JudgeLine["notesAbove"] if JudgeLine["notesAbove"] else JudgeLine["notesBelow"]
    )
    for note in notes:
        try:
            t = note["time"] * t_dw
            t_index = int(t / (ChartAudio_Split_Audio_Block_Length / 1000))
            seg: AudioSegment = ChartAudio_Split_Audio_List[t_index]
            t %= ChartAudio_Split_Audio_Block_Length / 1000
            ChartAudio_Split_Audio_List[t_index] = seg.overlay(NoteClickAudios[note["type"]], t * 1000)
            print(f"Process Note: {JudgeLine_cut}+{Note_cut}")
            Note_cut += 1
        except IndexError:
            pass
    JudgeLine_cut += 1

print("Merge...")
for i,seg in enumerate(ChartAudio_Split_Audio_List):
    ChartAudio = ChartAudio.overlay(seg, i * ChartAudio_Split_Audio_Block_Length)

ChartAudio.export(argv[3])

print("Done.")