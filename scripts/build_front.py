#!/usr/bin/env python3
"""Report FRONT page (growth-record style for child + parents).
Run from a case directory containing audio_data.json (see scripts/extract_audio_data.py).
Case content (name, texts, findings, flower counts) sits in the marked sections — edit per child."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, math

W, H = A4
BASE = os.path.dirname(os.path.abspath(__file__))
# --- skill packaging: fonts live in ../assets/fonts, case data (audio_data.json) in the CWD ---
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))
CASE = os.getcwd()


def reg(name, fname, fallback=None):
    p = os.path.join(FONTDIR, fname)
    if os.path.exists(p):
        pdfmetrics.registerFont(TTFont(name, p)); return name
    if fallback: return fallback
    raise SystemExit('missing font ' + fname)

pdfmetrics.registerFont(TTFont('SC', os.path.join(FONTDIR, 'NotoSC-Regular.ttf')))
reg('ENL', 'Inter-Light.ttf', 'ENR')
reg('SCB', 'NotoSC-SemiB.ttf', 'SC')
reg('SCS', 'NotoSC-Regular.ttf', 'SC')
reg('ENB', 'Inter-BoldF.ttf', 'SC')
reg('ENR', 'Inter-Reg.ttf', 'SC')
DISP = reg('ZCOOL', 'ZCOOLKuaiLe.ttf', 'SCB')   # rounded display if downloaded
HAND = reg('HAND', 'PatrickHand.ttf', 'ENB')     # handwriting for the encouragement line

INK   = HexColor('#000000')
SOFT  = HexColor('#1A1A1A')
CREAM = HexColor('#FFFFFF')
CARD  = HexColor('#FFFFFF')
YEL   = HexColor('#FFC93C')
YELD  = HexColor('#E8A90C')
BLUEB = HexColor('#AEDCF7')
YELB  = HexColor('#FFE08A')
GRNB  = HexColor('#C6E9C2')
RED   = HexColor('#E4572E')
PINK  = HexColor('#FF9FB2')
BLUE  = HexColor('#2E7CD6')
GREEN = HexColor('#3D9B50')
LBLUE = HexColor('#C4E2F8')
LINE  = HexColor('#E8E2D2')
DASHR = HexColor('#E4572E')

OUT = os.path.join(CASE, 'report-front.pdf')
c = canvas.Canvas(OUT, pagesize=A4)

def sw(t, f, s): return pdfmetrics.stringWidth(t, f, s)
def text(x, y, s, f='SCS', size=10, color=INK):
    c.setFont(f, size); c.setFillColor(color); c.drawString(x, y, s)
def wrap(s, font, size, maxw):
    tokens, i = [], 0
    while i < len(s):
        if s[i] == ' ': tokens.append(' '); i += 1
        elif ord(s[i]) < 128:
            j = i
            while j < len(s) and ord(s[j]) < 128 and s[j] != ' ': j += 1
            tokens.append(s[i:j]); i = j
        else: tokens.append(s[i]); i += 1
    lines, cur = [], ''
    for t in tokens:
        if sw(cur + t, font, size) <= maxw: cur += t
        else: lines.append(cur.rstrip()); cur = t.lstrip()
    if cur.strip(): lines.append(cur.rstrip())
    return lines
def para(x, y, s, f='SCS', size=9.5, color=INK, maxw=200, leading=14):
    for seg in s.split('\n'):
        for ln in wrap(seg, f, size, maxw):
            text(x, y, ln, f, size, color); y -= leading
    return y
def rrect(x, y, w, h, r, fill=None, stroke=None, swd=1):
    p = c.beginPath(); p.roundRect(x, y, w, h, r); c.setLineWidth(swd)
    if fill and stroke: c.setFillColor(fill); c.setStrokeColor(stroke); c.drawPath(p, stroke=1, fill=1)
    elif fill: c.setFillColor(fill); c.drawPath(p, stroke=0, fill=1)
    elif stroke: c.setStrokeColor(stroke); c.drawPath(p, stroke=1, fill=0)

M = 34; CW = W - 2 * M
c.setFillColor(CREAM); c.rect(0, 0, W, H, stroke=0, fill=1)
c.saveState(); c.translate(0, 12)   # whole module above the games zone rides 12pt up

# yellow blob top-right
c.saveState(); c.translate(W - 120, H - 30); c.rotate(-4)
rrect(-160, -58, 330, 120, 34, fill=YEL)
c.restoreState()

# ---------- header ----------
hy = H - 56
text(M + 2, hy, '2026 秋 · 口语测评', 'SCS', 8.5, SOFT)
text(M, hy - 34, '英语口语成长记录', DISP, 30, INK)
text(M + 2, hy - 52, 'My English Speaking Report', 'ENB', 11, SOFT)
text(M + 2, hy - 74, '姓名 Toto  ·  课题 My Funny Face  ·  2026.11.09  ·  37 秒', 'SCS', 9.5, INK)

# growth card
gx, gy, gw, gh = W - M - 236, hy - 66, 236, 62
rrect(gx + 3, gy - 5, gw, gh, 14, fill=HexColor('#F3E3B3'))
rrect(gx, gy, gw, gh, 14, fill=CARD)
text(gx + 14, gy + 42, '这一次，Toto 长到了这里', 'SCB', 11, INK)
stages = [('萌芽', HexColor('#B08968')), ('成长', GREEN), ('绽放', RED), ('闪耀', HexColor('#E79FBF'))]
for i, (nm, col) in enumerate(stages):
    cx = gx + 34 + i * 56; cy = gy + 22
    if nm == '绽放':
        c.setFillColor(YEL); c.circle(cx, cy, 13, stroke=0, fill=1)
    c.setFillColor(col)
    if nm == '萌芽': c.ellipse(cx - 6, cy - 3, cx + 6, cy + 4, stroke=0, fill=1)
    elif nm == '成长':
        c.setLineWidth(2); c.setStrokeColor(col); c.line(cx, cy - 6, cx, cy + 5)
        c.ellipse(cx - 7, cy + 2, cx - 0.5, cy + 8, stroke=0, fill=1); c.ellipse(cx + 0.5, cy + 4, cx + 7, cy + 10, stroke=0, fill=1)
    elif nm == '绽放':
        for dx, dy in [(0, 6), (5.5, 2), (3.5, -5), (-3.5, -5), (-5.5, 2)]:
            c.circle(cx + dx, cy + dy, 3.6, stroke=0, fill=1)
        c.setFillColor(YELD); c.circle(cx, cy, 3.2, stroke=0, fill=1)
    else:
        for dx, dy in [(0, 6), (5.5, 2), (3.5, -5), (-3.5, -5), (-5.5, 2)]:
            c.circle(cx + dx, cy + dy, 3.4, stroke=0, fill=1)
        c.setFillColor(HexColor('#FFF3F8')); c.circle(cx, cy, 3, stroke=0, fill=1)
    text(cx - sw(nm, 'SCS', 8.5) / 2, gy + 2, nm, 'SCS', 8.5, INK if nm == '绽放' else SOFT)

# ---------- polaroid: video cases use a real frame (photo.jpg); audio-only cases draw the child from their own words ----------
PHOTO = os.path.join(CASE, 'photo.jpg')
if os.path.exists(PHOTO):
    top = hy - 94
    c.saveState(); c.translate(M + 74, top - 90); c.rotate(-2)
    rrect(-74, -90, 148, 180, 4, fill=CARD, stroke=LINE)
    c.saveState()
    clip = c.beginPath(); clip.rect(-56, -30, 112, 116); c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(PHOTO, -56, -30, 112, 116)
    c.restoreState()
    text(-sw('Toto said...', 'ENB', 11) / 2, -44, 'Toto said...', 'ENB', 11, INK)
    text(-sw('视频里截的这一帧', 'SCS', 8.5) / 2, -59, '视频里截的这一帧', 'SCS', 8.5, INK)
    text(-sw("— that's me!", HAND, 12) / 2, -78, "— that's me!", HAND, 12, HexColor('#B03000'))
    c.restoreState()
else:
    # worked-example drawing (Toto's face, from his own words) — redraw per case from the child's text
    top = hy - 88
    c.saveState(); c.translate(M + 74, top - 90); c.rotate(-2)
    rrect(-74, -90, 148, 180, 4, fill=CARD, stroke=LINE)
    c.setFillColor(HexColor('#EFEDF4')); c.rect(-62, -14, 124, 94, stroke=0, fill=1)
    fcx, fcy, fr = 0, 26, 35
    c.setFillColor(PINK); c.setStrokeColor(INK); c.setLineWidth(1.8)
    c.circle(fcx - fr - 1, fcy + 4, 11.5, stroke=1, fill=1); c.circle(fcx + fr + 1, fcy + 4, 11.5, stroke=1, fill=1)
    c.setFillColor(YEL); c.circle(fcx, fcy, fr, stroke=1, fill=1)
    eye_pos = [(fcx - 20, fcy + 12), (fcx + 20, fcy + 12), (fcx, fcy + 23)]
    for i, (ex, ey) in enumerate(eye_pos):
        for j, bx in enumerate([ex - 8.5, ex + 2.5]):
            c.setStrokeColor(INK if (i + j) % 2 == 0 else YELD); c.setLineWidth(2.6); c.setLineCap(1)
            c.line(bx, ey + 13.5, bx + 6, ey + 11.5)
    for (ex, ey) in eye_pos:
        c.setFillColor(CARD); c.setStrokeColor(INK); c.setLineWidth(1.5); c.circle(ex, ey, 8, stroke=1, fill=1)
        c.setFillColor(BLUE); c.circle(ex, ey, 4.2, stroke=0, fill=1)
        c.setFillColor(INK); c.circle(ex, ey, 2, stroke=0, fill=1)
    c.setFillColor(RED); c.setStrokeColor(INK); c.setLineWidth(1.7)
    c.ellipse(fcx - 18, fcy - 31, fcx + 18, fcy - 12, stroke=1, fill=1)
    c.setFillColor(CARD); c.roundRect(fcx - 9, fcy - 19, 18, 5.4, 1.6, stroke=0, fill=1)
    text(-sw('Toto said...', 'ENB', 11) / 2, -38, 'Toto said...', 'ENB', 11, INK)
    text(-sw('照他原话画的「我」', 'SCS', 8.5) / 2, -53, '照他原话画的「我」', 'SCS', 8.5, INK)
    text(-sw("— that's me!", HAND, 12) / 2, -74, "— that's me!", HAND, 12, HexColor('#B03000'))
    c.restoreState()
# tape
c.saveState(); c.translate(M + 74, top + 2); c.rotate(-3)
c.setFillColor(HexColor('#FFE08A')); c.setStrokeColor(HexColor('#F0D488'))
p = c.beginPath(); p.rect(-26, -7, 52, 14); c.drawPath(p, stroke=0, fill=1)
c.restoreState()

# ---------- speech bubbles (hero, v3) ----------
import json as _json
_peaks = _json.load(open(os.path.join(CASE, 'audio_data.json')))['peaks']
def draw_wave(x, ybase, wdt, t0, t1, colr):
    import math
    b0, b1 = int(t0 / 0.05), int(t1 / 0.05)
    seg = _peaks[b0:b1]
    n = max(8, int(wdt / 5.6))
    c.setStrokeColor(colr); c.setLineWidth(3.2); c.setLineCap(1)
    for i in range(n):
        v = seg[int(i * len(seg) / n)] if seg else 0
        h = 1.8 + v * 11
        xx = x + i * (wdt / n)
        c.line(xx, ybase, xx, ybase + h)

bx0 = M + 162; avail = CW - 162
bubbles = [
    dict(label='打招呼', en='Say hello', colr=BLUEB, dark=HexColor('#1B6FB8'), w=252, dx=0,
         sentence='Hi! I am Toto.', fsize=11.5, t='00:01–00:03', wave=(1.2, 3.0), ww=84,
         listen='点评 · 开口就稳，名字清楚。', tag=None, under=None),
    dict(label='介绍我的脸', en='This is my face', colr=HexColor('#FFD9B3'), dark=HexColor('#B95C08'), w=avail, dx=0,
         sentence='This is my big round yellow face. These are my three big round blue eyes with six big black and yellow eyebrows.',
         fsize=10.5, t='00:03–00:17', wave=(3.1, 17.1), ww=118,
         listen='点评 · 最长一句一口气到底，three 前只停 0.9 秒。', tag=None, under=None),
    dict(label='耳朵、嘴巴和我', en='Ears, mouth and me', colr=GRNB, dark=HexColor('#2F7D3B'), w=avail, dx=0,
         sentence='These are my two big pink ears. This is my big oval red mouth. I love the ugly, silly and scary me!',
         fsize=10.5, t='00:18–00:36', wave=(17.6, 36.3), ww=104,
         listen='点评 · 结尾是自己编的。', tag=None, under=['oval', 'mouth']),
]
by = top
for bb in bubbles:
    bx = bx0 + bb['dx']; bw = bb['w']
    lines = wrap(bb['sentence'], 'ENR', bb['fsize'], bw - 30)
    bh = 39 + len(lines) * 12.5
    rrect(bx, by - bh, bw, bh, 13, fill=bb['colr'])
    c.setFillColor(bb['colr']); p = c.beginPath()
    p.moveTo(bx + 2, by - bh / 2 - 6); p.lineTo(bx - 9, by - bh / 2); p.lineTo(bx + 2, by - bh / 2 + 7); p.close()
    c.drawPath(p, stroke=0, fill=1)
    # time stamp, top-right inside
    text(bx + bw - 12 - sw(bb['t'], 'ENB', 8.5), by - 15, bb['t'], 'ENB', 8.5, bb['dark'])
    # sentences
    ly = by - 24
    undone = list(bb['under'] or [])
    for ln in lines:
        text(bx + 15, ly, ln, 'ENR', bb['fsize'], INK)
        if undone:
            for uw in list(undone):
                if uw in ln:
                    undone.remove(uw)
                    ux = bx + 15 + sw(ln[:ln.index(uw)], 'ENR', bb['fsize'])
                    c.setStrokeColor(DASHR); c.setLineWidth(1.5); c.setDash(3, 2)
                    c.line(ux, ly - 3.5, ux + sw(uw, 'ENR', bb['fsize']), ly - 3.5); c.setDash()
        ly -= 12.5
    # waveform + listening point row
    ry = by - 24 - (len(lines) - 1) * 12.5 - 14
    draw_wave(bx + 15, ry - 5, bb['ww'], bb['wave'][0], bb['wave'][1], bb['dark'])
    lx = bx + 15 + bb['ww'] + 10
    text(lx, ry - 3, '点评', 'SCB', 8.5, bb['dark'])
    text(lx + sw('点评', 'SCB', 8.5) + 4, ry - 3, '· ' + bb['listen'].split('· ', 1)[1], 'SCS', 8.5, bb['dark'])
    # label chip overlapping top edge
    chw = sw(bb['label'], 'SCB', 9) + sw(bb['en'], 'SCS', 8) + 26
    rrect(bx + 14, by - 9.5, chw, 17, 8.5, fill=CARD, stroke=bb['dark'], swd=1.1)
    text(bx + 22, by - 4.5, bb['label'], 'SCB', 9, INK)
    text(bx + 22 + sw(bb['label'], 'SCB', 9) + 6, by - 4.5, bb['en'], 'ENL', 8.5, INK)
    if bb['tag']:
        tw = sw(bb['tag'], 'SCS', 8.5) + 16
        c.saveState(); c.translate(bx + bw - tw - 4, by - bh + 4); c.rotate(-2)
        rrect(0, -8, tw, 17, 8.5, fill=CARD, stroke=LINE)
        text(8, -3.5, bb['tag'], 'SCS', 8.5, HexColor('#C73E1D')); c.restoreState()
    by -= bh + 7

# teacher band data — ONLY a real teacher comment provided for this case; set to None to omit the whole section (never invent one)
TEACHER = dict(hand='Super brave, Toto!', pill='再喊大声点',
               body='最后一句是 Toto 自己编的——讲到这句，声音悄悄小了下去，像有点不好意思。这份敢编敢说，比分数珍贵——下次请他站起来，把最后一句喊出来。')

# ---------- lower half: two different systems + closing ----------
def sumline(y, txt):
    tw9 = sw('总评', 'SCB', 8.5) + 12
    rrect(M, y - 3.5, tw9, 14.5, 7, fill=CARD, stroke=HexColor('#E4572E'), swd=1.0)
    text(M + 6, y, '总评', 'SCB', 8.5, HexColor('#E4572E'))
    text(M + tw9 + 8, y, txt, 'SCB', 9.5, INK)

def sect(y, title, en, note):
    text(M, y, title, 'SCB', 14, INK)
    text(M + sw(title, 'SCB', 14) + 10, y, en, 'ENL', 8.5, INK)
    if note:
        text(W - M - sw(note, 'SCS', 8.5), y, note, 'SCS', 8.5, INK)

def flowers(x, cy, n, s=1.0):
    for i in range(5):
        cx = x + i * 19 * s; filled = i < n
        for a in range(5):
            ang = math.radians(90 + a * 72)
            px, py = cx + 3.3 * s * math.cos(ang), cy + 3.3 * s * math.sin(ang)
            if filled:
                c.setFillColor(HexColor('#E84A3C')); c.circle(px, py, 2.6 * s, stroke=0, fill=1)
            else:
                c.setStrokeColor(HexColor('#D8DEE6')); c.setLineWidth(0.8); c.circle(px, py, 2.6 * s, stroke=1, fill=0)
        c.setFillColor(YEL if filled else HexColor('#E9EDF2')); c.circle(cx, cy, 1.7 * s, stroke=0, fill=1)

STAMP_GREEN = HexColor('#2E9E4F'); STAMP_AMBER = HexColor('#D9930D'); STAMP_RED = HexColor('#C73E1D')
def stamp(x_right, ybase, wd, tilt, dots=5):
    scol = STAMP_GREEN if dots >= 4 else (STAMP_AMBER if dots == 3 else STAMP_RED)
    tw2 = sw(wd, 'SCB', 9.5) + 16
    c.saveState(); c.translate(x_right - tw2, ybase); c.rotate(tilt)
    rrect(0, 0, tw2, 17, 8.5, fill=CARD, stroke=scol, swd=1.1)
    text(8, 4.5, wd, 'SCB', 9.5, scol); c.restoreState()
    return tw2

# ===== A: what he said — dimension strips lead, word wall + exhibits below =====
ay = by - 6
sect(ay, '他说了什么', 'What he said', '参照剑桥 Starters 量规')
sumline(ay - 17, '六句零差错 · 最后一句是自己编的')
sy = ay - 41
anchors = ['Starters · 主题词表', 'Starters · 结构清单', 'Starters · can-do 陈述']
stripw = [('词汇', 4, '用得准'), ('句式与语法', 5, '挺稳当'), ('完整与创意', 5, '有头有尾')]
for i, (nm, n, wd) in enumerate(stripw):
    gx = M + i * 174
    text(gx, sy, nm, 'SCB', 11, INK)
    stamp(gx + sw(nm, 'SCB', 11) + 48 + sw(wd, 'SCB', 9.5) + 16, sy - 8, wd, -2 if i % 2 == 0 else 2, n)
    text(gx, sy - 13, anchors[i], 'SCS', 8.5, INK)
    flowers(gx + 8, sy - 23, n, 0.9)
wy = ay - 88
groups = [('身体', ['face', 'eyes', 'eyebrows', 'ears', 'mouth']),
          ('颜色', ['yellow', 'blue', 'black', 'pink', 'red']),
          ('数字', ['3', '6', '2']),
          ('形容词', ['big', 'round', 'oval', 'ugly', 'silly', 'scary'])]
for gname, words_ in groups:
    text(M, wy, gname, 'SCB', 9, HexColor('#43536B'))
    cx = M + 34
    for w_ in words_:
        fnt = 'ENB' if w_.isdigit() else 'ENR'
        chw2 = sw(w_, fnt, 9) + 13
        rrect(cx, wy - 3.5, chw2, 14.5, 7, fill=CARD, stroke=HexColor('#C4D2DE'), swd=0.9)
        text(cx + 6.5, wy, w_, fnt, 9, INK)
        cx += chw2 + 5
    wy -= 21.5
ex = M + 292; ew = CW - 292
ey = ay - 86
text(ex, ey, '单数复数，分得清', 'SCB', 10, INK)
x2 = ex
text(x2, ey - 15, 'this', 'ENB', 10, BLUE); x2 += sw('this', 'ENB', 10)
text(x2, ey - 15, ' is my face · ', 'ENR', 10, INK); x2 += sw(' is my face · ', 'ENR', 10)
text(x2, ey - 15, 'these', 'ENB', 10, BLUE); x2 += sw('these', 'ENB', 10)
text(x2, ey - 15, ' are my eyes', 'ENR', 10, INK)
ey -= 34
text(ex, ey, '形容词会排队', 'SCB', 10, INK)
seg = [('big', '大小'), ('round', '形状'), ('yellow', '颜色')]
x2 = ex
for w_, lab in seg:
    text(x2, ey - 16, w_, 'ENB', 10, INK)
    text(x2 + 1, ey - 27, lab, 'SCS', 7.5, HexColor('#43536B'))
    x2 += sw(w_, 'ENB', 10)
    if w_ != 'yellow':
        text(x2 + 2, ey - 16, '·', 'ENB', 10, INK); x2 += sw('·', 'ENB', 10) + 4
ey -= 44
text(ex, ey, '最后一句，自己编的', 'SCB', 10, INK)
text(ex, ey - 15, '“ugly, silly and scary”', 'ENB', 10, HexColor('#C73E1D'))

# ===== B: how he sounded — melody line + three columns =====
ay2 = ay - 198 if TEACHER else ay - 206
sect(ay2, '他的声音怎么样', 'How he sounded', '对标 IELTS 口语标准')
sumline(ay2 - 17, '每句说完都稳稳落地 · 想词才停，句间很干脆')
# ===== his voice, measured two ways on one timeline: loudness (bars) + pitch (line); orange bands = pauses =====
import json as _j2
_f0 = _j2.load(open(os.path.join(CASE, 'audio_data.json')))['f0']
def fx(t): return M + t / 37.48 * CW
for pc, dur in [(8.04, 0.9), (20.64, 1.2), (25.8, 2.8)]:
    c.setFillColor(HexColor('#FDEEE3'))
    c.rect(fx(pc - dur / 2), ay2 - 71, (fx(pc + dur / 2) - fx(pc - dur / 2)), 38, stroke=0, fill=1)
text(M, ay2 - 31, '声音大小', 'SCS', 8.5, HexColor('#43536B'))
wyA = ay2 - 47
c.setStrokeColor(BLUE); c.setLineWidth(2.0); c.setLineCap(1)
_nn = len(_peaks)
for i, v in enumerate(_peaks):
    xx = M + i / _nn * CW
    c.line(xx, wyA, xx, wyA + 1.5 + v * 12.5)
text(M, ay2 - 55, '声音高低', 'SCS', 8.5, HexColor('#43536B'))
fy0 = ay2 - 71
def fy(v):
    import math as _m
    return fy0 + (_m.log2(min(v, 420)) - _m.log2(150)) / (_m.log2(420) - _m.log2(150)) * 14
_raw = [v if (v and v > 0) else 0 for v in _f0]
i = 0
while i < len(_raw):
    if _raw[i] == 0:
        j = i
        while j < len(_raw) and _raw[j] == 0: j += 1
        if 0 < i and j < len(_raw) and j - i <= 4:
            a, b = _raw[i - 1], _raw[j]
            for k in range(i, j): _raw[k] = a + (b - a) * (k - i + 1) / (j - i + 1)
        i = j
    else:
        i += 1
_fs = []
_run = []
def _flush():
    global _run
    med = []
    for j, v in enumerate(_run):
        lo = max(0, j - 2); hi = min(len(_run), j + 3)
        med.append(sorted(_run[lo:hi])[len(_run[lo:hi]) // 2])
    for j, v in enumerate(med):
        lo = max(0, j - 1); hi = min(len(med), j + 2)
        _fs.append(sum(med[lo:hi]) / (hi - lo))
    _run = []
for v in _raw:
    if v > 0: _run.append(v)
    else:
        _flush(); _fs.append(0)
_flush()
c.setStrokeColor(BLUE); c.setLineWidth(1.4); c.setLineCap(1)
p = c.beginPath(); pen = False
for i, v in enumerate(_fs):
    if v and v > 0:
        xx, yy2 = fx(i * 0.05), fy(v)
        if pen: p.lineTo(xx, yy2)
        else: p.moveTo(xx, yy2); pen = True
    else:
        pen = False
c.drawPath(p, stroke=1, fill=0)
for pc, lab in [(8.04, '0.9 秒'), (20.64, '1.2 秒'), (25.8, '2.8 秒')]:
    text(fx(pc) - sw(lab, 'SCS', 8.5) / 2, ay2 - 82, lab, 'SCS', 8.5, HexColor('#C73E1D'))
cols = [
    ('发音准确度', 'IELTS · Pronunciation', 4, '很清楚',
     '清晰度实测 17.9 dB，\n小关卡：词尾 th、v 音——\nmouth 成了 mouse，oval 没听出。'),
    ('流利度', 'IELTS · Fluency and Coherence', 4, '很顺溜',
     '没有「呃、啊」，也不重说。\n想词的停顿都躲在句中，\n句间很干脆。'),
    ('语调与重音', 'IELTS · Pronunciation', 4, '有起伏',
     '句尾 6/6 全降调，\n跨度 12.9 个半音超一个八度。\n遗憾：重音还没站出来。'),
]
cy0 = ay2 - 94
for i, (nm, en, dots, wd, desc) in enumerate(cols):
    gx = M + i * 174
    text(gx, cy0, nm, 'SCB', 11, INK)
    stamp(gx + sw(nm, 'SCB', 11) + 48 + sw(wd, 'SCB', 9.5) + 16, cy0 - 8, wd, -2 if i % 2 == 0 else 2, dots)
    text(gx, cy0 - 13, en, 'ENL', 8.5, INK)
    flowers(gx + 8, cy0 - 26, dots, 0.9)
    para(gx, cy0 - 41 if TEACHER else cy0 - 44, desc, 'SCS', 9.5, INK, maxw=163, leading=13)

# ===== closing: teacher band + games =====
if TEACHER:
    ty = cy0 - 80 if TEACHER else cy0 - 86
    text(M, ty, '老师的话', 'SCB', 14, INK)
    text(M + sw('老师的话', 'SCB', 14) + 8, ty, 'From the teacher', 'ENL', 8.5, INK)
    hb = ty - 33
    c.saveState(); c.translate(M, hb); c.rotate(-1.5)
    text(0, 0, TEACHER['hand'], HAND, 19, INK)
    c.setStrokeColor(HexColor('#E4572E')); c.setLineWidth(2.4); c.setLineCap(1)
    c.line(2, -5, sw(TEACHER['hand'], HAND, 19) - 2, -4); c.restoreState()
    pw = sw(TEACHER['pill'], 'SCB', 8.5) + 12
    rrect(M + 168, hb - 7, pw, 15, 7.5, fill=HexColor('#E4572E'))
    text(M + 174, hb - 2.5, TEACHER['pill'], 'SCB', 8.5, CARD)
    para(M + 246, hb + 3, TEACHER['body'], 'SCS', 9.5, INK, maxw=CW - 246, leading=12.5)
    gy = ty - 50 if TEACHER else ty - 58
else:
    gy = cy0 - 92
c.restoreState()
text(M, gy, '回家一起玩', 'SCB', 14, INK)
text(M + sw('回家一起玩', 'SCB', 14) + 8, gy, 'Play at home', 'ENL', 8.5, INK)
text(W - M - sw('玩过一项，就在方框里打个勾吧。', 'SCS', 8.5), gy, '玩过一项，就在方框里打个勾吧。', 'SCS', 8.5, INK)
games = [
    ('小舌头探险', '对着镜子露一点舌尖说 mouth、teeth、three——专练词尾 th。'),
    ('蜜蜂 v 嗡嗡', '上牙轻咬下唇说 oval、love、five，摸喉咙，有震动 v 就出来了。'),
    ('重音拍手 + 结尾喊话', 'YEL-low、SIL-ly 第一下重拍、第二下轻带；站起来喊出结尾句。'),
]
gyy = gy - 22
for i, (nm, desc) in enumerate(games):
    gx = M + i * 174
    rrect(gx, gyy - 1, 13, 13, 3.5, stroke=INK, swd=1.2)
    text(gx + 20, gyy + 1, nm, 'SCB', 10, INK)
    para(gx + 20, gyy - 12, desc, 'SCS', 9.5, INK, maxw=143, leading=13)


c.showPage(); c.save()
print('saved', OUT, 'display font:', DISP)
