const argv = process.argv.slice(2);
const fs = require("fs");

if (argv.length < 2) {
    console.log("Usage: tool-milthm-js2json <input> <output>");
    process.exit(1);
}

const milmth_chart = fs.readFileSync(argv[0], "utf-8");

class MilizeBeatmapClass {
    constructor() {
        this.mil = {
            meta: {},
            bpms: [],
            lines: [],
            storyboardObjects: [],
            animations: []
        };
    }

    /**
     * BeatmapAddBpm (float start, float bpm, int beatsPerBar)
     * @param {Number} start 
     * @param {Number} bpm 
     * @param {Number} beatsPerBar 
     */
    timing(start, bpm, beatsPerBar) {
        beatmap.mil.bpms.push({
            start: start,
            bpm: bpm,
            beatsPerBar: beatsPerBar
        })
    }

    /**
     * BeatmapAddStoryboardObject (int type, IntPtr data, int layer)
     * @param {Number} type 
     * @param {Number} data 
     * @param {Number} layer 
     */
    storyboardObject(type, data, layer) {
        beatmap.mil.storyboardObjects.push({
            type: type,
            data: data,
            layer: layer
        })
    }

    /**
     * BeatmapAddNote (int line, int bpm, IntPtr startTime, IntPtr endTime, int type, int isFake, int isAlwaysPerfect)
     * @param {Number} line 
     * @param {Number} bpm 
     * @param {Number} startTime 
     * @param {Number} endTime 
     * @param {Number} type 
     * @param {Boolean} isFake 
     * @param {Boolean} isAlwaysPerfect 
     */
    note(line, bpm, startTime, endTime, type, isFake, isAlwaysPerfect) {
        beatmap.mil.lines[line].notes.push({
            bpm: bpm,
            startTime: startTime,
            endTime: endTime,
            type: type,
            isFake: isFake,
            isAlwaysPerfect: isAlwaysPerfect
        })
    }

    /**
     * BeatmapAddAnimation (int bpmId, IntPtr fromBeat, IntPtr toBeat, int key, IntPtr fv, IntPtr tv, int data, int i1, int press, int ease, int valueExpression, IntPtr customEaseExpression)
     * @param {Number} bpmId 
     * @param {Number} fromBeat 
     * @param {Number} toBeat 
     * @param {Number} key 
     * @param {String} fv 
     * @param {String} tv 
     * @param {Number} data 
     * @param {Number} i1 
     * @param {Number} press 
     * @param {Number} ease 
     * @param {Boolean} valueExpression 
     * @param {String} customEaseExpression 
     */
    animation(bpmId, fromBeat, toBeat, key, fv, tv, data, i1, press, ease, valueExpression, customEaseExpression) {
        beatmap.mil.animations.push({
            bpmId: bpmId,
            fromBeat: fromBeat,
            toBeat: toBeat,
            key: key,
            fv: fv,
            tv: tv,
            data: data,
            i1: i1,
            press: press,
            ease: ease,
            valueExpression: valueExpression,
            customEaseExpression: customEaseExpression
        })
    }

    withProperty(key, value) {
        beatmap.mil.meta[key] = value;
        return beatmap;
    }

    line() {
        beatmap.mil.lines.push({
            notes: []
        });
    }
}

const beatmap = new MilizeBeatmapClass();
const MilizeBeatmap = beatmap;
eval(milmth_chart);

fs.writeFileSync(argv[1], JSON.stringify(beatmap.mil, null, 4));
