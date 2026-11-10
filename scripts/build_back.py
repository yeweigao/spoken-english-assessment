# -*- coding: utf-8 -*-
"""Page 2: benchmark alignment table, Swiss style — the technical substantiation page (for parents to see)."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

BASE = os.path.dirname(os.path.abspath(__file__))
# --- skill packaging: fonts live in ../assets/fonts, case data (audio_data.json) in the CWD ---
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))
CASE = os.getcwd()

pdfmetrics.registerFont(TTFont('SCR', os.path.join(FONTDIR, 'NotoSC-Regular.ttf')))
pdfmetrics.registerFont(TTFont('SCB', os.path.join(FONTDIR, 'NotoSC-SemiB.ttf')))
pdfmetrics.registerFont(TTFont('ENR', os.path.join(FONTDIR, 'Inter-Reg.ttf')))
pdfmetrics.registerFont(TTFont('ENB', os.path.join(FONTDIR, 'Inter-BoldF.ttf')))
INK = HexColor('#111111'); GRAY = HexColor('#555555'); HAIR = HexColor('#9AA4AD'); RED = HexColor('#E30613')

def st(name, font, size, lead, color=INK, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead, textColor=color, **kw)
sKick = st('k', 'ENB', 8.5, 10.5)
sTitle = st('t', 'SCB', 25, 28)
sMeta = st('m', 'SCR', 8.5, 11.5, GRAY, alignment=2)
sIntro = st('i', 'SCR', 9.5, 13.5)
sSec = st('sec', 'SCB', 11, 14)
sH = st('h', 'SCB', 7.5, 10, GRAY)
sDim = st('dim', 'SCB', 10, 12.5)
sC = st('c', 'SCR', 8.5, 12)
sNote = st('n', 'SCR', 8.5, 12.5, GRAY)
sBig = st('big', 'ENB', 13, 15)
sLab = st('lab', 'SCR', 8, 10.5, GRAY)
sFoot = st('f', 'SCR', 7.5, 10, GRAY)

def rule(h=2.6, color=INK):
    t = Table([['']], colWidths=[511], rowHeights=[h])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), color),
                           ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                           ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0)]))
    return t

OUT = os.path.join(CASE, 'report-back.pdf')
doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=42, rightMargin=42, topMargin=36, bottomMargin=24,
                        title='维度对标表（报告背面）', author='Muse')
E = []
head = Table([
    [Paragraph('<font color="#E30613">■</font>  SPEAKING ASSESSMENT — BENCHMARK MAP', sKick),
     Paragraph('', sMeta)],
    [Paragraph('维度对标表', sTitle),
     Paragraph('2026-11-09<br/>依据录音：Toto《My Funny Face》37 秒', sMeta)],
], colWidths=[340, 171])
head.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
                          ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                          ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1)]))
E.append(head); E.append(Spacer(1, 7)); E.append(rule()); E.append(Spacer(1, 9))
E.append(Paragraph('定位：<b>维度与量规层面的对标，不是分数换算</b>——本报告结果不与任何官方考试成绩等效。对标的作用，是让正面报告的每一项评分都找得到权威量规的出处。六个维度分两组：01–03 评内容，04–06 评声音（技术指标见页下）。', sIntro))
E.append(Spacer(1, 10))
rows = [
    ('01', '词汇', 'Lexical Resource<br/>词汇资源',
     'Starters 主题词表：身体与脸、颜色、数字；CEFR A1：能运用与具体日常需求有关的基础词汇。',
     '身体部位 5 个、颜色 5 种、数字 3 个，全部用在对的地方；可提升点：big 一词用 5 次。'),
    ('02', '句式与语法', 'Grammatical Range<br/>&amp; Accuracy<br/>语法多样性与准确性',
     'Starters 结构清单：名词单复数、this / these 指示词、形容词置于名词前、物主限定词 my。',
     '六句零语法错误：this 配单数、these 配复数无一次混淆；big round yellow 形容词顺序正确（已超出 Starters 的要求）。'),
    ('03', '完整与创意', 'Fluency &amp; Coherence<br/>中的内容连贯与展开',
     'Starters can-do：能就熟悉的话题说出短句、能逐项描述一个人或物。',
     '结构完整：自我介绍 → 逐项介绍五官 → 自创句收尾；末句 I love the ugly, silly and scary me 为自创，三连形容词。'),
    ('04', '发音准确度', 'Pronunciation<br/>发音：可懂度与音素准确性',
     'CEFR Pre-A1–A1 语音控制：所学词句的发音能被熟悉这类说话者的人理解（意译要点）。',
     '三套独立识别系统都听出了全文大意；分歧点在词尾辅音：mouth 被听成 mouse（词尾 /θ/）、oval 未被任何一套听出（/v/）、silly 被听成 city；谐噪比 17.9 dB。'),
    ('05', '流利度', 'Fluency &amp; Coherence<br/>流利与连贯',
     'CEFR A1：能以短句表达，其间有为找词而作的停顿（意译要点）。',
     '无填充词、无重说；停顿都躲在句中：想词 0.9 秒（three 前）、1.2 秒（pink 前）、2.8 秒（oval 句）；构音语速约 2.5 音节/秒。'),
    ('06', '语调与重音', 'Pronunciation<br/>发音：语调、重音与节奏（该标准明列项）',
     'CEFR Pre-A1–A1 韵律：能用所学短句的基本语调达意（意译要点）。',
     '基频实测：句尾 6 处全为降调；音高跨度 12.9 半音（超一个八度）；双音节词重音实测：yellow 等词两音节近等重（差 ≤1 dB），重音尚未站出来。'),
]
data = [[Paragraph('维度 DIMENSION', sH), Paragraph('IELTS 口语标准', sH),
         Paragraph('剑桥 STARTERS / CEFR 参照', sH), Paragraph('本报告的证据 EVIDENCE', sH)]]
for num, dim, ielts, ref, ev in rows:
    data.append([Paragraph(f'<font color="#E30613">{num}</font><br/><br/>{dim}', sDim),
                 Paragraph(ielts, sC), Paragraph(ref, sC), Paragraph(ev, sC)])
t = Table(data, colWidths=[66, 100, 158, 187], repeatRows=1)
t.setStyle(TableStyle([
    ('LINEABOVE', (0, 0), (-1, 0), 1.6, INK), ('LINEBELOW', (0, 0), (-1, 0), 0.7, INK),
    ('LINEBELOW', (0, 1), (-1, -2), 0.45, HAIR), ('LINEBELOW', (0, -1), (-1, -1), 1.6, INK),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
E.append(t)
E.append(Spacer(1, 12))
E.append(Paragraph('本次录音的技术指标（原生音频实测）', sSec)); E.append(Spacer(1, 4))
cells = [
    ('2.5', '音节/秒', '构音语速（不含停顿）'),
    ('0', '次', '填充词（呃、啊）；自我修正 0 次'),
    ('2.8', '秒', '句中最长停顿（oval 句）'),
    ('6/6', '句', '句尾降调（基频实测）'),
    ('12.9', '半音', '音高跨度，超一个八度'),
    ('17.9', 'dB', '谐噪比（声音清晰度）'),
]
grid = []
for i in range(0, 6, 3):
    row = []
    for big, unit, lab in cells[i:i + 3]:
        row.append([Paragraph(f'<font size="13">{big}</font> <font size="8.5">{unit}</font>', sBig),
                    Paragraph(lab, sLab)])
    grid.append(row)
gt = Table([[[c[0], c[1]] for c in r] for r in grid], colWidths=[170, 170, 171])
# flatten: build simpler - each cell a single paragraph with two lines
grid2 = []
for i in range(0, 6, 3):
    row = []
    for big, unit, lab in cells[i:i + 3]:
        row.append(Paragraph(f'<font face="ENB" size="13">{big}</font> <font face="SCR" size="8.5">{unit}</font><br/><font color="#555555" size="8.5">{lab}</font>', sC))
    grid2.append(row)
gt = Table(grid2, colWidths=[170, 170, 171])
gt.setStyle(TableStyle([
    ('LINEABOVE', (0, 0), (-1, 0), 1.6, INK), ('LINEBELOW', (0, 0), (-1, 0), 0.7, INK),
    ('LINEBELOW', (0, -1), (-1, -1), 1.6, INK),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
E.append(gt)
E.append(Spacer(1, 10))
E.append(Paragraph('方法注：内容部分看孩子实际所说的话是否准确、完整；声音部分直接测量录音本身（音高、停顿、清晰度、响度），发音判断来自实测，不靠转写猜测。评分由量规锚定，结果以小红花分档呈现——参照剑桥少儿英语以「盾牌」计数代替分数的做法。本报告为日常形成性测评，非官方考试成绩。', sNote))
doc.build(E)
print('saved', OUT)
