# -*- coding: utf-8 -*-
"""维度对标表 — substantiation document for the speaking assessment's alignment claims."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

BASE = os.path.dirname(os.path.abspath(__file__))
# --- skill packaging: fonts live in ../assets/fonts, case data (audio_data.json) in the CWD ---
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))
CASE = os.getcwd()

pdfmetrics.registerFont(TTFont('SCR', os.path.join(FONTDIR, 'NotoSC-Regular.ttf')))
pdfmetrics.registerFont(TTFont('SCB', os.path.join(FONTDIR, 'NotoSC-SemiB.ttf')))
pdfmetrics.registerFont(TTFont('ENR', os.path.join(FONTDIR, 'Inter-Reg.ttf')))
pdfmetrics.registerFont(TTFont('ENB', os.path.join(FONTDIR, 'Inter-BoldF.ttf')))

INK = HexColor('#14181D'); SUB = HexColor('#43536B'); BLUE = HexColor('#2F7FC1')
LINE = HexColor('#C9D4E0'); BAND = HexColor('#F2F6FA'); RED = HexColor('#C73E1D')

def st(name, font, size, lead, color=INK, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=lead, textColor=color, **kw)
sTitle = st('t', 'SCB', 19, 24)
sSub = st('sub', 'SCR', 9.5, 13.5, SUB)
sH = st('h', 'SCB', 8.5, 11, HexColor('#FFFFFF'))
sC = st('c', 'SCR', 8.6, 12.2)
sCd = st('cd', 'SCB', 9.2, 12.5)
sNote = st('n', 'SCR', 8.6, 12.6, SUB)
sClaim = st('cl', 'SCR', 8.6, 12.4)

OUT = os.path.join(CASE, 'benchmark-internal.pdf')
doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=34, bottomMargin=30,
                        title='口语测评维度对标表', author='Muse')
E = []
E.append(Paragraph('口语测评维度对标表', sTitle))
E.append(Paragraph('本报告六个评分维度 × IELTS 口语四项标准 × 剑桥少儿英语 Starters 量规 × CEFR（Pre-A1–A1）', sSub))
E.append(Paragraph('定位：这是<b>维度与量规层面的对标</b>，不是分数换算——本报告结果不与任何官方考试成绩等效。对标的用途是让每项评分都找得到权威量规的出处，让宣传表述有据可查。', sNote))
E.append(Spacer(1, 8))

rows = [
    ('词汇', 'Lexical Resource<br/>词汇资源',
     'Starters 主题词表：身体与脸、颜色、数字；CEFR A1：能运用与具体日常需求有关的基础词汇。',
     '身体部位 5 个、颜色 5 种、数字 3 个，全部用在对的地方；可提升点：big 一词用 5 次，大小全靠它。'),
    ('句式与语法', 'Grammatical Range<br/>&amp; Accuracy<br/>语法多样性与准确性',
     'Starters 结构清单：名词单复数、this / these 指示词、形容词置于名词前、物主限定词 my。',
     '六句零语法错误：this 配单数、these 配复数无一次混淆；big round yellow 形容词顺序正确（已超出 Starters 的要求）。'),
    ('完整与创意', 'Fluency &amp; Coherence<br/>中的内容连贯与展开',
     'Starters can-do：能就熟悉的话题说出短句、能逐项描述一个人或物。',
     '结构完整：自我介绍 → 逐项介绍五官 → 自创句收尾；末句 I love the ugly, silly and scary me 为自创，三连形容词。'),
    ('发音准确度', 'Pronunciation<br/>发音：可懂度与<br/>音素准确性',
     'CEFR Pre-A1–A1 语音控制：所学词句的发音能被熟悉这类说话者的人理解（意译要点）。',
     '三套独立识别系统交叉核对，分歧点定位到具体音素：词尾 /θ/（mouth 被听成 mouse）、/v/（oval 未被听出）；声音清晰度实测（谐噪比 17.9 dB）。'),
    ('流利度', 'Fluency &amp; Coherence<br/>流利与连贯',
     'CEFR A1：能以短句表达，其间有为找词而作的停顿（意译要点）。',
     '全程无填充词（呃、啊）、无重说；停顿按波形实测定点：句中想词 0.9 / 1.2 / 2.8 秒，句间停顿短；构音语速约 2.5 音节/秒。'),
    ('语调与重音', 'Pronunciation<br/>发音：语调、重音<br/>与节奏（该标准明列项）',
     'CEFR Pre-A1–A1 韵律：能用所学短句的基本语调达意（意译要点）。',
     '基频实测：句尾 6/6 全为降调；音高跨度 12.9 个半音（超一个八度）；双音节词前后半强度差实测，yellow 等词两音节近等重（差 ≤1 dB），重音未分化。'),
]
data = [[Paragraph('本报告维度', sH), Paragraph('IELTS 口语标准', sH), Paragraph('剑桥 Starters / CEFR 参照', sH), Paragraph('本报告的证据（以 Toto 本次录音为例）', sH)]]
for a, b, c_, d in rows:
    data.append([Paragraph(a, sCd), Paragraph(b, sC), Paragraph(c_, sC), Paragraph(d, sC)])
t = Table(data, colWidths=[64, 104, 168, 187], repeatRows=1)
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), BLUE),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), BAND]),
    ('GRID', (0, 0), (-1, -1), 0.6, LINE),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
E.append(t)
E.append(Spacer(1, 9))
E.append(Paragraph('方法注：内容侧据录音转写逐句核对原文；声音侧据<b>原生音频</b>声学实测（基频、停顿、谐噪比、强度）与多系统识别交叉核对，未以转写推断发音结论。本方案<b>未采用</b>音素级 GOP 评分，也未用真人考官语料校准的打分模型——结果呈现为小红花分档（参照剑桥少儿以「盾牌」计数代替分数的做法），不产生可与官方考试互换的分数。', sNote))
E.append(Spacer(1, 10))
claims = [
    [Paragraph('<b>宣传可用（有据）</b>', sClaim), Paragraph('<b>不可使用（红线）</b>', sClaim)],
    [Paragraph('· 评分维度对标 IELTS 口语四项标准<br/>· 量规参照剑桥少儿英语 Starters 与 CEFR Pre-A1–A1<br/>· 原生音频声学分析，与自动评分系统相同的特征路线（语速 / 停顿 / 基频 / 清晰度）<br/>· 以图标分档呈现结果，不给低龄孩子打具体分数', sClaim),
     Paragraph('· 「剑桥 / 雅思 / 托福同款技术」「同款 AI 考官」——无 GOP、无校准模型，不实<br/>· 「分数可与官方考试换算 / 等效」——无效度研究支撑<br/>· 将上述机构名称、标志用作背书——仅可描述性提及「参照 / 对标」', sClaim)],
]
ct = Table(claims, colWidths=[261.5, 261.5])
ct.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), BAND),
    ('BOX', (0, 0), (-1, -1), 0.6, LINE), ('INNERGRID', (0, 0), (-1, -1), 0.6, LINE),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
E.append(ct)
E.append(Spacer(1, 8))
E.append(Paragraph('对标表 v1 · 2026-11-09 · 依据录音：Toto《My Funny Face》（37 秒）实测与逐句核对结果', sNote))
doc.build(E)
print('saved', OUT)
