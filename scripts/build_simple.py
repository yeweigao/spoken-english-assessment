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
- Illustrations are all hand-drawn flat vector shapes in one family (rounded,
  matte, no emoji, no gloss): sun, clouds, flowers, the bottom landscape.
Run from a case directory containing the photo (d['img']). Case content sits
in the marked CASE DATA section — edit per child."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, math

W, H = A4
BASE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))
CASE = os.getcwd()

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
def wrap(s, font, size, maxw):
    # CJK-aware: latin words stay whole, each CJK char is its own token
    tokens, i = [], 0
    while i < len(s):
        ch = s[i]
        if ch == ' ':
            tokens.append(' '); i += 1
        elif ch.isascii() and (ch.isalnum() or ch in ".'-"):
            j = i
            while j < len(s) and s[j].isascii() and (s[j].isalnum() or s[j] in ".'-"): j += 1
            tokens.append(s[i:j]); i = j
        else:
            tokens.append(ch); i += 1
    lines, cur = [], ''
    for tk in tokens:
        trial = cur + tk
        if sw(trial, font, size) <= maxw or not cur.strip():
            cur = trial
        else:
            lines.append(cur.rstrip()); cur = tk.lstrip()
    if cur.strip(): lines.append(cur.rstrip())
    return lines

# ===== CASE DATA — the worked example below is Apple; TOTO follows as the
# second worked example. To build a case, put its dict in CHILD and run.
CHILD = dict(
    out='report-simple.pdf', name='Apple', pro='她', topic='My Password',
    date='2026.11.10', secs='45 秒', stage='绽放', comment='一整件事讲得有头有尾、顺顺当当，就差把词尾音补齐。',
    stage_def='能把短句连成一段、按顺序讲清一件事——这一级的口语 can-do 要求，她都做到了。',
    img='photo.jpg',
    overview=['这次她把「设一个密码」从头讲到尾：先挑词、再挑字母，最后拼出来揭晓，一步都没落下。',
              '最棒的是完整：45 秒讲完一整件事，还能自己变出 CEAD48，不是背的。',
              '小毛病在词尾巴：eight、salad 最后那个音没送出来，被听成了别的词。',
              '说话很顺：没有「嗯、啊」，只改了一次口；想字母时停了 1.4 秒，是在认真想。',
              '声音有高有低，句子说完都稳稳收住；下一步把词尾音补齐，就更像小老师了。'],
    dims=[('词汇', '用得准', 4, '本课词都用在对的地方：password、choose、letter、number；还自己挑了 chocolate 和 salad 当原料。'),
          ('句式与语法', '挺稳当', 4, '四步用 first、then、next、last 领着走，顺序不乱；小瑕疵一处：for me 应是 for myself。'),
          ('完整与创意', '有头有尾', 5, '开头、步骤、揭晓、道谢都齐；密码是自己拼的，不是背的。'),
          ('发音准确度', '很清楚', 4, '大意全被听懂；卡在词尾音：eight 被听成 ace，salad 被听成 said。'),
          ('流利度', '很顺溜', 4, '语速 3.1 音节/秒，没有「嗯、啊」；改了一次口，想字母时停了 1.4 秒。'),
          ('语调与重音', '有起伏', 4, '跨度 11.6 个半音，句尾多是降调、稳稳落地；salad 的重音落到了后面。')],
    goal='把词尾音补齐：eight 的 t、salad 的 d 都念出来。',
    games=[('词尾音大扫除', 'eight、next、salad 慢慢念，送出词尾的 t、d。'),
           ('步骤词讲故事', '用 first、then、next、last，把泡牛奶或穿衣服讲成四步。'),
           ('拼一个新密码', '挑两个喜欢的词，各取两字母，加两个数字，拼出来念给大家听。')],
    script=("Hello everyone, my name is Apple. I want to set a password for me. "
            "First, I choose two words: chocolate and salad. Then I choose two letters C E from chocolate. "
            "I choose two letters A D from salad. Next, I choose two numbers: four and eight. "
            "And last, I put them together. My password is CEAD48. Thank you!"),
)
EXAMPLE_TOTO = dict(
    out='report-simple.pdf', name='Toto', pro='他', topic='My Funny Face',
    date='2026.11.09', secs='37 秒', stage='绽放', comment='一口气把「怪脸」讲了一圈，句子稳，就差两个音还没出来。',
    stage_def='能把短句连成一段、按顺序讲清一件事——这一级的口语 can-do 要求，他都做到了。',
    img='portrait.png',
    overview=['这次他对着镜头，把自己的「怪脸」从头讲了一圈：眼睛、眉毛、耳朵、嘴巴，一个没落下。',
              '最棒的是句子稳：this 和 these 分得清清楚楚，最长一句 15 个词，一口气说完。',
              '结尾那句是他自己编的——课文里没有，他一口气夸了自己三个词。',
              '小毛病在两个音：mouth 的 th、oval 的 v 还没出来，被听成了别的词。',
              '说话不慌：没有「嗯、啊」，想词时停一停再接着说；声音有高有低，每句都稳稳收尾。'],
    dims=[('词汇', '用得准', 4, '颜色、大小、数字都说得出：three、six 用对了，big、round 反复用得稳。'),
          ('句式与语法', '挺稳当', 5, 'this 和 these 分工清楚，单复数没乱；最长一句 15 个词，一口气说完。'),
          ('完整与创意', '有头有尾', 5, '脸、眼睛、耳朵、嘴巴讲了一圈；结尾一句是自己编的。'),
          ('发音准确度', '很清楚', 4, '大意都听懂了；mouth 被听成 mouse——词尾 th 没出来；oval 的 v 也没出来，词没被听清。'),
          ('流利度', '很顺溜', 4, '语速约 2.5 音节/秒，没有「嗯、啊」；想词时停过几次，最长 2.8 秒。'),
          ('语调与重音', '有起伏', 4, '跨度 12.9 个半音，六句句尾全是降调、稳稳落地；YEL-low、SIL-ly 的重音都站对了。')],
    goal='把 mouth 的 th、oval 的 v 念出来。',
    games=[('小舌头探险', '对着镜子露一点舌尖说 mouth、teeth、three，专练词尾 th。'),
           ('蜜蜂 v 嗡嗡', '上牙轻咬下唇说 oval、love、five，摸喉咙，有震动 v 就出来了。'),
           ('重音拍手', 'YEL-low、SIL-ly 第一下重拍、第二下轻带，再站起来喊出结尾句。')],
    script=("Hi! I am Toto. This is my big round yellow face. These are my three big round blue eyes "
            "with six big black and yellow eyebrows. These are my two big pink ears. "
            "This is my big oval red mouth. I love the ugly, silly and scary me!"),
)

M = 48; CW = W - 2 * M

def render(d):
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
    _by = H - 354
    _fp = c.beginPath(); _fp.moveTo(12, _by + 4)
    for _x0, _y0, _x1, _y1 in [(12, 4, 104, -6), (104, -6, 196, 7), (196, 7, 288, -6), (288, -6, 380, 7), (380, 7, 472, -6), (472, -6, 583, 3)]:
        _fp.curveTo(_x0 + (_x1 - _x0) * 0.5, _by + _y0, _x1 - (_x1 - _x0) * 0.5, _by + _y1, _x1, _by + _y1)
    _fp.lineTo(583, H - 12); _fp.lineTo(12, H - 12); _fp.close()
    c.setFillColor(HexColor('#FFF9EA')); c.drawPath(_fp, stroke=0, fill=1)
    cloud(196, _by + 1, 0.85); cloud(472, _by - 2, 0.7)
    # the corner sun on top of the field
    # a real sun, built the way the reference builds it: one flat disc
    # with twelve pill-shaped rays floating around it, centre off the corner
    _sx, _sy = W - 30, H - 16
    c.setFillColor(HexColor('#FFD65A'))
    for _k in range(12):
        c.saveState(); c.translate(_sx, _sy); c.rotate(25 + _k * 30)
        _rp = c.beginPath(); _rp.roundRect(-4.5, 121, 9, 22, 4.5); c.drawPath(_rp, stroke=0, fill=1)
        c.restoreState()
    c.circle(_sx, _sy, 112, stroke=0, fill=1)
    # two rounded sparkles floating in the white
    sparkle_r(28, 216, 8, HexColor('#FFC93C')); sparkle_r(552, 168, 8, HexColor('#FFC93C'))
    # a proper little landscape along the bottom: two soft hill layers,
    # trees, bushes, grass and two tiny flowers — drawn, not a lone line
    _bp2 = c.beginPath(); _bp2.moveTo(12, 66)
    for _x0, _y0, _x1, _y1 in [(12, 66, 150, 58), (150, 58, 300, 64), (300, 64, 450, 57), (450, 57, 583, 62)]:
        _bp2.curveTo(_x0 + (_x1 - _x0) * 0.5, _y0, _x1 - (_x1 - _x0) * 0.5, _y1, _x1, _y1)
    _bp2.lineTo(583, 12); _bp2.lineTo(12, 12); _bp2.close()
    c.setFillColor(HexColor('#E3F0DB')); c.drawPath(_bp2, stroke=0, fill=1)
    _fp2 = c.beginPath(); _fp2.moveTo(12, 42)
    for _x0, _y0, _x1, _y1 in [(12, 42, 160, 35), (160, 35, 320, 41), (320, 41, 460, 34), (460, 34, 583, 39)]:
        _fp2.curveTo(_x0 + (_x1 - _x0) * 0.5, _y0, _x1 - (_x1 - _x0) * 0.5, _y1, _x1, _y1)
    _fp2.lineTo(583, 12); _fp2.lineTo(12, 12); _fp2.close()
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

    # the yellow board frame — everything is pinned inside it
    c.setStrokeColor(HexColor('#FFC93C')); c.setLineWidth(10); c.rect(7, 7, W - 14, H - 14, stroke=1, fill=0)

    for _fx, _fy in _tiny_flowers:
        flower1(_fx, _fy, 0.52, True)
    # ---------- 1. header: identity + overall ----------
    text(M, H - 46, '英语口语测评报告', DISP, 25, INK)
    text(M, H - 68, f"姓名 {d['name']} · 课题 {d['topic']} · 录音 {d['secs']} · {d['date']}", 'SCS', 10.5, INK)
    # small photo, top right: rounded, yellow-framed (kindergarten album)
    pw2, ph2 = 80, 94
    px2, py2 = 488, H - 127
    c.setFillColor(HexColor('#E8B93A')); c.rect(px2 - 2, py2 - 8, pw2 + 10, ph2 + 10, stroke=0, fill=1)
    c.setFillColor(CARD); c.rect(px2 - 5, py2 - 5, pw2 + 10, ph2 + 10, stroke=0, fill=1)
    cover_image(os.path.join(CASE, d['img']), px2 + 2.5, py2 + 2.5, pw2 - 5, ph2 - 5)
    c.setStrokeColor(YEL); c.setLineWidth(2.2)
    c.setStrokeColor(HexColor('#E1E6EC')); c.setLineWidth(0.8); c.rect(px2 - 5, py2 - 5, pw2 + 10, ph2 + 10, stroke=1, fill=0)
    tape(px2 + pw2 / 2, py2 + ph2 + 4, 36, 11, -5, '#FFFFFF')
    oy = H - 96
    # ---------- 2. the hexagon, first ----------
    hy = oy - 14
    head(hy, '六个维度')
    R = 72; cx0, cy0 = M + 118, hy - 118
    order = [0, 1, 2, 5, 4, 3]  # 词汇 句式 完整 / 语调 流利 发音 around the ring
    def _pt(i, r):
        a = math.radians(90 - i * 60)
        return (cx0 + r * math.cos(a), cy0 + r * math.sin(a))
    for ring in range(1, 6):
        outer = ring == 5
        c.setStrokeColor(HexColor('#A9BAC9') if outer else FAINT); c.setLineWidth(1.7 if outer else 0.8)
        pp = c.beginPath()
        for i in range(6):
            x, y = _pt(i, R * ring / 5)
            pp.moveTo(x, y) if i == 0 else pp.lineTo(x, y)
        pp.close(); c.drawPath(pp, stroke=1, fill=0)
    for i in range(6):
        x, y = _pt(i, R); c.setStrokeColor(FAINT); c.setLineWidth(0.8); c.line(cx0, cy0, x, y)
        c.setFillColor(HexColor('#A9BAC9')); c.circle(x, y, 1.7, stroke=0, fill=1)
    c.setFillColor(HexColor('#A9BAC9')); c.circle(cx0, cy0, 2, stroke=0, fill=1)
    def _data(off=0):
        pp = c.beginPath()
        for k, di in enumerate(order):
            x, y = _pt(k, R * d['dims'][di][2] / 5)
            pp.moveTo(x, y + off) if k == 0 else pp.lineTo(x, y + off)
        pp.close(); return pp
    c.setFillColor(HexColor('#90A4B8')); c.setFillAlpha(0.30); c.drawPath(_data(-2.5), stroke=0, fill=1); c.setFillAlpha(1)
    pp = _data()
    c.setFillColor(HexColor('#F09A2E')); c.setFillAlpha(0.30); c.drawPath(pp, stroke=0, fill=1); c.setFillAlpha(1)
    c.setStrokeColor(HexColor('#ED8F24')); c.setLineWidth(2.2); c.setLineJoin(1); c.drawPath(pp, stroke=1, fill=0); c.setLineJoin(0)
    for k, di in enumerate(order):
        x, y = _pt(k, R * d['dims'][di][2] / 5)
        c.setFillColor(HexColor('#ED8F24')); c.circle(x, y, 3.6, stroke=0, fill=1)
        c.setStrokeColor(CARD); c.setLineWidth(1.6); c.circle(x, y, 3.6, stroke=1, fill=0)
    for k, di in enumerate(order):
        nm, wd, n = d['dims'][di][0], d['dims'][di][1], d['dims'][di][2]
        lx, ly = _pt(k, R + 30)
        textC(lx, ly + 9, nm, 'SCB', 10.5, INK)
        textC(lx, ly - 5, wd, 'SCS', 9.5, GREY)
    # overview beside the chart
    ox = M + 268
    text(ox, hy - 24, '总览', 'SCB', 11, INK)
    yy = hy - 44
    for ln in d['overview']:
        yy = para(ox, yy, ln, 'SCS', 10, INK, maxw=W - M - ox, leading=13.5) - 4

    # ---------- 3. interpretation, dimension by dimension ----------
    iy = cy0 - 150
    head(iy, '逐项解读')
    for i, (nm, wd, n, desc) in enumerate(d['dims']):
        gx = M + (i % 2) * 272; gy = iy - 27 - (i // 2) * 57
        text(gx, gy, nm, 'SCB', 11, INK)
        text(gx + sw(nm, 'SCB', 11) + 8, gy, wd, 'SCS', 10, INK)
        flowers(gx + 168, gy + 3, n, 0.72)
        para(gx, gy - 14, desc, 'SCS', 9.5, INK, maxw=222, leading=12.5)

    # ---------- 4. what to do next ----------
    ny = iy - 27 - 3 * 57 - 14
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
    gy = ny - 60
    text(M, gy, '在家练', 'SCB', 11, INK)
    for j, (gn, gd) in enumerate(d['games']):
        bx = M + 64
        c.setFillColor(YEL); c.circle(bx + 6, gy + 3.5, 7, stroke=0, fill=1)
        textC(bx + 6, gy, str(j + 1), 'ENB', 8.5, INK)
        text(bx + 20, gy, gn, 'SCB', 10.5, INK)
        para(M + 168, gy, gd, 'SCS', 10, INK, maxw=CW - 168, leading=13)
        gy -= 20

    # ---------- 5. appendix: the transcript ----------
    ay = gy - 14
    c.setFillColor(HexColor('#E4E9EF')); c.rect(M - 9, ay - 63, CW + 22, 80, stroke=0, fill=1)
    c.setFillColor(HexColor('#FFFDF5')); c.rect(M - 12, ay - 60, CW + 22, 80, stroke=0, fill=1)
    c.setStrokeColor(HexColor('#F0EAD8')); c.setLineWidth(0.8); c.rect(M - 12, ay - 60, CW + 22, 80, stroke=1, fill=0)
    tape(W / 2, ay + 19, 40, 11, 2)
    text(M, ay, f"附：{d['pro']}说的话（全文）", 'SCB', 10.5, GREY)
    para(M, ay - 15, d['script'], 'ENR', 9.5, INK, maxw=CW, leading=13)
    _fr = '参照剑桥 Starters 与 IELTS 口语标准'
    text(W - M - sw(_fr, 'SCS', 8), 26, _fr, 'SCS', 8, INK)
    c.showPage(); c.save()
    print('saved', d['out'])

render(CHILD)
