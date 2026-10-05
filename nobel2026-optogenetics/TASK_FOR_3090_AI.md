# 任务说明：为科普视频生成"本人声音配音"和"数字人讲解"

> 这份说明是给运行在 3090 电脑上的 AI 助手看的。照着做完后，把文件推送到 GitHub，云端会合成最终视频。

## 背景
- 仓库：`b451577338-debug/coding`，分支：`claude/availability-check-yddmgd`
- 项目目录：`nobel2026-optogenetics/`
- 视频：《用光点亮大脑：2026 诺贝尔生理学或医学奖 · 光遗传学》，横屏 1920×1080，约 3 分 46 秒
- 本地已有：用户本人的声音模型（或声音样本）、用户的数字人素材，以及 3090 显卡

## 第 0 步：拉取仓库
```bash
git clone https://github.com/b451577338-debug/coding.git
cd coding
git checkout claude/availability-check-yddmgd
git pull
```

---

## 第 1 步：用本人声音生成旁白（先做这一步）

**输入**：`nobel2026-optogenetics/narration_lines.tsv`
- 以 `#` 开头的行是注释，跳过
- 其余每行用 Tab 分隔：`文件名  开始秒  参考时长  文本`，共 52 句
- 只需要用到"文件名"和"文本"两列，**时长不用卡**，按自然语速读就行，云端会自动重新排时间轴

**生成要求**：
- 用用户本人的声音模型（GPT-SoVITS / CosyVoice / F5-TTS 等，本机有哪个用哪个）
- 每句一个文件，文件名与第一列一致，例如 `s01_00.wav`、`s01_01.wav` …… `s10_04.wav`
- 格式：WAV，48 kHz（44.1 kHz 也可），单声道或立体声均可
- 语气：科普讲解，沉稳、清晰、带一点感染力；句首句尾不要留超过 0.3 秒的静音
- 多音字和读法注意：
  - "黑格曼""纳格尔""戴瑟罗斯"是人名，读清楚
  - "衣藻"读 yī zǎo
  - "通道视紫红质"读 tōng dào shì zǐ hóng zhì
  - "2026年10月5日"读作"二零二六年十月五日"
  - "2002到2003年"读作"二零零二到二零零三年"
- 生成完逐句听一遍，读错、吞字、有杂音的重新生成

**输出位置**：`nobel2026-optogenetics/user_assets/voice/`（52 个 wav 文件）

**推送**：
```bash
git add nobel2026-optogenetics/user_assets/voice
git commit -m "Add narration in user's own voice"
git push origin claude/availability-check-yddmgd
```
推送完告诉用户"配音已上传"。云端会据此重排时间轴，生成一条**完整旁白音轨** `nobel2026-optogenetics/user_assets/narration_full.wav` 推回仓库，供第 2 步使用。

---

## 第 2 步：用数字人生成讲解视频（等云端推回 `narration_full.wav` 后再做）

```bash
git pull origin claude/availability-check-yddmgd
```

**输入**：`nobel2026-optogenetics/user_assets/narration_full.wav`（完整旁白，带停顿，时长与成片一致）

**生成要求**：
- 用用户的数字人形象，以 `narration_full.wav` 驱动口型（MuseTalk / LatentSync / Wav2Lip / 本机已有的数字人工具均可）
- **整段一次生成，时长必须与 `narration_full.wav` 完全一致，从第 0 秒开始对齐**，不要剪掉开头或结尾的静音段
- 背景：**纯绿幕（#00FF00）**，或纯色背景；不要任何字幕、水印、背景音乐
- 构图：半身或胸部以上，人物居中，头顶留少量空间
- 分辨率：1080×1080 或 1920×1080 均可；帧率 25 或 30 fps
- 静音段落（没有说话的时候）人物保持自然微动、眨眼，不要定格
- 编码：H.264 MP4，**文件必须小于 90 MB**（GitHub 单文件上限 100 MB）。超了就用 `ffmpeg -i in.mp4 -c:v libx264 -crf 24 -preset slow -an avatar.mp4` 压缩，必要时降到 720p
- 音轨可以去掉（加 `-an`），云端会用配音音轨

**输出位置**：`nobel2026-optogenetics/user_assets/avatar/avatar.mp4`

**推送**：
```bash
git add nobel2026-optogenetics/user_assets/avatar
git commit -m "Add digital human narration video"
git push origin claude/availability-check-yddmgd
```
推送完告诉用户"数字人已上传"。

---

## 注意
- 只往 `nobel2026-optogenetics/user_assets/` 里加文件，不要改动仓库里的其他文件
- 不要 force push，不要改写历史
- 如果某一步做不了（比如本机没有对应模型），告诉用户卡在哪里、缺什么，不要用别的声音或形象代替
