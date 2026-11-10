# 范例：Apple《My Password》（2026-11-10）

输入是一段真实课堂视频（45 秒）。音轨抽成 16 kHz 单声道后走与录音案例相同的
声学管线；照片从视频里抽帧选取（正面报告的拍立得），题注如实标注来源。

本目录保留实测数据 `audio_data.json`（50 ms 峰值包络 + 基频序列）与简版案例数据 `case.json`。

出于隐私，视频原件、抽帧照片与成品报告 PDF 均不随仓库分发。
把 `audio_data.json` 放在案例目录、配合仓库根目录的字体运行 `scripts/build_front.py`
与 `scripts/build_back.py`，即可复现该报告（报告内容即两脚本中的案例段落；
本范例的正面走模板的照片模式，需要案例目录中另有 `photo.jpg`）。
同目录的 `case.json` 是简版的案例数据，运行 `scripts/build_simple.py` 即出简版一页。
