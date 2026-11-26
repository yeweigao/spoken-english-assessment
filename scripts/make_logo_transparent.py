#!/usr/bin/env python3
"""Knock a white-background logo JPEG/PNG out to a transparent PNG.

Usage:  python3 scripts/make_logo_transparent.py 输入图 输出.png [纯色底色]

The white is removed by unmixing: every pixel is treated as a mix of the logo's
own colour and white, so the alpha of a half-covered edge pixel is recovered and
the colour is pushed back to full strength (no pale fringe). The result is then
cropped to its content with a small margin.
"""
import sys
import numpy as np
from PIL import Image


def knockout(src, dst, preview_bg=None, margin=6, keep_inner=True):
    """Remove the OUTER white background, keep any white the logo itself owns
    (a shield's white body). Outer white is found by flooding from the canvas
    edge, so a white area enclosed by the logo's own outline stays opaque."""
    from collections import deque
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.float64)
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(axis=2); mn = a.min(axis=2)

    # white-ish = every channel high and the colour is not saturated
    whiteish = (mn > 232) & ((mx - mn) < 26)

    # flood the outer white from the canvas edge (4-connected)
    outside = np.zeros((h, w), dtype=bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if whiteish[y, x] and not outside[y, x]:
                outside[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if whiteish[y, x] and not outside[y, x]:
                outside[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and whiteish[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True; dq.append((ny, nx))

    # the logo's own colour = the most saturated pixel
    sat = mx - mn
    idx = np.unravel_index(np.argmax(sat), sat.shape)
    solid = a[idx]
    if sat.max() < 40:
        idx = np.unravel_index(np.argmin(mx), mx.shape)
        solid = a[idx]

    # alpha for the pixels next to the removed area: unmix against white
    denom = np.maximum(255.0 - solid, 1.0)
    edge = np.zeros((h, w), dtype=bool)
    edge[outside] = True
    # dilate the outside mask by one pixel → the anti-aliased rim
    d = outside.copy()
    d[1:, :] |= outside[:-1, :]; d[:-1, :] |= outside[1:, :]
    d[:, 1:] |= outside[:, :-1]; d[:, :-1] |= outside[:, 1:]
    rim = d & ~outside & whiteish

    alpha = np.ones((h, w))
    a_rim = np.clip(np.max(np.stack([(255.0 - r) / denom[0],
                                    (255.0 - g) / denom[1],
                                    (255.0 - b) / denom[2]]), axis=0), 0.0, 1.0)
    alpha[rim] = a_rim[rim]
    alpha[outside] = 0.0
    if not keep_inner:
        alpha[whiteish] = a_rim[whiteish]

    # unmix: colour = (pixel - (1-a) * white) / a → full-strength edges
    with np.errstate(divide='ignore', invalid='ignore'):
        rec = np.where(alpha[..., None] > 0.02,
                       (a - (1.0 - alpha[..., None]) * 255.0) / np.maximum(alpha[..., None], 1e-6),
                       solid)
    rec = np.clip(rec, 0, 255)

    out = np.dstack([rec, alpha * 255.0]).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')

    bbox = img.getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        x0 = max(0, x0 - margin); y0 = max(0, y0 - margin)
        x1 = min(img.width, x1 + margin); y1 = min(img.height, y1 + margin)
        img = img.crop((x0, y0, x1, y1))

    img.save(dst)
    if preview_bg:
        flat = Image.new('RGB', img.size, preview_bg)
        flat.paste(img, (0, 0), img)
        flat.save(dst + '-preview.png')
    print(f'{dst}: {img.width}x{img.height}, 全透明 {int((np.asarray(img)[...,3] == 0).sum())} px, '
          f'不透明 {int((np.asarray(img)[...,3] == 255).sum())} px')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    preview = sys.argv[3] if len(sys.argv) > 3 else None
    keep = '--no-keep-inner' not in sys.argv
    knockout(src, dst, preview, keep_inner=keep)
