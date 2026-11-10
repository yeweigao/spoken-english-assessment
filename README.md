# 儿童英语口语测评 · Spoken English Assessment

把一段儿童英语口语录音，做成报告：详细版两页 A4（正面成长记录 + 背面维度对标表），另有简版一页 A4 给家长快速读，两份并行独立。测评的立身之本是**原生音频实测**——发音、流利度、语调的结论只来自录音本身的声学测量与多系统识别交叉核对，不从转写文字推断。

- 六个维度（词汇 / 句式与语法 / 完整与创意 / 发音准确度 / 流利度 / 语调与重音），维度对标 IELTS 口语四项标准、量规参照剑桥少儿英语 Starters 与 CEFR Pre-A1–A1（对标是维度与量规层面，不是分数换算）
- 幼儿园孩子不用数字分，用小红花分档（参照剑桥少儿以「盾牌」计数代替分数的做法）
- 全本地运行，不需要任何 API key：Praat 声学测量 + Vosk 离线识别 + ReportLab 绘图

## 快速开始

```bash
pip install reportlab pypdf praat-parselmouth vosk numpy fonttools
python3 scripts/download_fonts.py          # 字体不随仓库分发，首次使用先下载（开源字体，OFL）
ffmpeg -i recording.m4a -ar 16000 -ac 1 speech-16k.wav
python3 scripts/extract_audio_data.py speech-16k.wav
python3 scripts/analyze.py speech-16k.wav  # 脚本顶部 TARGET / SYL / sent_words 按课题改
# 按 SKILL.md 第四步定档，把结论填入 build_front.py / build_back.py 的对应位置，然后：
python3 scripts/build_front.py
python3 scripts/build_back.py
python3 scripts/build_report.py            # 合并为 report.pdf
python3 scripts/build_simple.py            # 简版一页 report-simple.pdf（在案例目录运行）
```

完整规程（分析方法、量规、排版法、对外表述边界、验收清单）在 [SKILL.md](SKILL.md)；量规锚点在 [references/rubric.md](references/rubric.md)；版式与文字体系在 [references/type-system.md](references/type-system.md)；完整范例两个：[examples/toto-2026-11-09](examples/toto-2026-11-09)（纯音频）与 [examples/apple-2026-11-10](examples/apple-2026-11-10)（真实视频输入），出于隐私，范例不含录音/视频原件与成品 PDF，只保留实测数据。

## 结构

- `SKILL.md` / `skill.yaml` — 技能规程（可直接作为 Muse skill 安装到 `~/workspace/custom-skills/` 或 `~/.claude/skills/` 类目录）
- `scripts/` — 数据抽取、声学分析、正/背面生成、合并、字体下载、内部依据文件
- `references/` — 六维量规、对外表述边界（内部）、文字与版式体系
- `assets/fonts/` — 字体目录（由 download_fonts.py 填充，.gitignore 已排除）
