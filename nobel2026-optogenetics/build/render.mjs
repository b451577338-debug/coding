// Render frames [a, b) of the timeline into an H.264 chunk.
import { chromium } from "playwright";
import { spawn } from "child_process";
const [a, b, out] = [Number(process.argv[2]), Number(process.argv[3]), process.argv[4]];
const FPS = 30;
const br = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
const p = await br.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto("http://127.0.0.1:8765/build/video.html", { waitUntil: "load" });
await p.evaluate(() => window.ready);
const ff = spawn("ffmpeg", ["-y", "-v", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
  "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-r", String(FPS), out], { stdio: ["pipe", "inherit", "inherit"] });
const t0 = Date.now();
for (let f = a; f < b; f++) {
  const data = await p.evaluate(t => { window.renderAt(t); return document.getElementById("c").toDataURL("image/jpeg", .95); }, f / FPS);
  const buf = Buffer.from(data.slice(data.indexOf(",") + 1), "base64");
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
  if ((f - a) % 300 === 0) console.log(out, f, ((Date.now() - t0) / 1000).toFixed(0) + "s");
}
ff.stdin.end(); await new Promise(r => ff.on("close", r)); await br.close();
console.log("done", out, ((Date.now() - t0) / 1000).toFixed(0) + "s");
