import ssl, asyncio, json, subprocess, os, edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
VOICE = "zh-CN-YunxiNeural"
os.makedirs("audio", exist_ok=True)
data = json.load(open("narration.json"))
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
async def one(text, path):
    for i in range(6):
        try:
            await edge_tts.Communicate(text, VOICE, rate="-4%").save(path)
            if os.path.getsize(path) > 1000: return
        except Exception as e: print("retry", e)
        await asyncio.sleep(2+2*i)
    raise RuntimeError(text)
async def main():
    for s in data:
        s["clips"] = []
        for i, t in enumerate(s["lines"]):
            p = f"audio/{s['id']}_{i:02d}.mp3"
            if not os.path.exists(p) or os.path.getsize(p) < 1000: await one(t, p)
            s["clips"].append({"text": t, "file": p, "dur": round(dur(p), 3)})
        print(s["id"], round(sum(x["dur"] for x in s["clips"]),1))
    json.dump(data, open("timing_raw.json","w"), ensure_ascii=False, indent=1)
asyncio.run(main())
