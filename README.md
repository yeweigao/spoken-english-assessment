# 儿童英语口语测评 · Spoken English Assessment

把一段儿童英语口语录音或视频，做成报告。**默认出简版一页 A4**：页眉 → 六维雷达 + 老师说（便利贴；没评语时退回总览）→ 逐项解读 → 接下来怎么做；颜色可选六套马卡龙主题，底部插画跟着换色。默认路线是**千问原生听音频**——整段听两遍（裸听转写 + 原文锚定逐词核对），不出测量值，几分钟出片。需要可复现的声学测量、或要详细版两页（正面成长记录 + 背面瑞士排版对标表）时，再走本地实测管线。

- 六个维度（词汇 / 句式与语法 / 完整与创意 / 发音准确度 / 流利度 / 语调与重音），维度对标 IELTS 口语四项标准、量规参照剑桥少儿英语 Starters 与 CEFR Pre-A1–A1（对标是维度与量规层面，不是分数换算）
- 幼儿园孩子不用数字分，用小红花分档（参照剑桥少儿以「盾牌」计数代替分数的做法）
- 两条路线：听评档零模型、零 API key（录音会上云）；实测档本地离线（Praat 声学测量 + 三套离线识别 Whisper small/medium、Parakeet 交叉核对）
- 自由表达与朗读两类任务：朗读对着原文逐词比（原文必须是书上原文），查得出识别器自动「改对」的读错
- 家长页只放结论与短引语，不印孩子全文；全文留在 `case.json` 作记录
- 简版主题色 `theme`：cream（默认）/ mint / sakura / sky / lilac / peach；红色不随主题变，始终只给小红花与练习词

## 快速开始

```bash
pip install reportlab pypdf numpy pillow fonttools jieba python-pptx pymupdf
# 每个孩子一个案例目录（cases/<名字>-<日期>/），以下都在案例目录里运行；脚本不改，内容写 case.json
ffmpeg -i input.mp4 -vn -c:a copy audio.m4a        # 听评档：抽音轨交给模型听
python3 scripts/build_simple.py             # 简版一页 report-simple.pdf + 可编辑版 report-simple.pptx（theme + teacher + audio 都写在 case.json）
#   case.json 写 "audio": "audio.m4a"：缺 audio_data.json 时本机自动取响度包络，画底部的"声音山"（不上云、不印数字）
python3 scripts/install_fonts.py            # 老师电脑上装一次报告字体（字体先 download_fonts.py 取，或分发 zip 时附带；免管理员），PPT 才和 PDF 一个样
```

实测档（需要可复现的测量值或详细版两页时才装）：

```bash
pip install praat-parselmouth faster-whisper sherpa-onnx
python3 scripts/download_models.py         # 三套本地识别模型 → assets/models/（约 2.6 GB；之后离线运行）
ffmpeg -i input.mp4 -ar 16000 -ac 1 speech-16k.wav
python3 scripts/pick_frame.py input.mp4            # 视频：先出联系表选帧，再 --at 秒数 --box 裁切 → photo.jpg
python3 scripts/extract_audio_data.py speech-16k.wav
python3 scripts/transcribe.py && python3 scripts/analyze.py && python3 scripts/score_sound.py
python3 scripts/build_simple.py
python3 scripts/build_detail.py            # 详细版两页 report.pdf（案例内容写在 case.json 的 detail 段）
```

完整规程（路线选择、分析方法、量规、排版法、对外表述边界、验收清单）在 [SKILL.md](SKILL.md)；听评两遍听协议在 [references/listen-track.md](references/listen-track.md)；量规锚点在 [references/rubric.md](references/rubric.md)；版式与文字体系（含六套主题、老师说）在 [references/type-system.md](references/type-system.md)；完整范例两个：[examples/toto-2026-11-09](examples/toto-2026-11-09)（纯音频）与 [examples/apple-2026-11-10](examples/apple-2026-11-10)（真实视频输入），出于隐私，范例不含录音/视频原件与成品 PDF，只保留实测数据。

## 结构

- `SKILL.md` / `skill.yaml` — 技能规程（可直接作为 Muse skill 安装到 `~/workspace/custom-skills/` 或 `~/.claude/skills/` 类目录）
- `scripts/` — 抽帧选图、识别、声学分析、声音评分、简版与正/背面生成、合并、字体下载、内部依据文件
- `references/` — 六维量规、对外表述边界（内部）、文字与版式体系
- `assets/brand/` — 品牌标志（`cieg-logo.png` 集团、`kindergarten-logo.png` 幼儿园），RGBA 透明底 PNG，随包分发；换园所 logo 时把新图覆盖 `kindergarten-logo.png` 或在 case.json 写 `"school_logo": "你的图.png"`。白底图用 `python3 scripts/make_logo_transparent.py 输入图 输出.png [预览底色]` 抠成透明（盾形等内部白底会保留，只删外圈白）。
- `assets/fonts/` — 报告字体**不入 git**（约 22 MB）：跑 `download_fonts.py` 从 Google Fonts 取并实例化静态字重（思源黑体、站酷快乐体、Inter、Patrick Hand，均为 SIL OFL，许可文本 `OFL-*.txt` 已入库）。打包 zip 分发 skill 时把该目录一并放进去，再用 `install_fonts.py` 装到老师电脑。

  手动下载：Noto Sans SC https://fonts.google.com/noto/specimen/Noto+Sans+SC · ZCOOL KuaiLe https://fonts.google.com/specimen/ZCOOL+KuaiLe · Inter https://fonts.google.com/specimen/Inter · Patrick Hand https://fonts.google.com/specimen/Patrick+Hand
- `assets/brand/` — 页脚标志：`cieg-logo.png`（加拿大国际教育集团）、`kindergarten-logo.png`（默认幼儿园，可由 case.json 的 `school_logo` 换成各园自己的），均为透明底 PNG
