#!/usr/bin/env python3
"""The editable companion of the simple page: report-simple.pptx (one A4 portrait slide).

Called by build_simple.py after the PDF is saved. It renders the same page a second time with
every piece of text left out — that drawing (frame, sun, photo, radar, flowers, cards, the voice
hill …) becomes ONE picture filling the slide, locked in place behind everything. Then every piece
of text goes on top as a real text box, at the same spot, in the same font, size and colour:
paragraphs are single boxes that rewrap as the teacher types, the overview's bold lead-ins and
the goal's dashed red practice words are runs inside their paragraph, and the verdict stamps are
editable rounded boxes. Opens in PowerPoint, WPS and Keynote; export to PDF from there.

Fonts are named, not embedded (Office can't take them from a script): the three in assets/fonts
(Noto Sans SC Regular + SemiBold, ZCOOL KuaiLe) ship with the skill — run scripts/install_fonts.py
once on the teacher's computer (macOS / Windows, no admin), or the app substitutes its own CJK
font. Needs: python-pptx, pymupdf."""
import os, tempfile
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
import pymupdf

W, H = A4
FAMILY = {'SCS': ('Noto Sans SC', False), 'SCB': ('Noto Sans SC', True), 'ZCOOL': ('ZCOOL KuaiLe', False),
          'ENR': ('Inter', False), 'ENB': ('Inter', True)}
ASC = 0.80          # where PowerPoint puts the first baseline inside an exact-spaced line, as a share of the line
E = lambda pt: Emu(int(round(pt * 12700)))

# The PDF needs a typed space between Chinese and English ("七个 magic e 核心词"); PowerPoint, WPS and
# Keynote add that gap themselves, so in the PPT the typed space would double it. Drop a space that
# sits between a Chinese character or full-width mark and a Latin letter or digit, either way round.
import re as _re
_CJK = '\u3000-\u303f\u3400-\u9fff\uff00-\uffef'
_GAP = _re.compile(rf'(?<=[{_CJK}]) +(?=[A-Za-z0-9])|(?<=[A-Za-z0-9.,!?\'"]) +(?=[{_CJK}])')
def despace(s):
    return _GAP.sub('', s)

def despace_runs(texts):
    """Same rule across run boundaries (a dashed practice word is its own run)."""
    out = [despace(t) for t in texts]
    for i in range(len(out)):
        prev = out[i - 1][-1:] if i else ''
        nxt = out[i + 1][:1] if i + 1 < len(out) else ''
        if prev and out[i].startswith(' ') and _GAP.search(prev + ' ' + out[i].lstrip(' ')[:1]):
            out[i] = out[i].lstrip(' ')
        if nxt and out[i].endswith(' ') and _GAP.search(out[i].rstrip(' ')[-1:] + ' ' + nxt):
            out[i] = out[i].rstrip(' ')
    return out

def _font(run, f, size, color, underline_dash=False):
    fam, bold = FAMILY.get(f, ('Noto Sans SC', False))
    fo = run.font
    fo.size = Pt(size); fo.bold = bold; fo.color.rgb = RGBColor.from_string(color); fo.name = fam
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):                          # Chinese needs the east-asian slot named too
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {}); rPr.append(el)
        el.set('typeface', fam)
    if underline_dash:                                    # practice word: dashed red underline, as on the PDF
        rPr.set('u', 'dash')
        uf = rPr.makeelement(qn('a:uFill'), {}); sf = uf.makeelement(qn('a:solidFill'), {})
        clr = sf.makeelement(qn('a:srgbClr'), {'val': 'E4572E'}); sf.append(clr); uf.append(sf)
        latin = rPr.find(qn('a:latin'))
        (latin.addprevious(uf) if latin is not None else rPr.append(uf))

def _box(slide, x, top, w, h, rot, wrap_):
    tb = slide.shapes.add_textbox(E(x), E(top), E(w), E(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = wrap_; tf.auto_size = MSO_AUTO_SIZE.NONE; tf.vertical_anchor = MSO_ANCHOR.TOP
    if rot: tb.rotation = -rot                            # ReportLab turns counter-clockwise, Office clockwise
    return tf

def build(d, render, out, wrap):
    items = []
    tmp = tempfile.mkdtemp()
    bg_pdf, bg_png = os.path.join(tmp, 'bg.pdf'), os.path.join(tmp, 'bg.png')
    render(d, capture=items, out=bg_pdf)                  # the page without its words
    page = pymupdf.open(bg_pdf)[0]
    page.get_pixmap(dpi=250).save(bg_png)

    prs = Presentation()
    prs.slide_width, prs.slide_height = E(W), E(H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    pic = slide.shapes.add_picture(bg_png, 0, 0, prs.slide_width, prs.slide_height)
    pic.name = '底图（插画与图形，勿动）'

    for it in items:
        if it['t'] == 'line':
            lead = it['size'] * 1.25
            w = pdfmetrics.stringWidth(it['s'], it['f'], it['size']) + it['size'] * 0.6
            tf = _box(slide, it['x'], H - it['y'] - ASC * lead, w, lead, it['rot'], False)
            p = tf.paragraphs[0]; p.line_spacing = Pt(lead)
            r = p.add_run(); r.text = despace(it['s']); _font(r, it['f'], it['size'], it['color'])
        elif it['t'] == 'para':
            lead = it['leading']
            text = ''.join(r_[0] for r_ in it['runs'])
            n = max(1, len(wrap(text, 'SCS', it['size'], it['maxw'])))
            tf = _box(slide, it['x'], H - it['y'] - ASC * lead, it['maxw'] + 3, n * lead, it['rot'], not it.get('nowrap'))
            p = tf.paragraphs[0]; p.line_spacing = Pt(lead)
            for (s_, f_, ul), t_ in zip(it['runs'], despace_runs([r_[0] for r_ in it['runs']])):
                r = p.add_run(); r.text = t_; _font(r, f_, it['size'], it['color'], ul)
        elif it['t'] == 'stamp':
            sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, E(it['x']), E(H - it['y'] - it['h']), E(it['w']), E(it['h']))
            sh.adjustments[0] = 0.5
            sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            sh.line.color.rgb = RGBColor.from_string(it['color']); sh.line.width = Pt(0.7)
            st_ = sh._element.find(qn('p:style'))                # the default theme style carries a drop shadow
            if st_ is not None: sh._element.remove(st_)
            sh.rotation = -it['rot']
            tf = sh.text_frame
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.word_wrap = False; tf.auto_size = MSO_AUTO_SIZE.NONE; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
            r = p.add_run(); r.text = it['s']; _font(r, 'ZCOOL', 10, it['color'])
    prs.save(out)
    print('saved', os.path.basename(out), '（可编辑版：PowerPoint / WPS / Keynote 打开改字，再导出 PDF）')
