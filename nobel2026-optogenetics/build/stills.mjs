import { chromium } from "playwright";
const times = process.argv.slice(2).map(Number);
const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium", args: ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
const errs = []; p.on("pageerror", e => errs.push(String(e))); p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
await p.goto("http://127.0.0.1:8765/build/video.html", { waitUntil: "load" });
await p.evaluate(() => window.ready);
for (const t of times) {
  const t0 = Date.now();
  const data = await p.evaluate(t => { window.renderAt(t); return document.getElementById("c").toDataURL("image/jpeg", .85); }, t);
  const fs = await import("fs");
  fs.writeFileSync(`/tmp/claude-0/-home-user-coding/81e6f1f7-e8c9-507a-8754-65fe024800e1/scratchpad/still_${t.toFixed(1)}.jpg`, Buffer.from(data.split(",")[1], "base64"));
  console.log(t, Date.now() - t0, "ms");
}
console.log("errors:", errs.slice(0, 5));
await b.close();
