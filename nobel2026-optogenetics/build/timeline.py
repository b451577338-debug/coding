# Lay out narration clips on a global timeline and mix the voice track.
import json, subprocess
data = json.load(open("timing_raw.json"))
LEAD = {"s01": 3.0, "s02": 0.8}; DEFAULT_LEAD = 0.7
GAP = 0.32; TAIL = 0.9; END_TAIL = 4.0
t = 0.0; scenes = []; cues = []
for s in data:
    start = t; t += LEAD.get(s["id"], DEFAULT_LEAD)
    for c in s["clips"]:
        cues.append({"start": round(t, 3), "end": round(t + c["dur"], 3), "text": c["text"], "file": c["file"], "scene": s["id"]})
        t += c["dur"] + GAP
    t += (END_TAIL if s["id"] == "s10" else TAIL) - GAP
    scenes.append({"id": s["id"], "start": round(start, 3), "end": round(t, 3)})
total = round(t, 3)
json.dump({"total": total, "scenes": scenes, "cues": cues}, open("timeline.json", "w"), ensure_ascii=False, indent=1)
open("timeline.js", "w").write("window.TIMELINE=" + json.dumps({"total": total, "scenes": scenes, "cues": cues}, ensure_ascii=False) + ";")
# voice mix
inputs, filt = [], []
for i, c in enumerate(cues):
    inputs += ["-i", c["file"]]
    ms = int(c["start"] * 1000)
    filt.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0,apad=whole_dur={total}[v]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[v]", "-ac", "2", "-t", str(total), "voice.wav"], check=True)
for s in scenes: print(s)
print("total", total)
