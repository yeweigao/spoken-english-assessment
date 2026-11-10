#!/usr/bin/env python3
"""Pick the still for the front-page polaroid from the child's video.

Step 1 — candidates:   python3 pick_frame.py video.mp4
    Writes frame-candidates.jpg in the current (case) directory: the sharpest moments, at least
    1.4 s apart, each labelled with its time. LOOK at it and choose the frame where the child
    faces the camera with eyes open — sharpness alone cannot tell a blink from a smile.

Step 2 — the still:     python3 pick_frame.py video.mp4 --at 38.3 [--box x0,y0,x1,y1]
    Takes the sharpest frame within ±0.3 s of --at and writes photo.jpg. --box is the crop in
    pixels of the video frame (head and shoulders, roughly 9:10 portrait); without it the script
    writes frame-grid.jpg with a 100 px grid so you can read the box off the picture, and stops.
    Then set "photo": "photo.jpg" in case.json (the simple report reads it).

Needs: ffmpeg, pillow, numpy. The still shows a child's face: keep it in the case directory only."""
import argparse, glob, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

def frames(video, out_dir, fps=None, start=None, length=None):
    cmd = ['ffmpeg', '-v', 'error', '-y']
    if start is not None: cmd += ['-ss', f'{max(0, start):.2f}', '-t', f'{length:.2f}']
    cmd += ['-i', video]
    if fps: cmd += ['-vf', f'fps={fps}']
    cmd += ['-q:v', '2', os.path.join(out_dir, 'f_%05d.jpg')]
    subprocess.run(cmd, check=True)
    return sorted(glob.glob(os.path.join(out_dir, 'f_*.jpg')))

def sharpness(path):
    """Variance of a 4-neighbour Laplacian over the middle of the frame, where the child stands."""
    g = np.asarray(Image.open(path).convert('L'), dtype=np.float32)
    h, w = g.shape
    g = g[int(h * 0.1):int(h * 0.6), int(w * 0.15):int(w * 0.85)]
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('video'); ap.add_argument('--at', type=float); ap.add_argument('--box')
a = ap.parse_args()
if not os.path.isfile(a.video): sys.exit(f'找不到视频：{a.video}')

with tempfile.TemporaryDirectory() as tmp:
    if a.at is None:
        scored = sorted(((sharpness(p), i / 5.0, p) for i, p in enumerate(frames(a.video, tmp, fps=5))), reverse=True)
        picked = []
        for s, t, p in scored:
            if all(abs(t - q[1]) >= 1.4 for q in picked): picked.append((s, t, p))
            if len(picked) == 12: break
        if not picked: sys.exit('视频里没有读到画面')
        picked.sort(key=lambda r: r[1])
        tw = 300; tiles = []
        for s, t, p in picked:
            im = Image.open(p).convert('RGB'); im = im.resize((tw, round(im.height * tw / im.width)))
            im = im.crop((0, 0, tw, min(im.height, 400)))
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 78, 24], fill=(0, 0, 0)); d.text((6, 5), f'{t:.1f} s', fill=(255, 235, 0))
            tiles.append(im)
        cols = 6; rows = (len(tiles) + cols - 1) // cols; th = max(t.height for t in tiles)
        sheet = Image.new('RGB', (cols * tw, rows * th), (255, 255, 255))
        for k, im in enumerate(tiles): sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
        sheet.save('frame-candidates.jpg', quality=88)
        print('saved frame-candidates.jpg —', ', '.join(f'{t:.1f}s' for _, t, _ in picked))
        print('看图后选一帧（看镜头、睁眼、表情自然），再运行： pick_frame.py VIDEO --at 秒数')
    else:
        near = frames(a.video, tmp, start=a.at - 0.3, length=0.6)
        if not near: sys.exit('该时间点没有画面')
        best = Image.open(max(near, key=sharpness)).convert('RGB')
        if not a.box:
            g = best.copy(); d = ImageDraw.Draw(g)
            for yy in range(0, g.height, 100): d.line([(0, yy), (g.width, yy)], fill=(255, 235, 0)); d.text((4, yy + 2), str(yy), fill=(255, 235, 0))
            for xx in range(0, g.width, 100): d.line([(xx, 0), (xx, g.height)], fill=(0, 255, 255)); d.text((xx + 2, 4), str(xx), fill=(0, 255, 255))
            g.save('frame-grid.jpg', quality=88)
            sys.exit('saved frame-grid.jpg —— 对着网格读出头肩范围，再加 --box x0,y0,x1,y1（宽高比约 9:10）')
        x0, y0, x1, y1 = (int(v) for v in a.box.split(','))
        if not (0 <= x0 < x1 <= best.width and 0 <= y0 < y1 <= best.height): sys.exit('--box 超出画面')
        if not 0.75 <= (x1 - x0) / (y1 - y0) <= 1.05: print('提示：裁切框宽高比最好在 9:10 左右，否则版面会再裁一次')
        best.crop((x0, y0, x1, y1)).save('photo.jpg', quality=92)
        print('saved photo.jpg —— 在 case.json 里写上 "photo": "photo.jpg"')
