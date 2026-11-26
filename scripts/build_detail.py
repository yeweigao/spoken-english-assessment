#!/usr/bin/env python3
"""Case-driven DETAILED report: two A4 pages (front growth record + back benchmark map),
all per-case content read from the case's case.json `detail` block — no editing of this file per child.

Run from the case directory (case.json, photo.jpg, audio_data.json, analysis.json,
sound_scores.json sit beside it):
    python3 scripts/build_detail.py [case.json]
"""
import os, sys, json, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfWriter, PdfReader

W, H = A4
BASE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))
CASE_FILE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'case.json')
if not os.path.isfile(CASE_FILE):
    raise SystemExit(f'找不到 {CASE_FILE}：详细版的案例内容写在 case.json 的 detail 段里')
CASE = os.path.dirname(CASE_FILE)

def reg(name, fname, fallback=None):
    p = os.path.join(FONTDIR, fname)
    if os.path.exists(p):
        pdfmetrics.registerFont(TTFont(name, p)); return name
    if fallback: return fallback
    raise SystemExit('missing font ' + fname)

pdfmetrics.registerFont(TTFont('SC', os.path.join(FONTDIR, 'NotoSC-Regular.ttf')))
reg('SCB', 'NotoSC-SemiB.ttf', 'SC')
reg('SCS', 'NotoSC-Regular.ttf', 'SC')
_enl = os.path.join(FONTDIR, 'Inter-Light.ttf')
pdfmetrics.registerFont(TTFont('ENL', _enl if os.path.exists(_enl) else os.path.join(FONTDIR, 'Inter-Reg.ttf')))
reg('ENR', 'Inter-Reg.ttf', 'SCS')
reg('ENB', 'Inter-BoldF.ttf', 'SCS')
DISP = reg('ZCOOL', 'ZCOOLKuaiLe.ttf', 'SCB')
HAND = reg('HAND', 'PatrickHand.ttf', 'ENB')

INK = HexColor('#000000'); SOFT = HexColor('#1A1A1A'); CARD = HexColor('#FFFFFF')
YEL = HexColor('#FFC93C'); YELD = HexColor('#E8A90C'); RED = HexColor('#E4572E')
GREEN = HexColor('#3D9B50'); BLUE = HexColor('#2E7CD6'); LINE = HexColor('#E8E2D2')
PALETTE = {
    'blue': (HexColor('#AEDCF7'), HexColor('#1B6FB8')),
    'orange': (HexColor('#FFD9B3'), HexColor('#B95C08')),
    'green': (HexColor('#C6E9C2'), HexColor('#2F7D3B')),
    'pink': (HexColor('#FFD9E6'), HexColor('#B04570')),
}
STAGE_COL = {'萌芽': HexColor('#B08968'), '成长': GREEN, '绽放': RED, '闪耀': HexColor('#E79FBF')}

case = json.load(open(CASE_FILE, encoding='utf-8'))
detail = case.get('detail')
if not detail:
    raise SystemExit('case.json 里没有 detail 段：详细版的文字内容（气泡、词卡、教老师的话、对标证据）都写在里面')
peaks = json.load(open(os.path.join(CASE, 'audio_data.json')))['peaks']
f0 = json.load(open(os.path.join(CASE, 'audio_data.json'))).get('f0') or []
anal = json.load(open(os.path.join(CASE, 'analysis.json'))) if os.path.isfile(os.path.join(CASE, 'analysis.json')) else {}
scores = json.load(open(os.path.join(CASE, 'sound_scores.json'))) if os.path.isfile(os.path.join(CASE, 'sound_scores.json')) else {}
TOTAL = len(peaks) * 0.05
SECS = case.get('secs') or (f'{int(round(TOTAL))} 秒' if TOTAL < 60 else f'{int(TOTAL // 60)} 分 {int(TOTAL % 60)} 秒')

# ---------------------------------------------------------------- helpers
def sw(t, f, s): return pdfmetrics.stringWidth(t, f, s)
def wrap(s, font, size, maxw):
    toks, i = [], 0
    while i < len(s):
        if s[i] == ' ':
            toks.append(' '); i += 1
        elif ord(s[i]) < 128:
            j = i
            while j < len(s) and ord(s[j]) < 128 and s[j] != ' ': j += 1
            toks.append(s[i:j]); i = j
        else:
            toks.append(s[i]); i += 1
    lines, cur = [], ''
    for t in toks:
        if sw(cur + t, font, size) <= maxw: cur += t
        else: lines.append(cur.rstrip()); cur = t.lstrip()
    if cur.strip(): lines.append(cur.rstrip())
    return lines

def make_front(c, d):
    def text(x, y, s, f='SCS', size=10, color=INK):
        c.setFont(f, size); c.setFillColor(color); c.drawString(x, y, s)
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
    def stamp(x_right, ybase, wd, tilt, dots=5):
        scol = HexColor('#2E9E4F') if dots >= 4 else (HexColor('#D9930D') if dots == 3 else HexColor('#C73E1D'))
        tw = sw(wd, 'SCB', 9.5) + 16
        c.saveState(); c.translate(x_right - tw, ybase); c.rotate(tilt)
        rrect(0, 0, tw, 17, 8.5, fill=CARD, stroke=scol, swd=1.1)
        text(8, 4.5, wd, 'SCB', 9.5, scol); c.restoreState()
        return tw
    def sumline(y, txt):
        tw = sw('总评', 'SCB', 8.5) + 12
        rrect(M, y - 3.5, tw, 14.5, 7, fill=CARD, stroke=RED, swd=1.0)
        text(M + 6, y, '总评', 'SCB', 8.5, RED)
        text(M + tw + 8, y, txt, 'SCB', 9.5, INK)
    def sect(y, title, en, note):
        text(M, y, title, 'SCB', 14, INK)
        text(M + sw(title, 'SCB', 14) + 10, y, en, 'ENL', 8.5, INK)
        if note: text(W - M - sw(note, 'SCS', 8.5), y, note, 'SCS', 8.5, INK)
    def draw_wave(x, ybase, wdt, t0, t1, colr):
        b0, b1 = int(t0 / 0.05), int(t1 / 0.05)
        seg = peaks[b0:b1]
        n = max(8, int(wdt / 5.6))
        c.setStrokeColor(colr); c.setLineWidth(3.2); c.setLineCap(1)
        for i in range(n):
            v = seg[int(i * len(seg) / n)] if seg else 0
            c.line(x + i * (wdt / n), ybase, x + i * (wdt / n), ybase + 1.8 + v * 11)

    M = 34; CW = W - 2 * M
    c.setFillColor(CARD); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.saveState(); c.translate(0, 12)

    c.saveState(); c.translate(W - 120, H - 30); c.rotate(-4)
    rrect(-160, -58, 330, 120, 34, fill=YEL); c.restoreState()

    hy = H - 56
    text(M + 2, hy, detail.get('season', '2026 秋 · 口语测评'), 'SCS', 8.5, SOFT)
    text(M, hy - 34, '英语口语成长记录', DISP, 30, INK)
    text(M + 2, hy - 52, 'My English Speaking Report', 'ENB', 11, SOFT)
    _tlab = case.get('topic_label') or ('篇目' if case.get('task') == 'read' else '话题')
    text(M + 2, hy - 74, f"姓名 {case['name']}  ·  {_tlab} {case['topic']}  ·  {case['date']}  ·  {SECS}", 'SCS', 9.5, INK)

    stage = detail.get('stage', '绽放')
    gx, gy, gw, gh = W - M - 236, hy - 66, 236, 62
    rrect(gx + 3, gy - 5, gw, gh, 14, fill=HexColor('#F3E3B3'))
    rrect(gx, gy, gw, gh, 14, fill=CARD)
    text(gx + 14, gy + 42, f"这一次，{case['name']} 长到了这里", 'SCB', 11, INK)
    for i, nm in enumerate(('萌芽', '成长', '绽放', '闪耀')):
        col = STAGE_COL[nm]; cx = gx + 34 + i * 56; cy = gy + 22
        on = nm == stage
        if on: c.setFillColor(YEL); c.circle(cx, cy, 13, stroke=0, fill=1)
        c.setFillColor(col)
        if nm == '萌芽': c.ellipse(cx - 6, cy - 3, cx + 6, cy + 4, stroke=0, fill=1)
        elif nm == '成长':
            c.setLineWidth(2); c.setStrokeColor(col); c.line(cx, cy - 6, cx, cy + 5)
            c.ellipse(cx - 7, cy + 2, cx - 0.5, cy + 8, stroke=0, fill=1); c.ellipse(cx + 0.5, cy + 4, cx + 7, cy + 10, stroke=0, fill=1)
        else:
            for dx, dy in [(0, 6), (5.5, 2), (3.5, -5), (-3.5, -5), (-5.5, 2)]:
                c.circle(cx + dx, cy + dy, 3.6 if nm == '绽放' else 3.4, stroke=0, fill=1)
            c.setFillColor(YELD if nm == '绽放' else HexColor('#FFF3F8')); c.circle(cx, cy, 3.2 if nm == '绽放' else 3, stroke=0, fill=1)
        text(cx - sw(nm, 'SCS', 8.5) / 2, gy + 2, nm, 'SCS', 8.5, INK if on else SOFT)

    # polaroid
    PHOTO = os.path.join(CASE, case.get('photo') or 'photo.jpg')
    top = hy - 94
    c.saveState(); c.translate(M + 74, top - 90); c.rotate(-2)
    rrect(-74, -90, 148, 180, 4, fill=CARD, stroke=LINE)
    c.saveState(); clip = c.beginPath(); clip.rect(-56, -30, 112, 116); c.clipPath(clip, stroke=0, fill=0)
    if os.path.exists(PHOTO): c.drawImage(PHOTO, -56, -30, 112, 116)
    else:
        c.setFillColor(HexColor('#EFEDF4')); c.rect(-56, -30, 112, 116, stroke=0, fill=1)
        text(-sw('photo missing', 'ENB', 10) / 2, 40, 'photo missing', 'ENB', 10, RED)
    c.restoreState()
    text(-sw(f"{case['name']} said...", 'ENB', 11) / 2, -44, f"{case['name']} said...", 'ENB', 11, INK)
    text(-sw(detail.get('polaroid_caption', '视频里截的这一帧'), 'SCS', 8.5) / 2, -59, detail.get('polaroid_caption', '视频里截的这一帧'), 'SCS', 8.5, INK)
    text(-sw("— that's me!", HAND, 12) / 2, -78, "— that's me!", HAND, 12, HexColor('#B03000'))
    c.restoreState()
    c.saveState(); c.translate(M + 74, top + 2); c.rotate(-3)
    c.setFillColor(HexColor('#FFE08A')); c.setStrokeColor(HexColor('#F0D488'))
    c.rect(-26, -7, 52, 14, stroke=0, fill=1); c.restoreState()

    # bubbles
    bx0 = M + 162; avail = CW - 162
    by = top
    for bb in detail.get('bubbles', []):
        bw = bb.get('w') or avail
        fill, dark = PALETTE.get(bb.get('color', 'blue'), PALETTE['blue'])
        fsize = bb.get('fsize', 10.5)
        lines = wrap(bb['sentence'], 'ENR', fsize, bw - 30)
        bh = 34 + len(lines) * 11.5
        rrect(bx0, by - bh, bw, bh, 13, fill=fill)
        c.setFillColor(fill); p = c.beginPath()
        p.moveTo(bx0 + 2, by - bh / 2 - 6); p.lineTo(bx0 - 9, by - bh / 2); p.lineTo(bx0 + 2, by - bh / 2 + 7); p.close()
        c.drawPath(p, stroke=0, fill=1)
        text(bx0 + bw - 12 - sw(bb['t'], 'ENB', 8.5), by - 15, bb['t'], 'ENB', 8.5, dark)
        ly = by - 24
        undone = list(bb.get('under') or [])
        for ln in lines:
            text(bx0 + 15, ly, ln, 'ENR', fsize, INK)
            for uw in list(undone):
                if uw in ln:
                    undone.remove(uw)
                    ux = bx0 + 15 + sw(ln[:ln.index(uw)], 'ENR', fsize)
                    c.setStrokeColor(HexColor('#E4572E')); c.setLineWidth(1.5); c.setDash(3, 2)
                    c.line(ux, ly - 3.5, ux + sw(uw, 'ENR', fsize), ly - 3.5); c.setDash()
            ly -= 11.5
        ry = by - 22 - (len(lines) - 1) * 11.5 - 12
        draw_wave(bx0 + 15, ry - 5, bb.get('ww', 84), bb['start'], bb['end'], dark)
        lx = bx0 + 15 + bb.get('ww', 84) + 10
        text(lx, ry - 3, '点评', 'SCB', 8.5, dark)
        text(lx + sw('点评', 'SCB', 8.5) + 4, ry - 3, '· ' + bb.get('comment', ''), 'SCS', 8.5, dark)
        chw = sw(bb['label'], 'SCB', 9) + sw(bb.get('en', ''), 'SCS', 8) + 26
        rrect(bx0 + 14, by - 9.5, chw, 17, 8.5, fill=CARD, stroke=dark, swd=1.1)
        text(bx0 + 22, by - 4.5, bb['label'], 'SCB', 9, INK)
        text(bx0 + 22 + sw(bb['label'], 'SCB', 9) + 6, by - 4.5, bb.get('en', ''), 'ENL', 8.5, INK)
        by -= bh + 7

    # content
    content = detail['content']
    ay = min(by, top - 192) - 10
    sect(ay, '他说了什么', 'What he said', '参照剑桥 Starters 量规')
    sumline(ay - 17, content['summary'])
    sy = ay - 41
    anchors = ['Starters · 主题词表', 'Starters · 结构清单', 'Starters · can-do 陈述']
    for i, (nm, n, wd) in enumerate(content['strips']):
        gx2 = M + i * 174
        text(gx2, sy, nm, 'SCB', 11, INK)
        stamp(gx2 + sw(nm, 'SCB', 11) + 48 + sw(wd, 'SCB', 9.5) + 16, sy - 8, wd, -2 if i % 2 == 0 else 2, n)
        text(gx2, sy - 13, anchors[i], 'SCS', 8.5, INK)
        flowers(gx2 + 8, sy - 23, n, 0.9)
    wy = ay - 86
    for gname, words_ in content['word_groups']:
        text(M, wy, gname, 'SCB', 9, HexColor('#43536B'))
        cx = M + 34
        for w_ in words_:
            fnt = 'ENB' if w_.isdigit() else 'ENR'
            chw2 = sw(w_, fnt, 9) + 13
            rrect(cx, wy - 3.5, chw2, 14.5, 7, fill=CARD, stroke=HexColor('#C4D2DE'), swd=0.9)
            text(cx + 6.5, wy, w_, fnt, 9, INK)
            cx += chw2 + 5
        wy -= 18
    ex = M + 292; ey = ay - 86
    for exi in content['exhibits']:
        text(ex, ey, exi['title'], 'SCB', 10, INK)
        yy2 = ey - 15
        for seg in exi['lines']:
            text(ex, yy2, seg, 'ENB', 10, HexColor('#C73E1D') if seg.startswith('“') else INK); yy2 -= 13
        ey = yy2 - 14

    # sound section
    sound = detail['sound']
    ay2 = ey - 12
    sect(ay2, '她的声音怎么样', 'How she sounded', '对标 IELTS 口语标准')
    sumline(ay2 - 17, sound['summary'])
    PLOT0 = M + 56
    def fx(t): return PLOT0 + max(0.0, min(t, TOTAL)) / TOTAL * (CW - 56)
    band_top = ay2 - 64
    gaps = []
    sents = anal.get('sentences') or []
    for a_, b_ in zip(sents, sents[1:]):
        g = b_['start'] - a_['end']
        if g >= 0.6: gaps.append((a_['end'] + g / 2, g))
    for pc, dur in gaps:
        c.setFillColor(HexColor('#FDEEE3'))
        c.rect(fx(pc - dur / 2), band_top, fx(pc + dur / 2) - fx(pc - dur / 2), 34, stroke=0, fill=1)
    text(M, ay2 - 28, '声音大小', 'SCS', 8.5, HexColor('#43536B'))
    wyA = ay2 - 42
    c.setStrokeColor(BLUE); c.setLineWidth(2.0); c.setLineCap(1)
    for i, v in enumerate(peaks):
        xx = PLOT0 + i / len(peaks) * (CW - 56)
        c.line(xx, wyA, xx, wyA + 1.5 + v * 12.5)
    text(M, ay2 - 48, '声音高低', 'SCS', 8.5, HexColor('#43536B'))
    fy0 = band_top
    def fy(v):
        return fy0 + (math.log2(min(v, 420)) - math.log2(150)) / (math.log2(420) - math.log2(150)) * 14
    raw = [v if (v and v > 0) else 0 for v in f0]
    i = 0
    while i < len(raw):
        if raw[i] == 0:
            j = i
            while j < len(raw) and raw[j] == 0: j += 1
            if 0 < i and j < len(raw) and j - i <= 4:
                a_, b_ = raw[i - 1], raw[j]
                for k in range(i, j): raw[k] = a_ + (b_ - a_) * (k - i + 1) / (j - i + 1)
            i = j
        else: i += 1
    c.setStrokeColor(BLUE); c.setLineWidth(1.4); c.setLineCap(1)
    p = c.beginPath(); pen = False
    for i, v in enumerate(raw):
        if v > 0:
            xx, yy2 = fx(i * 0.05), fy(v)
            p.lineTo(xx, yy2) if pen else p.moveTo(xx, yy2); pen = True
        else: pen = False
    c.drawPath(p, stroke=1, fill=0)
    for pc, dur in gaps:
        lab = (f'{dur:.1f} 秒' if '音高' else '')
        text(fx(pc) - sw(lab, 'SCS', 8.5) / 2, ay2 - 76, lab, 'SCS', 8.5, HexColor('#C73E1D'))
    cy0 = ay2 - 96
    for i, (nm, en, dots, wd, desc) in enumerate(sound['cols']):
        gx3 = M + i * 174
        text(gx3, cy0, nm, 'SCB', 11, INK)
        stamp(gx3 + sw(nm, 'SCB', 11) + 48 + sw(wd, 'SCB', 9.5) + 16, cy0 - 8, wd, -2 if i % 2 == 0 else 2, dots)
        text(gx3, cy0 - 13, en, 'ENL', 8.5, INK)
        flowers(gx3 + 8, cy0 - 26, dots, 0.9)
        para(gx3, cy0 - 41, desc, 'SCS', 9.5, INK, maxw=163, leading=12.5)

    # teacher + games
    tch = detail.get('teacher')
    cy = cy0 - 90
    if tch:
        text(M, cy, '老师的话', 'SCB', 14, INK)
        text(M + sw('老师的话', 'SCB', 14) + 8, cy, 'From the teacher', 'ENL', 8.5, INK)
        hb = cy - 33
        c.saveState(); c.translate(M, hb); c.rotate(-1.5)
        text(0, 0, tch['hand'], HAND, 19, INK)
        c.setStrokeColor(HexColor('#E4572E')); c.setLineWidth(2.4); c.setLineCap(1)
        c.line(2, -5, sw(tch['hand'], HAND, 19) - 2, -4); c.restoreState()
        pw = sw(tch['pill'], 'SCB', 8.5) + 12
        rrect(M + 168, hb - 7, pw, 15, 7.5, fill=HexColor('#E4572E'))
        text(M + 174, hb - 2.5, tch['pill'], 'SCB', 8.5, CARD)
        para(M + 246, hb + 3, tch['body'], 'SCS', 9.5, INK, maxw=CW - 246, leading=12.5)
        gy2 = cy - 64
    else:
        gy2 = cy + 8
    text(M, gy2, '回家一起玩', 'SCB', 14, INK)
    text(M + sw('回家一起玩', 'SCB', 14) + 8, gy2, 'Play at home', 'ENL', 8.5, INK)
    text(W - M - sw('玩过一项，就在方框里打个勾吧。', 'SCS', 8.5), gy2, '玩过一项，就在方框里打个勾吧。', 'SCS', 8.5, INK)
    gyy = gy2 - 22
    for i, (nm, desc) in enumerate(case['games'][:3]):
        gx4 = M + i * 174
        rrect(gx4, gyy - 1, 13, 13, 3.5, stroke=INK, swd=1.2)
        text(gx4 + 20, gyy + 1, nm, 'SCB', 10, INK)
        para(gx4 + 20, gyy - 12, desc, 'SCS', 9.5, INK, maxw=143, leading=12.5)
    c.restoreState(); c.showPage(); c.save()

# ---------------------------------------------------------------- back page
def build_back(d, out):
    INKb = HexColor('#111111'); GRAY = HexColor('#555555'); HAIR = HexColor('#9AA4AD'); REDb = HexColor('#E30613')
    def st(name, font, size, lead, color=INKb, **kw):
        return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead, textColor=color, **kw)
    sKick = st('k', 'ENB', 8.5, 10.5); sTitle = st('t', 'SCB', 25, 28)
    sMeta = st('m', 'SCS', 8.5, 11.5, GRAY, alignment=2); sIntro = st('i', 'SCS', 9.5, 13.5)
    sSec = st('sec', 'SCB', 11, 14); sH = st('h', 'SCB', 7.5, 10, GRAY)
    sDim = st('dim', 'SCB', 10, 12.5); sC = st('c', 'SCS', 8.5, 12)
    sNote = st('n', 'SCS', 8.5, 12.5, GRAY); sLab = st('lab', 'SCS', 8, 10.5, GRAY)
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=42, rightMargin=42, topMargin=36, bottomMargin=24,
                            title='维度对标表（报告背面）')
    E = []
    head = Table([
        [Paragraph('<font color="#E30613">■</font>  SPEAKING ASSESSMENT — BENCHMARK MAP', sKick), Paragraph('', sMeta)],
        [Paragraph('维度对标表', sTitle), Paragraph(detail['back']['meta'], sMeta)],
    ], colWidths=[340, 171])
    head.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                              ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                              ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))
    E.append(head); E.append(Spacer(1, 7))
    rule = Table([['']], colWidths=[511], rowHeights=[2.6])
    rule.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), INKb),
                              ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                              ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    E.append(rule); E.append(Spacer(1, 9))
    E.append(Paragraph(detail['back']['position'], sIntro)); E.append(Spacer(1, 10))
    data = [[Paragraph('维度 DIMENSION', sH), Paragraph('IELTS 口语标准', sH),
             Paragraph('剑桥 STARTERS / CEFR 参照', sH), Paragraph('本报告的证据 EVIDENCE', sH)]]
    for num, dim, ielts, ref, ev in detail['back']['rows']:
        data.append([Paragraph(f'<font color="#E30613">{num}</font><br/><br/>{dim}', sDim),
                     Paragraph(ielts, sC), Paragraph(ref, sC), Paragraph(ev, sC)])
    t = Table(data, colWidths=[66, 100, 158, 187], repeatRows=1)
    t.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1.6, INKb), ('LINEBELOW', (0, 0), (-1, 0), 0.7, INKb),
        ('LINEBELOW', (0, 1), (-1, -2), 0.45, HAIR), ('LINEBELOW', (0, -1), (-1, -1), 1.6, INKb),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    E.append(t); E.append(Spacer(1, 12))
    E.append(Paragraph('本次录音的技术指标（原生音频实测）', sSec)); E.append(Spacer(1, 4))
    grid2 = []
    cells = detail['back']['indicators']
    for i in range(0, 6, 3):
        row = []
        for big, unit, lab in cells[i:i + 3]:
            row.append(Paragraph(f'<font face="ENB" size="13">{big}</font> <font face="SCS" size="8.5">{unit}</font>'
                                 f'<br/><font color="#555555" size="8.5">{lab}</font>', sC))
        grid2.append(row)
    gt = Table(grid2, colWidths=[170, 170, 171])
    gt.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1.6, INKb), ('LINEBELOW', (0, 0), (-1, -1), 0.7, INKb) if False else ('LINEBELOW', (0, 0), (-1, 0), 0.7, INKb),
        ('LINEBELOW', (0, -1), (-1, -1), 1.6, INKb),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    E.append(gt); E.append(Spacer(1, 10))
    E.append(Paragraph(detail['back']['method'], sNote))
    doc.build(E)

front_pdf = os.path.join(CASE, '_detail-front.pdf')
back_pdf = os.path.join(CASE, '_detail-back.pdf')
c = canvas.Canvas(front_pdf, pagesize=A4, initialFontName='SCS', initialFontSize=10)
make_front(c, case)
build_back(case, back_pdf)
w = PdfWriter(); w.append(PdfReader(front_pdf)); w.append(PdfReader(back_pdf))
out = os.path.join(CASE, case.get('detail_out', 'report.pdf'))
with open(out, 'wb') as fh: w.write(fh)
print('saved', os.path.basename(out), '(两页：正面成长记录 + 背面对标表)')
