import logging

import chartobj_phi
import tool_funcs

def Load_Chart_Object(phigros_chart: dict):
    logging.info("Loading Chart Object, fmt = phi")
    
    fmtVersion = phigros_chart.get("formatVersion", 3)
    
    def _loadMoveEvents(es: list[dict]):
        match fmtVersion:
            case 1:
                return [
                    chartobj_phi.judgeLineMoveEvent(
                        startTime = e.get("startTime", -1.0),
                        endTime = e.get("endTime", -1.0),
                        start = tool_funcs.unpack_pos(e.get("start", 0.0))[0] / 880,
                        end = tool_funcs.unpack_pos(e.get("end", 0.0))[0] / 880,
                        start2 = tool_funcs.unpack_pos(e.get("start", 0.0))[1] / 520,
                        end2 = tool_funcs.unpack_pos(e.get("end", 0.0))[1] / 520
                    ) for e in es
                ]
            case 3:
                return [
                    chartobj_phi.judgeLineMoveEvent(
                        startTime = e.get("startTime", -1.0), endTime = e.get("endTime", -1.0),
                        start = e.get("start", 0.5), end = e.get("end", 0.5),
                        start2 = e.get("start2", 0.5), end2 = e.get("end2", 0.5)
                    ) for e in es
                ]
            case _:
                logging.warning(f"Unsupported format version: {fmtVersion}")
                return [
                    chartobj_phi.judgeLineMoveEvent(
                        startTime = e.get("startTime", -1.0), endTime = e.get("endTime", -1.0),
                        start = e.get("start", 0.0), end = e.get("end", 0.0),
                        start2 = e.get("start2", 0.0), end2 = e.get("end2", 0.0)
                    ) for e in es
                ]
    
    phigros_chart_obj = chartobj_phi.Phigros_Chart(
        formatVersion = fmtVersion,
        offset = phigros_chart.get("offset", 0.0),
        judgeLineList = [
            chartobj_phi.judgeLine(
                bpm = line.get("bpm", -1.0),
                notesAbove = [
                    chartobj_phi.Note(
                        type = n.get("type", 1), time = n.get("time", -1.0),
                        positionX = n.get("positionX", 0.0), holdTime = n.get("holdTime", 0.0),
                        speed = n.get("speed", 0.0), floorPosition = n.get("floorPosition", -1.0),
                        above = True
                    ) for n in line.get("notesAbove", [])
                ],
                notesBelow = [
                    chartobj_phi.Note(
                        type = n.get("type", 1), time = n.get("time", -1.0),
                        positionX = n.get("positionX", 0.0), holdTime = n.get("holdTime", 0.0),
                        speed = n.get("speed", 0.0), floorPosition = n.get("floorPosition", -1.0),
                        above = False
                    ) for n in line.get("notesBelow", [])
                ],
                speedEvents = [
                    chartobj_phi.speedEvent(
                        startTime = e.get("startTime", -1.0),
                        endTime = e.get("endTime", -1.0), value = e.get("value", 0.0)
                    ) for e in line.get("speedEvents", [])
                ],
                judgeLineMoveEvents = _loadMoveEvents(line.get("judgeLineMoveEvents", [])),
                judgeLineRotateEvents = [
                    chartobj_phi.judgeLineRotateEvent(
                        startTime = e.get("startTime", -1.0), endTime = e.get("endTime", -1.0),
                        start = e.get("start", 0.0), end = e.get("end", 0.0)
                    ) for e in line.get("judgeLineRotateEvents", [])
                ],
                judgeLineDisappearEvents = [
                    chartobj_phi.judgeLineDisappearEvent(
                        startTime = e.get("startTime", -1.0), endTime = e.get("endTime", -1.0),
                        start = e.get("start", 0.0), end = e.get("end", 0.0)
                    ) for e in line.get("judgeLineDisappearEvents", [])
                ]
            )
            for line in phigros_chart.get("judgeLineList", [])
        ]
    )
    
    logging.info("Load Chart Object Successfully, fmt = phi")
    return phigros_chart_obj