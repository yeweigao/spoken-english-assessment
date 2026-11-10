#!/usr/bin/env python3
"""Report SIMPLE page (one A4 page for parents — the quick-read companion
to the two-page detailed report; same measurements, same flower counts).

Order follows the normal assessment-report genre: identity -> six-dimension
radar with a plain-language overview -> per-dimension readings -> next steps
(goal + home games) -> appendix: the full transcript. Design law (full spec
in references/type-system.md, section 简版一页):
- ONE pale-cream field over the whole top, ending in a drawn wave with two
  clouds on the seam; ONE strong yellow (frame + the ray sun, #FFD65A, built
  as a flat disc with twelve pill rays, centre off the top-right corner);
  the child's photo print sits on the sun (cover-fit: crop, never stretch).
- Radar data in marigold orange; red is reserved for earned flowers, which
  appear ONLY in the per-dimension readings. No overall grade line and no
  invented framework tiers: quality lives in the flowers and the readings.
- Say each thing once: the radar carries dimension names only (the verdict
  word lives in the readings), the overview speaks in conclusions without
  measurements, the readings carry the evidence. validate() enforces this.
- Illustrations are all hand-drawn flat vector shapes in one family (rounded,
  matte, no emoji, no gloss): sun, clouds, flowers, the bottom landscape.
Run with the case's case.json (default ./case.json); the photo and audio_data.json sit beside it.
Nothing in this script is edited per child."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, math, re, json

W, H = A4
BASE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))

def reg(name, fname, fallback=None):
    p = os.path.join(FONTDIR, fname)
    if os.path.exists(p):
        pdfmetrics.registerFont(TTFont(name, p)); return name
    if fallback: return fallback
    raise SystemExit('missing font ' + fname)

pdfmetrics.registerFont(TTFont('SC', os.path.join(FONTDIR, 'NotoSC-Regular.ttf')))
reg('SCB', 'NotoSC-SemiB.ttf', 'SC')
reg('SCS', 'NotoSC-Regular.ttf', 'SC')
reg('ENB', 'Inter-BoldF.ttf', 'SC')
reg('ENR', 'Inter-Reg.ttf', 'SC')
DISP = reg('ZCOOL', 'ZCOOLKuaiLe.ttf', 'SCB')

INK = HexColor('#141414'); RED = HexColor('#E4572E')
GREY = HexColor('#6B7280'); FAINT = HexColor('#C9D2DD')
CARD = HexColor('#FFFFFF'); YEL = HexColor('#FFC93C')

def sw(t, f, s): return pdfmetrics.stringWidth(t, f, s)
CLOSE = '，。、；：！？）」』”’》〕…'
OPEN = '（「『“‘《〔'
PUNCT = CLOSE + OPEN + ' '
try:                                   # word boundaries for Chinese, so 「这样」「不慌不忙」 aren't cut in two
    import jieba; jieba.setLogLevel(60)
    def _cjk_words(run): return list(jieba.cut(run, HMM=False))
except ImportError:                    # without jieba every character is its own token
    def _cjk_words(run): return list(run)

def _tokens(s):
    """Latin words stay whole; a short quoted group like 「嗯、啊」 stays whole; Chinese is cut into words."""
    out, i, run = [], 0, ''
    def flush():
        nonlocal run
        if run: out.extend(_cjk_words(run)); run = ''
    while i < len(s):
        ch = s[i]
        if ch == '「':
            k = s.find('」', i)
            if 0 < k - i <= 7:
                flush(); out.append(s[i:k + 1]); i = k + 1; continue
        if ch == ' ':
            flush(); out.append(' '); i += 1
        elif ch.isascii() and (ch.isalnum() or ch in ".'-?!,"):
            flush(); j = i
            while j < len(s) and s[j].isascii() and (s[j].isalnum() or s[j] in ".'-?!,"): j += 1
            if s[i:j].replace('.', '').isdigit() and s[j:j + 1] == ' ' and j + 1 < len(s) and '\u4e00' <= s[j + 1] <= '\u9fff':
                j += 2                         # a number keeps its unit: 「1.2 秒」 never splits
            out.append(s[i:j]); i = j
        elif ch in PUNCT:
            flush(); out.append(ch); i += 1
        else:
            run += ch; i += 1
    flush()
    return out

def _real(line):
    """Characters that carry meaning — punctuation doesn't make a last line long enough."""
    return len([ch for ch in line if ch not in PUNCT])

def wrap(s, font, size, maxw):
    lines, cur = [], ''
    for tk in _tokens(s):
        trial = cur + tk
        if sw(trial, font, size) <= maxw or not cur.strip():
            cur = trial
        elif sw(tk, font, size) > maxw * 0.6 and not tk.isascii():      # a very long word may still break
            for ch in tk:
                if sw(cur + ch, font, size) <= maxw: cur += ch
                else: lines.append(cur.rstrip()); cur = ch
        else:
            lines.append(cur.rstrip()); cur = tk.lstrip()
    if cur.strip(): lines.append(cur.rstrip())
    # kinsoku: closing punctuation never starts a line, opening marks never end one
    for k in range(1, len(lines)):
        while lines[k] and lines[k][0] in CLOSE:
            lines[k - 1] += lines[k][0]; lines[k] = lines[k][1:].lstrip()
    for k in range(len(lines) - 1):
        while len(lines[k]) > 1 and lines[k][-1] in OPEN:
            lines[k + 1] = lines[k][-1] + lines[k + 1]; lines[k] = lines[k][:-1]
    lines = [ln for ln in lines if ln]
    # no widow: the last line carries at least three real characters (punctuation doesn't count);
    # Chinese is pulled down from the line above, a word at a time when word boundaries are known
    if len(lines) > 1 and not lines[-1].isascii():
        guard = 0
        while _real(lines[-1]) < 3 and _real(lines[-2]) > 5 and not lines[-2][-1].isascii() and guard < 12:
            guard += 1
            toks = _tokens(lines[-2]); take = toks[-1]
            if len(take) > 3 or take.isascii(): take = lines[-2][-1]
            lines[-2] = lines[-2][:-len(take)]; lines[-1] = take + lines[-1]
            while len(lines[-2]) > 1 and lines[-2][-1] in OPEN:
                lines[-1] = lines[-2][-1] + lines[-1]; lines[-2] = lines[-2][:-1]
            while lines[-1][0] in CLOSE and len(lines[-2]) > 1:      # keep kinsoku after the pull
                lines[-1] = lines[-2][-1] + lines[-1]; lines[-2] = lines[-2][:-1]
    # English text: the last line carries at least two words (no lone "me!")
    if len(lines) > 1 and len(lines[-1].split()) < 2 and len(lines[-2].split()) > 3 and ' ' in lines[-2]:
        head, last = lines[-2].rsplit(' ', 1)
        lines[-2], lines[-1] = head, last + ' ' + lines[-1]
    return lines

# ===== CASE DATA lives in the case directory, never in this script:
#   python3 build_simple.py [case.json]      (default: ./case.json; photo, audio_data.json beside it)
# Fields: name, pro (她/他), topic, date, task ("speak" | "read"), photo, overview[2–4], mark[],
# dims[6 × [name, verdict word, flowers, reading]], goal, games[3 × [name, how]], script.
# The recording length on the page comes from audio_data.json (50 ms windows), so it can't drift.
import sys
CASE_FILE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'case.json')
if not os.path.isfile(CASE_FILE):
    raise SystemExit(f'找不到 {CASE_FILE}：案例数据写在案例目录的 case.json 里（范例见 examples/*/case.json）')
CASE = os.path.dirname(CASE_FILE)

def fmt_secs(t):
    t = int(round(t))
    return f'{t} 秒' if t < 60 else f'{t // 60} 分 {t % 60} 秒' if t % 60 else f'{t // 60} 分钟'

def load_case(path):
    d = json.load(open(path, encoding='utf-8'))
    d['dims'] = [tuple(x) for x in d['dims']]; d['games'] = [tuple(x) for x in d['games']]
    d['img'] = d.get('photo') or d.get('img')
    d.setdefault('out', 'report-simple.pdf'); d.setdefault('task', 'speak')
    ad = os.path.join(CASE, 'audio_data.json')
    if os.path.isfile(ad):
        d['secs'] = fmt_secs(len(json.load(open(ad))['peaks']) * 0.05)
    elif 'secs' not in d:
        raise SystemExit('缺录音时长：放入 audio_data.json（extract_audio_data.py 生成），或在 case.json 写 secs')
    return d

M = 48; CW = W - 2 * M
E = 18                       # inner edge of the board frame: kept inside a home printer's printable area
OVER_X = M + 268             # overview column
OVER_W = W - M - OVER_X
COLX = (M, M + 272)          # readings: content dimensions left, sound dimensions right
DESC_W = 222
MEASURE = re.compile(r'\d+(\.\d+)?\s*(秒|个词|个半音|半音|音节|次|个|%|dB|分贝|Hz)')

def lead_of(line):
    """'最棒的：…' -> '最棒的：' (a lead-in of up to six characters before a full-width colon)."""
    k = line.find('：')
    return line[:k + 1] if 0 < k <= 6 else ''

def common_run(a, b):
    """Longest run of words the two texts share — spaces and punctuation don't count."""
    a, b = re.sub(r'[\s\W_]+', '', a), re.sub(r'[\s\W_]+', '', b)
    best = ''
    for i in range(len(a)):
        for j in range(i + len(best) + 1, len(a) + 1):
            if a[i:j] in b: best = a[i:j]
            else: break
    return best

def validate(d):
    """Fail with a message the writer can act on, before anything is drawn."""
    if d.get('task', 'speak') not in ('speak', 'read'):
        raise ValueError('task 只能是 speak（自由表达）或 read（朗读现成文本）')
    if d.get('task') == 'read' and not d.get('original'):
        raise ValueError('朗读案例必须写 original（课文原文）：读错的词只有对着原文才查得出')
    ov = d['overview']
    if not 2 <= len(ov) <= 4:
        raise ValueError('overview 写 2–4 条：讲了什么 / 最棒的 / 说得怎么样 / 要加油的')
    for k, line in enumerate(ov):
        if len(wrap(line, 'SCS', 10, OVER_W)) > 2:
            raise ValueError(f'overview[{k}] 超过两行，请精简：{line}')
        m = MEASURE.search(line)
        if m:
            raise ValueError(f'overview[{k}] 含测量值「{m.group()}」：数字证据只写在逐项解读里，总览只说结论')
        for nm, _, _, desc in d['dims']:
            run = common_run(line, desc)
            if len(run) >= 7:
                raise ValueError(f'overview[{k}] 与「{nm}」解读重复了「{run}」：总览换一种说法，或删掉其中一处')
    if len(d['dims']) != 6 or [x[0] for x in d['dims']] != ['词汇', '句式与语法', '完整与创意', '发音准确度', '流利度', '语调与重音']:
        raise ValueError('dims 须按 词汇、句式与语法、完整与创意、发音准确度、流利度、语调与重音 排列')
    for nm, wd, n, desc in d['dims']:
        if not (isinstance(n, int) and 0 <= n <= 5): raise ValueError(f'{nm} 的花数须为 0–5')
        if len(wrap(desc, 'SCS', 9.5, DESC_W)) > 3: raise ValueError(f'「{nm}」解读超过三行，请精简')
    if len(d['games']) != 3: raise ValueError('games 须为 3 个')
    if len(wrap(d['goal'], 'SCS', 10.5, CW - 90)) > 1: raise ValueError('goal 须一行写完')
    pron = d['dims'][3][3] + d['goal']
    for w_ in d.get('mark', []):
        if not re.search(r'\b' + re.escape(w_) + r'\b', d['script'], re.I):
            raise ValueError(f'mark 里的「{w_}」不在全文里')
        if w_.lower() not in pron.lower():
            raise ValueError(f'mark 里的「{w_}」须同时出现在「发音准确度」解读或小目标里，前后才对得上')
    meta = f"姓名 {d['name']} · 课题 {d['topic']} · 录音 {d['secs']} · {d['date']}"
    if M + sw(meta, 'SCS', 10.5) > PHOTO_X - 14:
        raise ValueError('页眉信息行太长，会碰到照片：请缩短课题')

PHOTO_W, PHOTO_H = 96, 112
PHOTO_X, PHOTO_TOP = W - M - PHOTO_W + 4, H - 28

def top_layout(d):
    """Where the top half ends, computed from content — the cream field, the overview and the
    readings heading all follow it, so nothing is pinned to a hand-set y."""
    hy = H - 110                                   # 六个维度 heading
    cy0 = hy - 110                                 # radar centre
    photo_bottom = PHOTO_TOP - PHOTO_H - 8
    oy0 = min(hy - 24, photo_bottom - 22)          # 总览 title: below the photo print
    yy = oy0 - 21
    for ln in d['overview']:
        yy -= 14 * len(wrap(ln, 'SCS', 10, OVER_W)) + 4
    iy = min(cy0 - 150, yy - 40)                   # 逐项解读 heading
    return dict(hy=hy, cy0=cy0, oy0=oy0, iy=iy, field_bottom=iy + 34)

SUN_R, SUN_C = 138, (W - 30, H - 16)

def render(d):
    validate(d)
    L = top_layout(d)
    c = canvas.Canvas(os.path.join(CASE, d['out']), pagesize=A4)
    def text(x, y, s, f='SCS', size=10, color=INK):
        c.setFont(f, size); c.setFillColor(color); c.drawString(x, y, s)
    def textC(cx, y, s, f='SCS', size=10, color=INK):
        text(cx - sw(s, f, size) / 2, y, s, f, size, color)
    def para(x, ytop, s, f='SCS', size=9.5, color=INK, maxw=240, leading=12.5):
        yy = ytop
        for ln in wrap(s, f, size, maxw):
            text(x, yy, ln, f, size, color); yy -= leading
        return yy
    def tape(cx, cy, w=34, h=10, ang=-4, col='#FFE9A8'):
        c.saveState(); c.translate(cx, cy); c.rotate(ang)
        c.setFillColor(HexColor(col)); c.setFillAlpha(0.78)
        c.rect(-w / 2, -h / 2, w, h, stroke=0, fill=1); c.setFillAlpha(1); c.restoreState()
    from reportlab.lib.utils import ImageReader
    def cover_image(path, x, y, w, h, fx=0.5, fy=0.5):
        # object-fit: cover — scale to fill the box, centre-crop the overflow, never distort
        iw, ih = ImageReader(path).getSize()
        s = max(w / iw, h / ih); dw, dh = iw * s, ih * s
        c.saveState()
        clip = c.beginPath(); clip.rect(x, y, w, h); c.clipPath(clip, stroke=0, fill=0)
        c.drawImage(path, x + (w - dw) * fx, y + (h - dh) * fy, dw, dh)
        c.restoreState()
    def cloud(cx, cy, s=1.0):
        c.setFillColor(CARD)
        c.ellipse(cx - 26 * s, cy - 8 * s, cx + 26 * s, cy + 8 * s, stroke=0, fill=1)
        c.ellipse(cx - 14 * s, cy - 4 * s, cx + 8 * s, cy + 13 * s, stroke=0, fill=1)
        c.ellipse(cx + 2 * s, cy - 5 * s, cx + 20 * s, cy + 10 * s, stroke=0, fill=1)
    def leaf(x, y, w, h, ang, col):
        c.saveState(); c.translate(x, y); c.rotate(ang); c.setFillColor(col)
        c.ellipse(-w / 2, -h / 2, w / 2, h / 2, stroke=0, fill=1); c.restoreState()
    def sparkle_r(cx, cy, r, col):
        # a plump four-lobe sparkle — same rounded family as the flower petals
        c.setFillColor(col); p = c.beginPath(); p.moveTo(cx, cy + r)
        p.curveTo(cx + r * 0.18, cy + r * 0.18, cx + r * 0.18, cy + r * 0.18, cx + r, cy)
        p.curveTo(cx + r * 0.18, cy - r * 0.18, cx + r * 0.18, cy - r * 0.18, cx, cy - r)
        p.curveTo(cx - r * 0.18, cy - r * 0.18, cx - r * 0.18, cy - r * 0.18, cx - r, cy)
        p.curveTo(cx - r * 0.18, cy + r * 0.18, cx - r * 0.18, cy + r * 0.18, cx, cy + r)
        c.drawPath(p, stroke=0, fill=1)
    def gloss(cx, cy, r):
        c.saveState(); c.translate(cx - r * 0.34, cy + r * 0.38); c.rotate(-28)
        c.setFillColor(CARD); c.setFillAlpha(0.8)
        c.ellipse(-r * 0.34, -r * 0.15, r * 0.34, r * 0.15, stroke=0, fill=1)
        c.setFillAlpha(1); c.restoreState()
    def flower1(cx, cy, s=0.8, filled=True):
        for a in range(6):
            deg = 90 + a * 60
            ang = math.radians(deg)
            px, py = cx + 3.0 * s * math.cos(ang), cy + 3.0 * s * math.sin(ang)
            c.saveState(); c.translate(px, py); c.rotate(deg)
            if filled:
                c.setFillColor(HexColor('#F0563F')); c.ellipse(-2.8 * s, -1.75 * s, 2.8 * s, 1.75 * s, stroke=0, fill=1)
            else:
                c.setStrokeColor(FAINT); c.setLineWidth(0.8); c.setDash(2.2, 1.8)
                c.ellipse(-2.8 * s, -1.75 * s, 2.8 * s, 1.75 * s, stroke=1, fill=0); c.setDash()
            c.restoreState()
        if filled:
            c.setFillColor(HexColor('#FFC93C')); c.circle(cx, cy, 1.85 * s, stroke=0, fill=1)
            c.setStrokeColor(HexColor('#E8930C')); c.setLineWidth(0.6 * s); c.circle(cx, cy, 1.85 * s, stroke=1, fill=0)
        else:
            c.setFillColor(HexColor('#EDF1F5')); c.circle(cx, cy, 1.85 * s, stroke=0, fill=1)
    def flowers(x, cy, n, s=0.8):
        for i in range(5):
            flower1(x + 9.5 * s + i * 19 * s, cy, s, i < n)
    def stage_icon(i, cx, cy, on):
        GR = HexColor('#7CB342') if on else HexColor('#C9D2DC')
        BR = HexColor('#8D6E63') if on else HexColor('#D5DCE4')
        if i == 0:
            c.setFillColor(BR); c.ellipse(cx - 8, cy - 8, cx + 8, cy - 2, stroke=0, fill=1)
            c.setStrokeColor(GR); c.setLineWidth(2); c.setLineCap(1); c.line(cx, cy - 5, cx, cy + 2)
            leaf(cx - 3.4, cy + 3.4, 8, 4.4, 38, GR); leaf(cx + 3.4, cy + 3.4, 8, 4.4, 142, GR)
        elif i == 1:
            c.setStrokeColor(GR); c.setLineWidth(2); c.setLineCap(1); c.line(cx, cy - 8, cx, cy + 4)
            leaf(cx - 3.6, cy + 1, 8.6, 4.6, 38, GR); leaf(cx + 3.6, cy + 1, 8.6, 4.6, 142, GR)
            leaf(cx, cy + 6.4, 8.6, 4.6, 90, GR)
        elif i == 2:
            c.setStrokeColor(GR); c.setLineWidth(2); c.setLineCap(1); c.line(cx, cy - 9, cx, cy - 1)
            leaf(cx + 3.4, cy - 5.4, 8, 4.2, -32, GR)
            flower1(cx, cy + 3.4, 0.92, on)
        else:
            stage_icon(2, cx, cy, on)
            _sc = HexColor('#FFC93C') if on else HexColor('#D5DCE4')
            sparkle_r(cx - 11, cy + 6, 3.4, _sc); sparkle_r(cx + 11, cy + 1, 2.6, _sc)
    def head(y, t):
        text(M, y, t, DISP, 15.5, INK)
        return y

    # ===== one cream field over the whole top; its bottom edge is a soft wave,
    # with two clouds sitting on the seam — the divider is drawn, not ruled =====
    _by = L['field_bottom']
    _fp = c.beginPath(); _fp.moveTo(E, _by + 4)
    for _x0, _y0, _x1, _y1 in [(E, 4, 104, -6), (104, -6, 196, 7), (196, 7, 288, -6), (288, -6, 380, 7), (380, 7, 472, -6), (472, -6, W - E, 3)]:
        _fp.curveTo(_x0 + (_x1 - _x0) * 0.5, _by + _y0, _x1 - (_x1 - _x0) * 0.5, _by + _y1, _x1, _by + _y1)
    _fp.lineTo(W - E, H - E); _fp.lineTo(E, H - E); _fp.close()
    c.setFillColor(HexColor('#FFF9EA')); c.drawPath(_fp, stroke=0, fill=1)
    cloud(196, _by + 1, 0.85); cloud(472, _by - 2, 0.7)
    # the corner sun on top of the field
    # a real sun, built the way the reference builds it: one flat disc
    # with twelve pill-shaped rays floating around it, centre off the corner
    # The disc is large enough that a clear arc shows around the photo print; a ray is drawn only
    # where it reads as part of the sun — never across text, never cut by the frame, never peeking
    # out from behind the photo as a stray bar.
    _sx, _sy = SUN_C
    c.setFillColor(HexColor('#FFD65A'))
    _keep_out = [(OVER_X - 8, L['oy0'] - 400, W, L['oy0'] + 16),                 # overview column
                 (M - 4, H - 80, M + 12 + max(sw('英语口语测评报告', DISP, 25),                  # title + meta line
                                              sw(f"姓名 {d['name']} · 课题 {d['topic']} · 录音 {d['secs']} · {d['date']}", 'SCS', 10.5)), H),
                 (PHOTO_X - 14, PHOTO_TOP - PHOTO_H - 16, PHOTO_X + PHOTO_W + 14, PHOTO_TOP + 16)]
    _rays = []
    for _k in range(12):
        _a = math.radians(115 + _k * 30)
        _pts = [(_sx + r_ * math.cos(_a), _sy + r_ * math.sin(_a)) for r_ in (SUN_R + 9, SUN_R + 31)]
        _x0, _x1 = min(p_[0] for p_ in _pts) - 5, max(p_[0] for p_ in _pts) + 5
        _y0, _y1 = min(p_[1] for p_ in _pts) - 5, max(p_[1] for p_ in _pts) + 5
        if _x0 < E + 4 or _x1 > W - E - 4 or _y0 < E + 4 or _y1 > H - E - 4: continue
        if any(_x0 < kx1 and _x1 > kx0 and _y0 < ky1 and _y1 > ky0 for kx0, ky0, kx1, ky1 in _keep_out): continue
        _rays.append((_k, _a))
    _ks = {k for k, _ in _rays}
    _grouped = [(k, a) for k, a in _rays if ((k - 1) % 12 in _ks and (k - 2) % 12 in _ks) or
                ((k - 1) % 12 in _ks and (k + 1) % 12 in _ks) or ((k + 1) % 12 in _ks and (k + 2) % 12 in _ks)]
    for _k, _a in _grouped:                       # a ray stays only inside a run of three neighbours
        c.saveState(); c.translate(_sx, _sy); c.rotate(math.degrees(_a) - 90)
        _rp = c.beginPath(); _rp.roundRect(-4.5, SUN_R + 9, 9, 22, 4.5); c.drawPath(_rp, stroke=0, fill=1)
        c.restoreState()
    c.circle(_sx, _sy, SUN_R, stroke=0, fill=1)
    # a proper little landscape along the bottom: two soft hill layers,
    # trees, bushes, grass and two tiny flowers — drawn, not a lone line
    _bp2 = c.beginPath(); _bp2.moveTo(E, 66)
    for _x0, _y0, _x1, _y1 in [(E, 66, 150, 58), (150, 58, 300, 64), (300, 64, 450, 57), (450, 57, W - E, 62)]:
        _bp2.curveTo(_x0 + (_x1 - _x0) * 0.5, _y0, _x1 - (_x1 - _x0) * 0.5, _y1, _x1, _y1)
    _bp2.lineTo(W - E, E); _bp2.lineTo(E, E); _bp2.close()
    c.setFillColor(HexColor('#E3F0DB')); c.drawPath(_bp2, stroke=0, fill=1)
    _fp2 = c.beginPath(); _fp2.moveTo(E, 42)
    for _x0, _y0, _x1, _y1 in [(E, 42, 160, 35), (160, 35, 320, 41), (320, 41, 460, 34), (460, 34, W - E, 39)]:
        _fp2.curveTo(_x0 + (_x1 - _x0) * 0.5, _y0, _x1 - (_x1 - _x0) * 0.5, _y1, _x1, _y1)
    _fp2.lineTo(W - E, E); _fp2.lineTo(E, E); _fp2.close()
    c.setFillColor(HexColor('#CDE6BE')); c.drawPath(_fp2, stroke=0, fill=1)
    # bushes
    c.setFillColor(HexColor('#A9D18E'))
    c.ellipse(196, 32, 232, 44, stroke=0, fill=1); c.ellipse(336, 30, 366, 41, stroke=0, fill=1); c.ellipse(52, 44, 76, 53, stroke=0, fill=1)
    # the big tree, right
    c.setFillColor(HexColor('#8D6E63')); c.rect(502, 34, 5, 17, stroke=0, fill=1)
    c.setFillColor(HexColor('#7CB342'))
    c.circle(504, 62, 13, stroke=0, fill=1); c.circle(494, 52, 9, stroke=0, fill=1); c.circle(515, 53, 10, stroke=0, fill=1)
    c.setFillColor(HexColor('#F0563F')); c.circle(498, 60, 2.1, stroke=0, fill=1); c.circle(511, 66, 2.1, stroke=0, fill=1)
    # a small tree, left
    c.setFillColor(HexColor('#8D6E63')); c.rect(118, 40, 4, 12, stroke=0, fill=1)
    c.setFillColor(HexColor('#7CB342'))
    c.circle(120, 60, 9, stroke=0, fill=1); c.circle(113, 53, 6.5, stroke=0, fill=1); c.circle(127, 54, 7, stroke=0, fill=1)
    # grass tufts along the crests
    c.setStrokeColor(HexColor('#7CB342')); c.setLineWidth(1.4)
    for gx2, gy2 in [(160, 38), (268, 34), (404, 32), (452, 30), (556, 36), (70, 46)]:
        c.line(gx2, gy2, gx2 - 3, gy2 + 7); c.line(gx2 + 4, gy2, gx2 + 4, gy2 + 8); c.line(gx2 + 8, gy2, gx2 + 11, gy2 + 7)
    # two tiny flowers on stems, same glyph as the score flowers
    c.setStrokeColor(HexColor('#7CB342')); c.setLineWidth(1.4)
    c.line(168, 36, 168, 46); c.line(430, 33, 430, 43)
    _tiny_flowers = [(168, 50), (430, 47)]

    # the yellow board frame — everything is pinned inside it. Its outer edge sits 14pt (5 mm)
    # in from the paper edge, inside what an office or home printer can actually print.
    c.setStrokeColor(HexColor('#FFC93C')); c.setLineWidth(8); c.rect(E - 4, E - 4, W - 2 * E + 8, H - 2 * E + 8, stroke=1, fill=0)

    for _fx, _fy in _tiny_flowers:
        flower1(_fx, _fy, 0.52, True)
    # ---------- 1. header: identity + overall ----------
    text(M, H - 46, '英语口语测评报告', DISP, 25, INK)
    text(M, H - 68, f"姓名 {d['name']} · 课题 {d['topic']} · 录音 {d['secs']} · {d['date']}", 'SCS', 10.5, INK)
    # small photo, top right: rounded, yellow-framed (kindergarten album)
    pw2, ph2 = PHOTO_W, PHOTO_H
    px2, py2 = PHOTO_X, PHOTO_TOP - PHOTO_H
    c.saveState(); c.translate(px2 + pw2 / 2, py2 + ph2 / 2); c.rotate(2)
    c.setFillColor(HexColor('#000000')); c.setFillAlpha(0.10)
    c.rect(-pw2 / 2 - 4, -ph2 / 2 - 8, pw2 + 10, ph2 + 12, stroke=0, fill=1); c.setFillAlpha(1)
    c.setFillColor(CARD); c.rect(-pw2 / 2 - 6, -ph2 / 2 - 6, pw2 + 12, ph2 + 12, stroke=0, fill=1)
    cover_image(os.path.join(CASE, d['img']), -pw2 / 2, -ph2 / 2, pw2, ph2)
    c.restoreState()
    tape(px2 + pw2 / 2, py2 + ph2 + 6, 40, 12, -5, '#FFFFFF')
    photo_bottom = py2 - 8
    oy = H - 96
    # ---------- 2. the hexagon, first ----------
    hy = L['hy']
    head(hy, '六个维度')
    R = 72; cx0, cy0 = M + 118, L['cy0']
    order = [0, 1, 2, 5, 4, 3]  # 词汇 句式 完整 / 语调 流利 发音 around the ring
    def _pt(i, r):
        a = math.radians(90 - i * 60)
        return (cx0 + r * math.cos(a), cy0 + r * math.sin(a))
    for ring in range(1, 6):
        outer = ring == 5
        c.setStrokeColor(FAINT); c.setLineWidth(1.1 if outer else 0.7)
        pp = c.beginPath()
        for i in range(6):
            x, y = _pt(i, R * ring / 5)
            pp.moveTo(x, y) if i == 0 else pp.lineTo(x, y)
        pp.close(); c.drawPath(pp, stroke=1, fill=0)
    for i in range(6):
        x, y = _pt(i, R); c.setStrokeColor(FAINT); c.setLineWidth(0.8); c.line(cx0, cy0, x, y)

    def _data(off=0):
        pp = c.beginPath()
        for k, di in enumerate(order):
            x, y = _pt(k, R * d['dims'][di][2] / 5)
            pp.moveTo(x, y + off) if k == 0 else pp.lineTo(x, y + off)
        pp.close(); return pp
    pp = _data()
    c.setFillColor(HexColor('#F09A2E')); c.setFillAlpha(0.30); c.drawPath(pp, stroke=0, fill=1); c.setFillAlpha(1)
    c.setStrokeColor(HexColor('#ED8F24')); c.setLineWidth(2.2); c.setLineJoin(1); c.drawPath(pp, stroke=1, fill=0); c.setLineJoin(0)
    for k, di in enumerate(order):
        x, y = _pt(k, R * d['dims'][di][2] / 5)
        c.setFillColor(HexColor('#ED8F24')); c.circle(x, y, 3.6, stroke=0, fill=1)
        c.setStrokeColor(CARD); c.setLineWidth(1.6); c.circle(x, y, 3.6, stroke=1, fill=0)
    for k, di in enumerate(order):        # names only: the verdict word is said once, in the readings
        nm = d['dims'][di][0]
        lx, ly = _pt(k, R + 10)
        if k == 0: textC(lx, ly + 4, nm, 'SCB', 10.5, INK)
        elif k == 3: textC(lx, ly - 12, nm, 'SCB', 10.5, INK)
        elif k in (1, 2): text(lx, ly - 3.5, nm, 'SCB', 10.5, INK)
        else: text(lx - sw(nm, 'SCB', 10.5), ly - 3.5, nm, 'SCB', 10.5, INK)
    # overview beside the chart
    ox = OVER_X
    oy0 = L['oy0']
    text(ox, oy0, '总览', 'SCB', 11, INK)
    yy = oy0 - 21
    for ln in d['overview']:
        lead = lead_of(ln)
        for j, row in enumerate(wrap(ln, 'SCS', 10, OVER_W)):
            if j == 0 and lead and row.startswith(lead):
                text(ox, yy, lead, 'SCB', 10, INK)
                text(ox + sw(lead, 'SCB', 10), yy, row[len(lead):], 'SCS', 10, INK)
            else:
                text(ox, yy, row, 'SCS', 10, INK)
            yy -= 14
        yy -= 4

    # ---------- 3. interpretation, dimension by dimension ----------
    iy = L['iy']
    head(iy, '逐项解读')
    for col, sub in enumerate(('说了什么', '声音怎么样')):
        text(COLX[col], iy - 19, sub, 'SCS', 9, GREY)
    gy = iy - 36
    for row in range(3):                 # each row as tall as its longer reading
        pair = (d['dims'][row], d['dims'][row + 3])
        rows_used = max(len(wrap(x[3], 'SCS', 9.5, DESC_W)) for x in pair)
        for col, (nm, wd, n, desc) in enumerate(pair):
            gx = COLX[col]
            text(gx, gy, nm, 'SCB', 11, INK)
            text(gx + sw(nm, 'SCB', 11) + 8, gy, wd, 'SCS', 10, INK)
            flowers(gx + 168, gy + 3, n, 0.72)
            para(gx, gy - 14, desc, 'SCS', 9.5, INK, maxw=DESC_W, leading=12.5)
        gy -= 14 + rows_used * 12.5 + 11

    # ---------- 4. what to do next ----------
    ny = gy - 10
    head(ny, '接下来怎么做')
    _gw = sw(d['goal'], 'SCS', 10.5)
    c.setFillColor(HexColor('#E7ECF1')); c.rect(M + 59, ny - 36, _gw + 18, 21, stroke=0, fill=1)
    c.setFillColor(HexColor('#FFF9EA')); c.rect(M + 56, ny - 33, _gw + 18, 21, stroke=0, fill=1)
    c.setStrokeColor(HexColor('#EFE9DC')); c.setLineWidth(0.8); c.rect(M + 56, ny - 33, _gw + 18, 21, stroke=1, fill=0)
    tape(M + 62, ny - 12, 24, 8, -7)
    # baseline sits 0.35em BELOW the chip's centre: PDF text hangs on its baseline,
    # and CJK ink lives almost entirely above it — centre the ink, not the baseline
    text(M, ny - 26, '小目标', 'SCB', 11, RED)
    text(M + 65, ny - 26, d['goal'], 'SCS', 10.5, INK)
    gy = ny - 56
    text(M, gy, '在家练', 'SCB', 11, INK)
    for j, (gn, gd) in enumerate(d['games']):
        bx = M + 64                      # three games, no order between them: a box to tick, not a rank
        c.setStrokeColor(INK); c.setLineWidth(1.1); c.roundRect(bx, gy - 1.5, 11, 11, 2.5, stroke=1, fill=0)
        text(bx + 20, gy, gn, 'SCB', 10.5, INK)
        para(M + 168, gy, gd, 'SCS', 10, INK, maxw=CW - 168, leading=13)
        gy -= 20

    # ---------- 5. appendix: the transcript ----------
    ay = gy - 16
    # the transcript is the child's whole speech: it is never trimmed — it steps down 9.5 -> 8 pt to fit,
    # with leading kept at 1.45x so the practice-word underline never touches the next line
    for tfs, lf in ((9.5, 1.45), (9, 1.45), (8.5, 1.45), (8, 1.45), (8, 1.36)):
        tld = round(tfs * lf, 1)
        lines = wrap(d['script'], 'ENR', tfs, CW)
        box_h = 31 + len(lines) * tld
        box_bot = ay + 17 - box_h
        if box_bot >= 74: break
    else:
        raise ValueError(f'内容超出版面 {74 - box_bot:.0f}pt：全文已缩到 8pt，请精简解读或游戏')
    c.setFillColor(HexColor('#E4E9EF')); c.rect(M - 9, box_bot - 3, CW + 22, box_h, stroke=0, fill=1)
    c.setFillColor(HexColor('#FFFDF5')); c.rect(M - 12, box_bot, CW + 22, box_h, stroke=0, fill=1)
    c.setStrokeColor(HexColor('#F0EAD8')); c.setLineWidth(0.8); c.rect(M - 12, box_bot, CW + 22, box_h, stroke=1, fill=0)
    tape(W / 2, ay + 17, 40, 11, 2)
    text(M, ay, f"附：{d['pro']}说的话（全文）", 'SCB', 10.5, GREY)
    # the recording itself, as a quiet strip beside the title: the page was measured, not guessed
    _ad = os.path.join(CASE, 'audio_data.json')
    if os.path.exists(_ad):
        pk = json.load(open(_ad))['peaks']
        box_r = M - 12 + CW + 22                     # the box's right edge: label and strip stay inside it
        lab_w = sw(d['secs'], 'SCS', 8.5)
        lab_x = box_r - 12 - lab_w
        wx0 = max(M + sw(f"附：{d['pro']}说的话（全文）", 'SCB', 10.5) + 24, box_r - 230)
        ww = lab_x - 8 - wx0; n = max(24, int(ww / 3.05))
        c.setStrokeColor(HexColor('#C2CCD6')); c.setLineWidth(1.8); c.setLineCap(1)
        for i in range(n):
            seg = pk[int(i * len(pk) / n): max(int((i + 1) * len(pk) / n), int(i * len(pk) / n) + 1)]
            v = max(seg) if seg else 0
            xx = wx0 + i * ww / (n - 1); h = 1 + v * 9
            c.line(xx, ay + 3.5 - h / 2, xx, ay + 3.5 + h / 2)
        text(lab_x, ay, d['secs'], 'SCS', 8.5, GREY)
    marks = [w_.lower() for w_ in d.get('mark', [])]
    yy = ay - 16
    for ln in lines:
        text(M, yy, ln, 'ENR', tfs, INK)
        for m_ in re.finditer(r"[A-Za-z']+", ln):     # the practice words, same dashed red as the main report
            if m_.group().lower() in marks:
                ux = M + sw(ln[:m_.start()], 'ENR', tfs)
                c.setStrokeColor(RED); c.setLineWidth(1.2); c.setDash(2.6, 1.8)
                c.line(ux, yy - 2.4, ux + sw(m_.group(), 'ENR', tfs), yy - 2.4); c.setDash()
        yy -= tld
    # footer on its own clean label, never across the drawn landscape
    _fr = '参照剑桥 Starters 与 IELTS 口语标准'
    _fw = sw(_fr, 'SCS', 8) + 20
    c.setFillColor(CARD); c.setFillAlpha(0.92)
    c.roundRect(W / 2 - _fw / 2, 19, _fw, 15, 7.5, stroke=0, fill=1); c.setFillAlpha(1)
    textC(W / 2, 23.5, _fr, 'SCS', 8, INK)
    c.showPage(); c.save()
    print('saved', d['out'])

render(load_case(CASE_FILE))
