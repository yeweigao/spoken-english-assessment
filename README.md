# 儿童英语口语测评 · Spoken English Assessment

把一段儿童英语口语录音，做成报告：详细版两页 A4（正面成长记录 + 背面维度对标表），另有简版一页 A4 给家长快速读，两份并行独立。测评的立身之本是**原生音频实测**——发音、流利度、语调的结论只来自录音本身的声学测量与多系统识别交叉核对，不从转写文字推断。

- 六个维度（词汇 / 句式与语法 / 完整与创意 / 发音准确度 / 流利度 / 语调与重音），维度对标 IELTS 口语四项标准、量规参照剑桥少儿英语 Starters 与 CEFR Pre-A1–A1（对标是维度与量规层面，不是分数换算）
- 幼儿园孩子不用数字分，用小红花分档（参照剑桥少儿以「盾牌」计数代替分数的做法）
- 全本地运行，不需要任何 API key：Praat 声学测量 + 三套离线识别（Whisper small/medium、Parakeet）交叉核对 + ReportLab 绘图
- 自由表达与朗读两类任务：朗读对着原文逐词比，查得出识别器自动「改对」的读错

## 快速开始

```bash
pip install reportlab pypdf praat-parselmouth numpy pillow fonttools faster-whisper
pip install sherpa-onnx jieba                # 可选：Parakeet 第三套识别；中文按词断行
python3 scripts/download_fonts.py          # 字体不随仓库分发，首次使用先下载（开源字体，OFL）
python3 scripts/download_models.py         # 三个本地识别模型 → assets/models/（约 2.6 GB，只需一次；之后离线运行）
#   连不上 Hugging Face：HF_ENDPOINT=https://hf-mirror.com python3 scripts/download_models.py
# 每个孩子一个案例目录，以下都在案例目录里运行；脚本不改，案例内容写 case.json（范例见 examples/*/case.json）
ffmpeg -i input.mp4 -ar 16000 -ac 1 speech-16k.wav
python3 scripts/pick_frame.py input.mp4            # 视频：先出联系表选帧，再 --at 秒数 --box 裁切 → photo.jpg
python3 scripts/extract_audio_data.py speech-16k.wav
python3 scripts/transcribe.py                # 三套本地识别 → asr/
python3 scripts/analyze.py                  # 技术指标 → analysis.json
python3 scripts/score_sound.py              # 声音三维花数与证据 → sound_scores.json
python3 scripts/build_simple.py             # 简版一页 report-simple.pdf
# 详细版（正面 / 背面）的案例内容仍写在 build_front.py / build_back.py 里：
python3 scripts/build_front.py && python3 scripts/build_back.py && python3 scripts/build_report.py
```

完整规程（分析方法、量规、排版法、对外表述边界、验收清单）在 [SKILL.md](SKILL.md)；量规锚点在 [references/rubric.md](references/rubric.md)；版式与文字体系在 [references/type-system.md](references/type-system.md)；完整范例两个：[examples/toto-2026-11-09](examples/toto-2026-11-09)（纯音频）与 [examples/apple-2026-11-10](examples/apple-2026-11-10)（真实视频输入），出于隐私，范例不含录音/视频原件与成品 PDF，只保留实测数据。

## 结构

- `SKILL.md` / `skill.yaml` — 技能规程（可直接作为 Muse skill 安装到 `~/workspace/custom-skills/` 或 `~/.claude/skills/` 类目录）
- `scripts/` — 抽帧选图、识别、声学分析、声音评分、简版与正/背面生成、合并、字体下载、内部依据文件
- `references/` — 六维量规、对外表述边界（内部）、文字与版式体系
- `assets/fonts/` — 字体目录（由 download_fonts.py 填充，.gitignore 已排除）
