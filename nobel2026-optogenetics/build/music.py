# Procedural ambient score: slow pad chords + soft bells at scene changes + "zap" ticks for light pulses.
import json, numpy as np, wave
T = json.load(open("timeline.json")); total = T["total"]; SR = 48000
n = int(total * SR); t = np.arange(n) / SR
out = np.zeros((n, 2))
def hz(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [43, 50, 55, 58, 62], [45, 52, 57, 61, 64],
          [50, 57, 62, 65, 72], [41, 48, 53, 57, 60], [43, 50, 55, 59, 62], [45, 52, 57, 60, 64]]
CH = 7.0
for k in range(int(total / CH) + 2):
    s0 = k * CH; ch = chords[k % len(chords)]
    a, b = int(max(0, s0 - 1.5) * SR), int(min(total, s0 + CH + 2.5) * SR)
    if a >= n: break
    tt = t[a:b] - (s0 - 1.5)
    env = np.clip(tt / 2.5, 0, 1) * np.clip((CH + 4 - tt) / 2.5, 0, 1)
    for j, m in enumerate(ch):
        f = hz(m)
        for det, pan in ((-0.12, 0.25), (0.12, 0.75)):
            w = np.sin(2 * np.pi * (f + det) * tt + j) + 0.18 * np.sin(2 * np.pi * 2 * (f + det) * tt)
            amp = 0.022 * (0.6 if m > 64 else 1.0)
            out[a:b, 0] += w * env * amp * (1 - pan); out[a:b, 1] += w * env * amp * pan
# sub drone
out += (0.03 * np.sin(2 * np.pi * hz(38) * t) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 11)))[:, None]
def bell(at, m, vol=0.10, dec=3.0):
    a = int(at * SR); L = int(min(dec * 2.2, total - at) * SR)
    if L <= 0: return
    tt = np.arange(L) / SR; f = hz(m)
    w = (np.sin(2*np.pi*f*tt) + 0.5*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*2) + 0.25*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*4))
    w *= np.exp(-tt / dec) * np.clip(tt / 0.005, 0, 1) * vol
    out[a:a+L] += w[:, None]
for i, s in enumerate(T["scenes"]):
    bell(s["start"] + 0.15, [74, 77, 81, 79][i % 4], 0.07)
    bell(s["start"] + 0.45, [86, 89, 88, 84][i % 4], 0.035)
# title shimmer (opening)
for i, m in enumerate([81, 84, 88, 93, 96]): bell(2.0 + i * 0.18, m, 0.04, 2.0)
# scene 6 light pulses: soft ticks on a 1.2s grid during the "flash" section
s6 = next(s for s in T["scenes"] if s["id"] == "s06")
p = s6["start"] + 11.9
while p < s6["start"] + 20.3:
    bell(p, 96, 0.05, 0.25); p += 1.0
# finale swell
s10 = T["scenes"][-1]
for i, m in enumerate([62, 69, 74, 78, 81]): bell(s10["end"] - 8 + i * 0.25, m, 0.06, 5.0)
# simple stereo reverb via multi-tap feedback
rev = np.zeros_like(out)
for d, g in ((0.031, .35), (0.047, .3), (0.071, .27), (0.113, .22), (0.173, .18), (0.257, .14)):
    k = int(d * SR); rev[k:, 0] += out[:-k, 1] * g; rev[k:, 1] += out[:-k, 0] * g
out = out + rev
fade = np.ones(n); fi = int(2.5 * SR); fo = int(4 * SR)
fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
out *= fade[:, None]; out /= max(1e-9, np.abs(out).max()); out *= 0.9
pcm = (out * 32767).astype(np.int16)
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("music ok", total)
