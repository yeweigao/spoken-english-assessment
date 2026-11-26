#!/usr/bin/env python3
"""Report SIMPLE page (one A4 page for parents — the quick-read companion
to the two-page detailed report; same measurements, same flower counts).

Order follows the normal assessment-report genre: identity -> six-dimension
radar with a plain-language overview -> per-dimension readings -> the
teacher's note (only when a real one was supplied) -> next steps (goal + home
games) -> appendix: the full transcript. Design law (full spec in
references/type-system.md, section 简版一页):
- ONE pale field over the whole top, ending in a drawn wave with two clouds on
  the seam; ONE strong tone (frame + the ray sun, built as a flat disc with
  twelve pill rays, centre off the top-right corner); the child's photo print
  sits on the sun (cover-fit: crop, never stretch). The palette comes from
  case.json `theme` — six macaron sets in THEMES; red flowers and the practice
  underlines keep their meaning and do not change with the theme.
- Radar data in the theme's deep tone; red is reserved for earned flowers and
  the practice-word underline, which appear ONLY where they carry that meaning.
  No overall grade line and no invented framework tiers.
- 老师说 is always there, signed with the name the teacher gives: the AI writes it as the child's
  stage summary of spoken English with real encouragement — not a replay of this video, no
  "I watched the video", nothing that puts the teacher in the room (the parent filmed it).
- Everything on the page judges the child's spoken English level only: a song, a show or a game
  is just the carrier of the evidence, never judged as singing or acting.
- Say each thing once: the radar carries dimension names only (the verdict
  word lives in the readings), the overview speaks in conclusions without
  measurements, the readings carry the evidence. validate() enforces this.
- Illustrations are all hand-drawn flat vector shapes in one family (rounded,
  matte, no emoji, no gloss): sun, clouds, flowers, and the bottom scene — the child's own
  recording drawn as a hill of rounded waveform bars, a speech bubble where her voice begins, and plants growing on the
  loudest crests from seedling to bloom (no trees, no row of unrelated icons, no red).
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

# ===== macaron themes, chosen per case in case.json "theme" (default cream) =====
# Each set: field = the pale wash over the top, sun/frame = the strong tone,
# radar = a readable deep tone of the same family, plus the paper tints of
# the goal chip and the transcript box. Red stays fixed: it carries meaning
# (earned flowers, practice-word underline) and never becomes a theme colour.
THEMES = {
    'cream': dict(label='奶油黄', field='#FFF9EA', sun='#FFD65A', frame='#FFC93C',
                  tape='#FFE9A8', chip_shadow='#E7ECF1', chip_line='#EFE9DC',
                  box_shadow='#E4E9EF', box_fill='#FFFDF5', box_line='#F0EAD8',
                  radar_fill='#F09A2E', radar_line='#ED8F24', quote='#DFA32A', hill1='#E3F0DB', hill2='#CDE6BE', bush='#A9D18E', leaf='#7CB342', trunk='#8D6E63'),
    'mint': dict(label='薄荷绿', field='#E7F7EE', sun='#7FD2AB', frame='#5FB78D',
                 tape='#CDEDDF', chip_shadow='#E2EFE9', chip_line='#D7EADF',
                 box_shadow='#E1EFE8', box_fill='#FBFFFC', box_line='#DAEDE4',
                 radar_fill='#3E9E7A', radar_line='#2F8767', quote='#4E9A7D', hill1='#DFF2E8', hill2='#C7E7D7', bush='#A3D6BE', leaf='#62BB92', trunk='#8C7B6C'),
    'sakura': dict(label='樱花粉', field='#FFEEF2', sun='#FFA4BC', frame='#EE8FA8',
                   tape='#FFD9E2', chip_shadow='#F5E6EA', chip_line='#F4DEE4',
                   box_shadow='#F5E6EA', box_fill='#FFFCFD', box_line='#F6E2E8',
                   radar_fill='#D4698A', radar_line='#C15578', quote='#D0738F', hill1='#FDEBF0', hill2='#F9D7E2', bush='#F4BFD0', leaf='#EE8FA8', trunk='#B0897C'),
    'sky': dict(label='云朵蓝', field='#EAF5FD', sun='#93CBEA', frame='#6FB6DE',
                tape='#CFE9F7', chip_shadow='#E5EFF5', chip_line='#DAE9F2',
                box_shadow='#E4EEF4', box_fill='#FCFFFF', box_line='#DCECF4',
                radar_fill='#3D8FC0', radar_line='#2F7BA9', quote='#4C90B8', hill1='#E4F2FA', hill2='#CDE7F4', bush='#A8D5E9', leaf='#6FB6DE', trunk='#8C7B6C'),
    'lilac': dict(label='薰衣草', field='#F1ECFA', sun='#C3A9E6', frame='#A88CD8',
                  tape='#E3D8F6', chip_shadow='#EAE6F1', chip_line='#E3DCF0',
                  box_shadow='#EAE6F1', box_fill='#FEFDFF', box_line='#E6DFF1',
                  radar_fill='#7A5BB5', radar_line='#684CA1', quote='#7E63B0', hill1='#F0EAF9', hill2='#E0D6F1', bush='#CBB9E7', leaf='#A88CD8', trunk='#9A8578'),
    'peach': dict(label='蜜桃橙', field='#FFF0E6', sun='#FFB68F', frame='#F79B6C',
                  tape='#FFDCC8', chip_shadow='#F5E8E0', chip_line='#F6E0D4',
                  box_shadow='#F5E8E0', box_fill='#FFFCFA', box_line='#F7E3D9',
                  radar_fill='#DD7742', radar_line='#C9652F', quote='#D2743C', hill1='#FDEDE1', hill2='#F8D8C3', bush='#F5C2A4', leaf='#F49A6F', trunk='#A8785C'),
}

def sw(t, f, s): return pdfmetrics.stringWidth(t, f, s)
CLOSE = '，。、；：！？）」』”’》〕…·'
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
    if (len(lines) > 1 and lines[-1].isascii() and lines[-2].isascii()        # English lines only: a Chinese
            and len(lines[-1].split()) < 2 and len(lines[-2].split()) > 3):     # line has no spaces to count
        head, last = lines[-2].rsplit(' ', 1)
        lines[-2], lines[-1] = head, last + ' ' + lines[-1]
    return lines

# ===== CASE DATA lives in the case directory, never in this script:
#   python3 build_simple.py [case.json]      (default: ./case.json; photo, audio_data.json beside it)
# Fields: name, pro (她/他), topic, date, task ("speak" | "read"), photo, theme (six macaron
# keys), overview[2–4], mark[], dims[6 × [name, verdict word, flowers, reading]], goal,
# games[3 × [name, how]], script, teacher{comment, sign} (optional, real source only).
# The recording length on the page comes from audio_data.json (50 ms windows), so it can't drift.
import sys
CASE_FILE = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), 'case.json'))
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
    d.setdefault('theme', 'cream')
    ad = os.path.join(CASE, 'audio_data.json')
    if not os.path.isfile(ad) and d.get('audio'):
        # take the loudness envelope here, on this machine: it only shapes the bottom hill and
        # never prints a number — the listening route can use it without becoming a measurement
        _src = os.path.join(CASE, d['audio'])
        if os.path.isfile(_src):
            try:
                import extract_audio_data
                _dat = extract_audio_data.extract(_src)
                json.dump({'peaks': _dat['peaks'], 'f0': _dat['f0']}, open(ad, 'w'))
                print(f"（波形：本机取 {len(_dat['peaks'])} 段包络 → audio_data.json，不上云、不印数字）")
            except Exception as _e:
                print(f'（波形：{d["audio"]} 取不到包络（{_e}），底部只画平缓山坡）')
    if os.path.isfile(ad):
        d['secs'] = fmt_secs(len(json.load(open(ad))['peaks']) * 0.05)
    elif 'secs' not in d:
        raise SystemExit('缺录音时长：放入 audio_data.json（extract_audio_data.py 生成），或在 case.json 写 secs')
    return d

M = 48; CW = W - 2 * M
E = 18                       # inner edge of the board frame: kept inside a home printer's printable area
FOOT_TOP = 72                # the fine-print band (logos + standards) runs from the frame up to here
FLOOR = 116                  # content stops above this: the voice hill and its plants live below
BRAND = os.path.normpath(os.path.join(BASE, '..', 'assets', 'brand'))
OVER_X = M + 268             # overview / teacher's-note column
OVER_W = W - M - OVER_X
NOTE_X = OVER_X + 4          # the sticky note sits a hair inside the column
NOTE_W = W - M - NOTE_X - 6
NOTE_LEAD = 13
COLX = (M, M + 272)          # readings: content dimensions left, sound dimensions right
DESC_W = 222
MEASURE = re.compile(r'\d+(\.\d+)?\s*(秒|个词|个半音|半音|音节|次|个|%|dB|分贝|Hz)')
# 老师说 is the child's stage summary with encouragement, not a review of this video. Words that put
# the teacher (or an audience) in the room give the report away to the parent who filmed it;
# narrating the viewing or the moment (今天、刚才) turns a summary back into a replay
IN_ROOM = re.compile(r'课上|课堂|班上|全班|小朋友们|大家|现场|当场|在场|台下|台上|听众|观众|我们班|我在旁边'
                     r'|看(了|完).{0,40}?(视频|录音)|(这段|这次|这个)(视频|录音)|视频里|录音里|今天|刚才|一开口')
# a song or a show is only the carrier of the evidence: the conclusions are English ability (words,
# sentences, sounds, flow, stress), never how well the song or the show went, nor how it was sung
# or acted (backstops — SKILL.md sets the focus from the first listen)
PERFORMANCE = re.compile(r'唱|歌|表演|节目|演出|舞|手势|动作|一句不落|忘词')
NOT_ENGLISH = re.compile(r'(?<![发读念元辅长短重])音准(?!确)|跑调|走调|调子|唱功|旋律|节拍|拍子|打拍|高音|低音|气息|换气|嗓|舞蹈|动作到位|表演力|台风')

def lead_of(line):
    """'最棒的：…' -> '最棒的：' (a lead-in of up to six characters before a full-width colon)."""
    k = line.find('：')
    return line[:k + 1] if 0 < k <= 6 else ''

def topic_label(d):
    """What the header calls this piece of work. '课题' reads like a textbook unit test, which is
    not what a free performance is; a book gets 篇目, everything else 话题. case.json may override."""
    return d.get('topic_label') or ('篇目' if d.get('task') == 'read' else '话题')

def meta_line(d):
    """The one line under the title: who, what, how long, when."""
    return f"姓名 {d['name']} · {topic_label(d)} {d['topic']} · 录音 {d['secs']} · {d['date']}"

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
    if d.get('img') and not os.path.isfile(os.path.join(CASE, d['img'])):
        raise ValueError(f"找不到照片 {d['img']}：放进案例目录（视频用 pick_frame.py 选一帧），或改 case.json 的 photo")
    if d.get('task', 'speak') not in ('speak', 'read'):
        raise ValueError('task 只能是 speak（自由表达）或 read（朗读现成文本）')
    if d.get('theme') not in THEMES:
        raise ValueError('theme 只能是 ' + ' / '.join(f'{k}（{v["label"]}）' for k, v in THEMES.items()))
    tch = d.get('teacher')
    if not tch:
        raise ValueError('缺老师说：case.json 写 teacher: {comment, sign}——评语由 AI 依本次测评写四五句，署名问老师；简版右栏固定是老师说，没有总览')
    if tch:
        cm = str(tch.get('comment') or '').strip()
        if not cm:
            raise ValueError('teacher.comment 为空：老师说由 AI 依本次测评写四五句')
        if note_height(d) > 150:
            raise ValueError('老师评语放进便利贴超过六行，请精简到四五句')
        m = MEASURE.search(cm)
        if m:
            raise ValueError(f'老师说含测量值「{m.group()}」：数字证据只写在逐项解读里，老师说只说人话')
        for nm, _, _, desc in d['dims']:
            run = common_run(cm, desc)
            if len(run) >= 7:
                raise ValueError(f'老师说与「{nm}」解读重复了「{run}」：换一种说法，或删掉其中一处')
        m = IN_ROOM.search(cm)
        if m:
            raise ValueError(f'老师说写了「{m.group()}」：老师说是孩子这一阶段英语口语的总评加鼓励，不复述这段视频——'
                             f'不写成在场（课上、大家、现场），也不写「看了视频」「录音里」「今天」「刚才」')
    elif not (2 <= len(d.get('overview') or []) <= 4):
        raise ValueError('没有 teacher 时必须写 overview 2–4 条（有老师评语时右栏被评语占用，overview 可省略）')
    if d.get('task') == 'read' and not d.get('original'):
        raise ValueError('朗读案例必须写 original（课文原文）：读错的词只有对着原文才查得出')
    ov = d.get('overview') or []
    if ov and not 2 <= len(ov) <= 4:
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
    for gn, _ in d['games']:
        if sw(gn, 'SCB', 10.5) > 78:                   # the name column runs from M+84 to the description at M+168
            raise ValueError(f'在家练游戏名「{gn}」太长，会压到说明：游戏名控制在五六个字（英文词算两三个字）')
    if len(wrap(d['goal'], 'SCS', 10.5, CW - 90)) > 1: raise ValueError('goal 须一行写完')
    for where, s in ([(f'「{x[0]}」解读', x[3]) for x in d['dims']] + [('老师说', (tch or {}).get('comment', '')), ('小目标', d['goal'])]
                     + [(f'在家练「{g[0]}」', f'{g[0]}：{g[1]}') for g in d['games']]):
        m = PERFORMANCE.search(s) if not where.startswith('在家练') else None
        if m:
            raise ValueError(f'{where}写到了「{m.group()}」：歌和表演只是取证的载体，这里写英语水平——'
                             f'能说出哪些词和句子、哪些音已发准、连不连贯、重音语调，不写歌唱得、节目演得怎么样')
        m = NOT_ENGLISH.search(s)
        if m:
            raise ValueError(f'{where}写到了「{m.group()}」：报告只评英语口语（词、句、发音、流利、语调重音），'
                             f'不评唱得怎么样、演得怎么样；换成英语上的说法或删掉')
    pron = d['dims'][3][3] + d['goal']
    for w_ in d.get('mark', []):
        if not re.search(r'\b' + re.escape(w_) + r'\b', d['script'], re.I):
            raise ValueError(f'mark 里的「{w_}」不在全文里')
        if w_.lower() not in pron.lower():
            raise ValueError(f'mark 里的「{w_}」须同时出现在「发音准确度」解读或小目标里，前后才对得上')
    meta = meta_line(d)
    if M + sw(meta, 'SCS', 10.5) > PHOTO_X - 14:
        raise ValueError('页眉信息行太长，会碰到照片：请缩短题目')
    # pronunciation coaching: diagnose -> the one table -> dictionary check (scripts/coach.py)
    import coach
    coach.check(d)

PHOTO_W, PHOTO_H = 96, 112
PHOTO_X, PHOTO_TOP = W - M - PHOTO_W + 4, H - 28

def note_lines(d):
    tch = d.get('teacher')
    if not tch:
        return []
    return wrap(str(tch['comment']), 'SCS', 9.5, NOTE_W - 48)

def note_height(d):
    """Height of the sticky note: label + comment lines + signature."""
    lines = note_lines(d)
    if not lines:
        return 0
    sign = (d['teacher'].get('sign') or '').strip()
    return 12 + 22 + len(lines) * NOTE_LEAD + (15 if sign else 4) + 10

def right_bottom(d, oy0):
    """Bottom edge of whatever stands in the column right of the radar, and the gap it wants below."""
    if d.get('teacher'):
        return oy0 - note_height(d), 10           # the note's own edge; 10pt of air under it
    yy = oy0 - 21
    for ln in d.get('overview') or []:
        yy -= 14 * len(wrap(ln, 'SCS', 10, OVER_W)) + 4
    return yy, 40

def top_layout(d):
    """Where the top half ends, computed from content — the cream field, the right column and the
    readings heading all follow it, so nothing is pinned to a hand-set y."""
    hy = H - 110                                   # 六个维度 heading
    cy0 = hy - 110                                 # radar centre
    photo_bottom = PHOTO_TOP - PHOTO_H - 8
    oy0 = min(hy - 24, photo_bottom - 22)          # right column starts below the photo print
    yy, gap = right_bottom(d, oy0)
    iy = min(cy0 - 128, yy - gap)                 # 逐项解读 heading
    return dict(hy=hy, cy0=cy0, oy0=oy0, iy=iy, field_bottom=iy + 30)

SUN_R, SUN_C = 138, (W - 30, H - 16)

CAP = None        # set to a list by render(d, capture=...): text is recorded for the PPT instead of drawn

def render(d, capture=None, out=None):
    global CAP
    CAP = capture
    validate(d)
    L = top_layout(d)
    T = THEMES[d['theme']]
    # every font in the file is embedded: start on Noto instead of ReportLab's default (unembedded) Helvetica
    c = canvas.Canvas(out or os.path.join(CASE, d['out']), pagesize=A4, initialFontName='SCS', initialFontSize=10)
    ctx = {'off': (0, 0, 0)}        # page offset + rotation of the frame text is drawn in (sticky note)
    def text(x, y, s, f='SCS', size=10, color=INK):
        if CAP is not None:
            ox_, oy_, rot_ = ctx['off']
            CAP.append(dict(t='line', x=x + ox_, y=y + oy_, s=s, f=f, size=size, color=color.hexval()[2:], rot=rot_)); return
        c.setFont(f, size); c.setFillColor(color); c.drawString(x, y, s)
    def textC(cx, y, s, f='SCS', size=10, color=INK):
        text(cx - sw(s, f, size) / 2, y, s, f, size, color)
    def para(x, ytop, s, f='SCS', size=9.5, color=INK, maxw=240, leading=12.5):
        if CAP is not None:
            CAP.append(dict(t='para', x=x, y=ytop, runs=[(s, f, False)], size=size, color=color.hexval()[2:],
                            maxw=maxw, leading=leading, rot=0))
            return ytop - len(wrap(s, f, size, maxw)) * leading
        yy = ytop
        for ln in wrap(s, f, size, maxw):
            text(x, yy, ln, f, size, color); yy -= leading
        return yy
    def tape(cx, cy, w=34, h=10, ang=-4, col=None):
        c.saveState(); c.translate(cx, cy); c.rotate(ang)
        c.setFillColor(HexColor(col or T['tape'])); c.setFillAlpha(0.78)
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
    def flower1(cx, cy, s=0.8, filled=True, petal='#F0563F', core='#FFC93C', ring='#E8930C'):
        for a in range(6):
            deg = 90 + a * 60
            ang = math.radians(deg)
            px, py = cx + 3.0 * s * math.cos(ang), cy + 3.0 * s * math.sin(ang)
            c.saveState(); c.translate(px, py); c.rotate(deg)
            if filled:
                c.setFillColor(HexColor(petal)); c.ellipse(-2.8 * s, -1.75 * s, 2.8 * s, 1.75 * s, stroke=0, fill=1)
            else:
                c.setStrokeColor(FAINT); c.setLineWidth(0.8); c.setDash(2.2, 1.8)
                c.ellipse(-2.8 * s, -1.75 * s, 2.8 * s, 1.75 * s, stroke=1, fill=0); c.setDash()
            c.restoreState()
        if filled:
            c.setFillColor(HexColor(core)); c.circle(cx, cy, 1.85 * s, stroke=0, fill=1)
            c.setStrokeColor(HexColor(ring)); c.setLineWidth(0.6 * s); c.circle(cx, cy, 1.85 * s, stroke=1, fill=0)
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
    def stamp(x, ybase, wd, n, tilt=-1.5):
        """Verdict word as a little stamp: white card, coloured edge and text by flower count
        (green >= 4, amber 3, red below) — the same reading as the detailed page's stamps."""
        scol = HexColor('#2E9E4F') if n >= 4 else (HexColor('#D9930D') if n == 3 else HexColor('#C73E1D'))
        # same hand as 老师说 (ZCOOL KuaiLe), drawn lighter: the glyphs are filled in colour and
        # traced with a 0.4pt white outline (text render mode 2), which pares every stroke thinner
        tw2 = sw(wd, DISP, 10) + 13
        if CAP is not None:
            CAP.append(dict(t='stamp', x=x, y=ybase + 3.8 - 7.6, w=tw2, h=15.2, s=wd, color=scol.hexval()[2:], rot=tilt))
            return tw2
        c.saveState(); c.translate(x + tw2 / 2, ybase + 3.8); c.rotate(tilt)
        c.setFillColor(CARD); c.setStrokeColor(scol); c.setLineWidth(0.7)
        c.roundRect(-tw2 / 2, -7.6, tw2, 15.2, 7.6, stroke=1, fill=1)
        t_ = c.beginText(-tw2 / 2 + 6.5, -3.9); t_.setFont(DISP, 10); t_.setFillColor(scol)
        t_.setTextRenderMode(2); c.setStrokeColor(CARD); c.setLineWidth(0.4)
        t_.textOut(wd); c.drawText(t_)
        c.restoreState()                 # the render mode lives in the graphics state: restore it here
        return tw2

    def head(y, t):
        text(M, y, t, DISP, 15.5, INK)
        return y

    def draw_note(top):
        """The teacher's note as a sticky note in the column beside the radar:
        a strip of tape, a pale card, one big opening quote, and a signature."""
        lines = note_lines(d)
        sign = (d['teacher'].get('sign') or '').strip()
        h = note_height(d)
        cx, cy = NOTE_X + NOTE_W / 2, top - h / 2
        c.saveState(); c.translate(cx, cy); c.rotate(-1.3)
        x0, ty0 = -NOTE_W / 2, h / 2
        c.setFillColor(HexColor('#000000')); c.setFillAlpha(0.08)
        c.roundRect(x0 + 3, -h / 2 - 4, NOTE_W, h, 6, stroke=0, fill=1); c.setFillAlpha(1)
        c.setFillColor(HexColor(T['field'])); c.roundRect(x0, -h / 2, NOTE_W, h, 6, stroke=0, fill=1)
        c.setStrokeColor(HexColor(T['chip_line'])); c.setLineWidth(0.9)
        c.roundRect(x0, -h / 2, NOTE_W, h, 6, stroke=1, fill=0)
        ctx['off'] = (cx, cy, -1.3)
        text(x0 + 16, ty0 - 17, '老师说', DISP, 12, HexColor(T['quote']))
        c.setFont(DISP, 23); c.setFillColor(HexColor(T['quote'])); c.drawString(x0 + 14, ty0 - 41, '“')   # part of the card
        yy = ty0 - 39
        if CAP is not None:
            CAP.append(dict(t='para', x=cx + x0 + 30, y=cy + yy, runs=[(str(d['teacher']['comment']), 'SCS', False)], size=9.5,
                            color='141414', maxw=NOTE_W - 48, leading=NOTE_LEAD, rot=-1.3))
        else:
            for ln in lines:
                text(x0 + 30, yy, ln, 'SCS', 9.5, INK); yy -= NOTE_LEAD
        if sign:
            text(x0 + NOTE_W - 16 - sw(sign, 'SCS', 8.5), -h / 2 + 10, sign, 'SCS', 8.5, GREY)
        ctx['off'] = (0, 0, 0)
        c.restoreState()
        tape(cx, top - 2, 46, 12, -2)

    # ===== one cream field over the whole top; its bottom edge is a soft wave,
    # with two clouds sitting on the seam — the divider is drawn, not ruled =====
    _by = L['field_bottom']
    _fp = c.beginPath(); _fp.moveTo(E, _by + 4)
    for _x0, _y0, _x1, _y1 in [(E, 3, 104, -5), (104, -5, 196, 5), (196, 5, 288, -5), (288, -5, 380, 5), (380, 5, 472, -5), (472, -5, W - E, 2)]:
        _fp.curveTo(_x0 + (_x1 - _x0) * 0.5, _by + _y0, _x1 - (_x1 - _x0) * 0.5, _by + _y1, _x1, _by + _y1)
    _fp.lineTo(W - E, H - E); _fp.lineTo(E, H - E); _fp.close()
    c.setFillColor(HexColor(T['field'])); c.drawPath(_fp, stroke=0, fill=1)
    cloud(196, _by + 1, 0.85); cloud(472, _by - 2, 0.7)
    # the corner sun on top of the field
    # a real sun, built the way the reference builds it: one flat disc
    # with twelve pill-shaped rays floating around it, centre off the corner
    # The disc is large enough that a clear arc shows around the photo print; a ray is drawn only
    # where it reads as part of the sun — never across text, never cut by the frame, never peeking
    # out from behind the photo as a stray bar.
    _sx, _sy = SUN_C
    c.setFillColor(HexColor(T['sun']))
    _keep_out = [(OVER_X - 8, L['oy0'] - 400, W, L['oy0'] + 16),                 # overview column
                 (M - 4, H - 80, M + 12 + max(sw('英语口语测评报告', DISP, 25),                  # title + meta line
                                              sw(meta_line(d), 'SCS', 10.5)), H),
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
    # ===== the bottom scene: her voice, grown into a hill =====
    # The front hill's ridge IS this child's recording — the loudness envelope from audio_data.json,
    # smoothed into rolling hills, so every report has its own skyline. On the loudest crests small
    # plants grow, a little bigger from left to right — seedling, leaves, bud, bloom — the same
    # direction the radar and the readings read: what she said is already growing. A speech
    # bubble with a sound wave in it sits where her voice begins. The plants bloom in the theme's
    # sun colour, never red: red stays reserved for earned flowers.
    X0, X1, BASE, AMP, NPT = E, W - E, 58, 25, 92
    _env = None
    _ad = os.path.join(CASE, 'audio_data.json')
    if os.path.isfile(_ad):
        _pk = [float(v) for v in json.load(open(_ad)).get('peaks', [])]
        if len(_pk) >= 20:
            _bins = [max(_pk[int(i * len(_pk) / NPT):max(int(i * len(_pk) / NPT) + 1, int((i + 1) * len(_pk) / NPT))]) for i in range(NPT)]
            _ker = [math.exp(-(k * k) / (2 * 0.85 ** 2)) for k in range(-5, 6)]
            _sm = []
            for i in range(NPT):
                _acc = _wt = 0.0
                for k, w_ in zip(range(-5, 6), _ker):
                    if 0 <= i + k < NPT: _acc += _bins[i + k] * w_; _wt += w_
                _sm.append(_acc / _wt)
            _top = sorted(_sm)[int(0.92 * (NPT - 1))] or 1.0
            _env = [min(1.0, v / _top) for v in _sm]
    _real = _env is not None
    if _env is None:                       # no recording data: a calm default skyline
        _env = [0.45 + 0.3 * math.sin(i / NPT * math.pi * 3.2 + 0.6) ** 2 for i in range(NPT)]
    _env = [v * min(1.0, (i + 1) / 6, (NPT - i) / 6) for i, v in enumerate(_env)]     # land softly at both edges
    _px = [X0 + (X1 - X0) * i / (NPT - 1) for i in range(NPT)]
    _py = [BASE + AMP * v ** 0.8 for v in _env]

    def _smooth_path(xs, ys, floor):
        p_ = c.beginPath(); p_.moveTo(xs[0], floor); p_.lineTo(xs[0], ys[0])
        for i in range(len(xs) - 1):                       # Catmull-Rom through every point
            x0_, y0_ = (xs[i - 1], ys[i - 1]) if i else (xs[i], ys[i])
            x3_, y3_ = (xs[i + 2], ys[i + 2]) if i + 2 < len(xs) else (xs[i + 1], ys[i + 1])
            p_.curveTo(xs[i] + (xs[i + 1] - x0_) / 6, ys[i] + (ys[i + 1] - y0_) / 6,
                       xs[i + 1] - (x3_ - xs[i]) / 6, ys[i + 1] - (y3_ - ys[i]) / 6, xs[i + 1], ys[i + 1])
        p_.lineTo(xs[-1], floor); p_.close(); return p_

    # the voice hill is drawn the way a recording is drawn: a row of rounded waveform bars, one per
    # slice of the recording, standing on a gently rolling ground so it still reads as a hill
    _soft = [sum(_env[max(0, i - 9):i + 10]) / len(_env[max(0, i - 9):i + 10]) for i in range(NPT)]
    _gy = [max(FOOT_TOP + 1, BASE - 10 + 6 * math.sin(i / NPT * math.pi * 2.3 + 0.5) + 10 * v) for i, v in enumerate(_soft)]
    _py = [g + 3 + AMP * v ** 1.25 for g, v in zip(_gy, _env)]          # each bar rises from the ground by her loudness
    c.setFillColor(HexColor(T['hill2'])); c.drawPath(_smooth_path(_px, _gy, E), stroke=0, fill=1)
    _bw = (X1 - X0) / NPT * 0.68
    if not _real:                          # no recording: a plain hill — never a made-up waveform
        c.drawPath(_smooth_path(_px, _py, E), stroke=0, fill=1)
    for i in (range(1, NPT - 1) if _real else ()):
        top = max(_py[i], _gy[i] + _bw)
        c.roundRect(_px[i] - _bw / 2, _gy[i] - 4, _bw, top - _gy[i] + 4, _bw / 2, stroke=0, fill=1)

    # where the plants stand: local crests, the highest first, kept apart; then left to right
    _lead = 0
    while _lead < NPT - 1 and _env[_lead] < 0.35: _lead += 1          # where her voice begins
    _cand = [i for i in range(4, NPT - 4) if _env[i] >= max(_env[max(0, i - 4):i + 5]) and _env[i] > 0.35]
    _cand.sort(key=lambda i: -_env[i])
    _spots = []
    for i in _cand:
        if _px[i] < _px[_lead] + 70 or _px[i] > X1 - 30: continue
        if abs(_px[i] - W / 2) < 70 and _py[i] < 60: continue             # keep clear of the footer label
        if all(abs(_px[i] - _px[j]) >= 62 for j in _spots): _spots.append(i)
        if len(_spots) == 5: break
    _spots.sort()
    if not _real:                          # no recording data: no plants either — nothing here is invented
        _spots = []
    LEAF = HexColor('#7CB342')        # plants stay plant-green in every theme; only the hills take the theme

    def _leaf(x, y, l, ang):
        c.saveState(); c.translate(x, y); c.rotate(ang)
        lp = c.beginPath(); lp.moveTo(0, 0); lp.curveTo(l * 0.35, l * 0.42, l * 0.75, l * 0.36, l, 0)
        lp.curveTo(l * 0.75, -l * 0.2, l * 0.35, -l * 0.22, 0, 0); lp.close()
        c.setFillColor(LEAF); c.drawPath(lp, stroke=0, fill=1); c.restoreState()

    def _plant(x, y, stage):
        """0 seedling · 1 two leaves · 2 taller, three leaves · 3 bud · 4 bloom — one drawing family."""
        h = (7, 11, 15, 18, 19)[stage]
        c.setStrokeColor(LEAF); c.setLineWidth(1.6); c.setLineCap(1)
        c.line(x, y - 1, x, y + h); c.setLineCap(0)
        ll = (6, 8, 9, 9, 9.5)[stage]
        if stage == 0:
            _leaf(x, y + h, ll, 25); _leaf(x, y + h, ll, 155)
        else:
            _leaf(x, y + h * 0.42, ll, 28); _leaf(x, y + h * 0.42 + 2, ll, 152)
        if stage >= 2: _leaf(x, y + h * 0.75, ll * 0.8, 32)
        if stage == 3:                                    # a closed bud: teardrop on two small sepals
            bp = c.beginPath(); bp.moveTo(x, y + h + 13)
            bp.curveTo(x + 6.5, y + h + 7, x + 5, y + h, x, y + h); bp.curveTo(x - 5, y + h, x - 6.5, y + h + 7, x, y + h + 13)
            bp.close(); c.setFillColor(HexColor(T['sun'])); c.drawPath(bp, stroke=0, fill=1)
            _leaf(x, y + h + 0.5, 5, 40); _leaf(x, y + h + 0.5, 5, 140)
        if stage == 4:
            flower1(x, y + h + 8, 1.2, True, petal=T['sun'], core='#FFFFFF', ring=T['frame'])

    _stages = {1: [4], 2: [2, 4], 3: [1, 3, 4], 4: [0, 2, 3, 4], 5: [0, 1, 2, 3, 4]}.get(len(_spots), [])
    for i, st_ in zip(_spots, _stages):
        _plant(_px[i], _py[i] - 2.5, st_)

    # a few grass tufts in the valleys
    _val = []                              # the gaps between bars already read as quiet; no grass needed
    c.setStrokeColor(LEAF); c.setLineWidth(1.3); c.setLineCap(1)
    for i in _val[::2][:5]:
        gx_, gy_ = _px[i], _py[i] - 3
        c.line(gx_ - 3, gy_, gx_ - 6, gy_ + 6); c.line(gx_, gy_, gx_, gy_ + 7.5); c.line(gx_ + 3, gy_, gx_ + 6, gy_ + 6)
    c.setLineCap(0)

    # the speech bubble where her voice begins, a little sound wave inside
    _sx0 = max(X0 + 10, min(_px[_lead] - 6, X0 + 90)); _sy0 = _py[_lead] + 14
    _bw, _bh = 42, 24
    c.setFillColor(CARD); c.setStrokeColor(HexColor(T['frame'])); c.setLineWidth(1.4); c.setLineJoin(1)
    _tp = c.beginPath(); _tp.moveTo(_sx0 + 9, _sy0 + 4); _tp.lineTo(_sx0 + 6, _sy0 - 8); _tp.lineTo(_sx0 + 20, _sy0 + 2); _tp.close()
    c.drawPath(_tp, stroke=1, fill=1)
    c.roundRect(_sx0, _sy0, _bw, _bh, 9, stroke=1, fill=1)
    c.setLineJoin(0)
    c.setStrokeColor(CARD); c.setLineWidth(2.2)
    c.line(_sx0 + 8, _sy0 + 2.6, _sx0 + 19, _sy0 + 2.6)                # erase the tail's seam inside the bubble
    c.setFillColor(HexColor(T['quote']))
    for k_, hh in enumerate((5, 10, 14, 8, 11, 5)):
        c.roundRect(_sx0 + 7.5 + k_ * 5, _sy0 + _bh / 2 - hh / 2, 2.6, hh, 1.3, stroke=0, fill=1)

    # the yellow board frame — everything is pinned inside it. Its outer edge sits 14pt (5 mm)
    # in from the paper edge, inside what an office or home printer can actually print.
    c.setStrokeColor(HexColor(T['frame'])); c.setLineWidth(8); c.rect(E - 4, E - 4, W - 2 * E + 8, H - 2 * E + 8, stroke=1, fill=0)
    # ---------- 1. header: identity + overall ----------
    text(M, H - 46, '英语口语测评报告', DISP, 25, INK)
    text(M, H - 68, meta_line(d), 'SCS', 10.5, INK)
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
    R = 66; cx0, cy0 = M + 118, L['cy0']
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
    c.setFillColor(HexColor(T['radar_fill'])); c.setFillAlpha(0.30); c.drawPath(pp, stroke=0, fill=1); c.setFillAlpha(1)
    c.setStrokeColor(HexColor(T['radar_line'])); c.setLineWidth(2.2); c.setLineJoin(1); c.drawPath(pp, stroke=1, fill=0); c.setLineJoin(0)
    for k, di in enumerate(order):
        x, y = _pt(k, R * d['dims'][di][2] / 5)
        c.setFillColor(HexColor(T['radar_line'])); c.circle(x, y, 3.6, stroke=0, fill=1)
        c.setStrokeColor(CARD); c.setLineWidth(1.6); c.circle(x, y, 3.6, stroke=1, fill=0)
    for k, di in enumerate(order):        # names only: the verdict word is said once, in the readings
        nm = d['dims'][di][0]
        lx, ly = _pt(k, R + 10)
        if k == 0: textC(lx, ly + 4, nm, 'SCB', 10.5, INK)
        elif k == 3: textC(lx, ly - 12, nm, 'SCB', 10.5, INK)
        elif k in (1, 2): text(lx, ly - 3.5, nm, 'SCB', 10.5, INK)
        else: text(lx - sw(nm, 'SCB', 10.5), ly - 3.5, nm, 'SCB', 10.5, INK)
    # right of the chart: the teacher's note when a real one exists, 总览 only when it doesn't
    ox = OVER_X
    oy0 = L['oy0']
    if d.get('teacher'):
        draw_note(oy0)
    else:
        text(ox, oy0, '总览', 'SCB', 11, INK)
        yy = oy0 - 21
        for ln in d.get('overview') or []:
            lead = lead_of(ln)
            if CAP is not None:
                runs = ([(lead, 'SCB', False), (ln[len(lead):], 'SCS', False)] if lead and ln.startswith(lead) else [(ln, 'SCS', False)])
                CAP.append(dict(t='para', x=ox, y=yy, runs=runs, size=10, color='141414', maxw=OVER_W, leading=14, rot=0))
                yy -= len(wrap(ln, 'SCS', 10, OVER_W)) * 14 + 4
                continue
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
    tch = d.get('teacher')
    # spacing steps down only as far as the page needs: (gap name->reading, leading, gap between rows)
    _rows = [max(len(wrap(x[3], 'SCS', 9.5, DESC_W)) for x in (d['dims'][r], d['dims'][r + 3])) for r in range(3)]
    _below = 34 + 62 + 24 * len(d['games'])          # 英语学习小建议 + the games, measured as drawn below
    for RT, RL, RG in ((17, 14, 16), (16, 13.5, 14), (15, 13, 12), (14, 12.5, 10)):
        if gy - sum(RT + n_ * RL + RG for n_ in _rows) - _below >= FLOOR: break
    for row in range(3):                 # each row as tall as its longer reading
        pair = (d['dims'][row], d['dims'][row + 3])
        rows_used = max(len(wrap(x[3], 'SCS', 9.5, DESC_W)) for x in pair)
        # one line per dimension: name + stamp on the left, the five flowers (smaller) closing on the
        # column's right edge, so every row shares one left edge and one right edge; the reading sits
        # 17pt below in a softer ink with 14pt leading — air inside a cell, less between cells; on a full
        # page the spacing steps down (16/13.5/14 … 14/12.5/10) before anything overflows
        for col, (nm, wd, n, desc) in enumerate(pair):
            gx = COLX[col]
            text(gx, gy, nm, 'SCB', 11, INK)
            stamp(gx + sw(nm, 'SCB', 11) + 8, gy, wd, n, -1.5 if (row + col) % 2 == 0 else 1.5)
            flowers(gx + DESC_W - 5 * 19 * 0.64, gy + 3.4, n, 0.64)
            para(gx, gy - RT, desc, 'SCS', 9.5, HexColor('#3A3F46'), maxw=DESC_W, leading=RL)
        gy -= RT + rows_used * RL + RG

    # ---------- 4. what to do next ----------
    ny = gy - 34
    head(ny, '英语学习小建议')
    _gw = sw(d['goal'], 'SCS', 10.5)
    c.setFillColor(HexColor(T['chip_shadow'])); c.rect(M + 59, ny - 36, _gw + 18, 21, stroke=0, fill=1)
    c.setFillColor(HexColor(T['field'])); c.rect(M + 56, ny - 33, _gw + 18, 21, stroke=0, fill=1)
    c.setStrokeColor(HexColor(T['chip_line'])); c.setLineWidth(0.8); c.rect(M + 56, ny - 33, _gw + 18, 21, stroke=1, fill=0)
    tape(M + 62, ny - 12, 24, 8, -7)
    # baseline sits 0.35em BELOW the chip's centre: PDF text hangs on its baseline,
    # and CJK ink lives almost entirely above it — centre the ink, not the baseline
    text(M, ny - 26, '小目标', 'SCB', 11, RED)
    _marks = [w_.lower() for w_ in d.get('mark', [])]
    if CAP is not None:
        runs, pos = [], 0
        for m_ in re.finditer(r"[A-Za-z']+", d['goal']):
            if m_.group().lower() in _marks:
                runs += [(d['goal'][pos:m_.start()], 'SCS', False), (m_.group(), 'SCS', True)]; pos = m_.end()
        runs.append((d['goal'][pos:], 'SCS', False))
        CAP.append(dict(t='para', x=M + 65, y=ny - 26, runs=[r for r in runs if r[0]], size=10.5, color='141414',
                        maxw=_gw + 30, leading=14, rot=0, nowrap=True))
    else:
        text(M + 65, ny - 26, d['goal'], 'SCS', 10.5, INK)
    for m_ in (re.finditer(r"[A-Za-z']+", d['goal']) if CAP is None else ()):      # the words to practise, dashed red
        if m_.group().lower() in _marks:
            ux = M + 65 + sw(d['goal'][:m_.start()], 'SCS', 10.5)
            c.setStrokeColor(RED); c.setLineWidth(1.2); c.setDash(2.6, 1.8)
            c.line(ux, ny - 28.6, ux + sw(m_.group(), 'SCS', 10.5), ny - 28.6); c.setDash()
    gy = ny - 62
    text(M, gy, '在家练', 'SCB', 11, INK)
    for j, (gn, gd) in enumerate(d['games']):
        bx = M + 64                      # three games, no order between them: a box to tick, not a rank
        c.setStrokeColor(INK); c.setLineWidth(1.1); c.roundRect(bx, gy - 1.5, 11, 11, 2.5, stroke=1, fill=0)
        text(bx + 20, gy, gn, 'SCB', 10.5, INK)
        para(M + 168, gy, gd, 'SCS', 10, INK, maxw=CW - 168, leading=13)
        gy -= 24

    # the page keeps only what a parent reads: shape, evidence, teacher's voice, actions.
    # The full transcript stays in case.json as the record — it is not printed on this page.
    if gy < FLOOR:
        raise ValueError(f'内容超出版面 {FLOOR - gy:.0f}pt：请精简解读、游戏或老师评语')

    # ===== footer: the group's logo, the kindergarten's logo, and the standards in fine print =====
    # It sits on the hill's own ground (the band below FOOT_TOP), so the scene stays one picture.
    # Logos are transparent PNGs drawn straight onto the ground — no chip behind them (never
    # recoloured or stretched: contain-fit). The
    # kindergarten logo comes from case.json "school_logo" (or assets/brand/kindergarten-logo.png);
    # until there is one, a dashed placeholder keeps its place.
    def logo_chip(x, w, path, label):
        y0, h = E + 4, FOOT_TOP - E - 10
        if path and os.path.isfile(path):
            from reportlab.lib.utils import ImageReader
            ir = ImageReader(path); iw, ih = ir.getSize()
            k = min(w / iw, h / ih)
            c.drawImage(ir, x + (w - iw * k) / 2, y0 + (h - ih * k) / 2, iw * k, ih * k, mask='auto')
        else:
            c.setStrokeColor(FAINT); c.setLineWidth(0.7); c.setDash(2.2, 1.8)
            c.roundRect(x + 4, y0 + 4, w - 8, h - 8, 3.5, stroke=1, fill=0); c.setDash()
            c.setFillColor(GREY); c.setFont('SCS', 6); c.drawCentredString(x + w / 2, y0 + h / 2 - 2, label)
    _lw, _kw = 76, 50                  # the group's logo is wide, a kindergarten's is usually a crest
    logo_chip(E + 8, _lw, os.path.join(BRAND, 'cieg-logo.png'), '集团标志')
    _sl = d.get('school_logo')
    _sl = os.path.join(CASE, _sl) if _sl else os.path.join(BRAND, 'kindergarten-logo.png')
    logo_chip(W - E - 8 - _kw, _kw, _sl, '幼儿园标志')
    # the fine print, in the register of an exam's published marking notes: paragraph one is the
    # rule (what each dimension examines and which IELTS / Starters description it is set against,
    # what the flower counts mean), paragraph two the source documents. Plain weight throughout,
    # no space between Chinese and English, full-width Chinese punctuation. Anchors as references/rubric.md.
    _fx0, _fx1 = E + 8 + _lw + 12, W - E - 8 - _kw - 12
    _fs, _fl = 4.6, 5.85
    _fp = ['评分说明：本报告设六个评定维度，各维度依据本次录音取证，并对照IELTS口语评分描述与剑桥Pre A1 Starters相应要求定档。'
           '词汇考查用词范围与准确性（朗读任务考查核心词认读），参照Starters主题词表及IELTS Lexical Resource；'
           '句式与语法考查句型范围与错误情况（朗读任务考查漏读、添读与替换），参照Starters语法结构清单及IELTS Grammatical Range and Accuracy；'
           '完整与创意考查表达结构的完整性与自主组句，参照Starters口语能力描述（can-do statements）及IELTS Fluency and Coherence；'
           '发音准确度考查词语能否被准确辨识（朗读任务对照原文），参照IELTS Pronunciation；'
           '流利度考查语速、长停顿、重复与填充词，参照IELTS Fluency and Coherence；'
           '语调与重音考查句末升降与语句起伏，参照IELTS Pronunciation。'
           '各维度以五朵小红花为满档：五朵表示该维度无可指认的失误且有突出表现，四朵表示整体达到要求、存在一处明确的待改进点，三朵及以下均附具体证据。',
           '依据文本：IELTS Speaking Band Descriptors（public version），IDP IELTS、British Council与Cambridge University Press & Assessment；'
           'Cambridge English Pre A1 Starters考试大纲及词汇表、语法结构清单，Cambridge University Press & Assessment；'
           'Common European Framework of Reference for Languages: Companion Volume，Council of Europe，2020。']
    _plain = [t.replace('**', '') for t in _fp]
    _flines = [ln for t in _plain for ln in wrap(t, 'SCS', _fs, _fx1 - _fx0)]
    _band_mid = E + 4 + (FOOT_TOP - E - 10) / 2
    _fy = _band_mid + (len(_flines) - 1) * _fl / 2 - _fs * 0.35
    _fink = HexColor('#3F4A3C')
    if len(_flines) * _fl > FOOT_TOP - E - 6:
        raise ValueError('页脚参考标准超过页脚高度，请精简条目')
    if CAP is not None:
        for t, pl in zip(_fp, _plain):
            runs = [(seg, 'SCB' if k % 2 else 'SCS', False) for k, seg in enumerate(t.split('**')) if seg]
            CAP.append(dict(t='para', x=_fx0, y=_fy, runs=runs, size=_fs, color='3F4A3C', maxw=_fx1 - _fx0, leading=_fl, rot=0))
            _fy -= len(wrap(pl, 'SCS', _fs, _fx1 - _fx0)) * _fl
    else:
        for t, pl in zip(_fp, _plain):
            # which characters are bold, by position in the plain text
            bold, pos = [], 0
            for k, seg in enumerate(t.split('**')):
                bold += [bool(k % 2)] * len(seg)
            off = 0
            for ln in wrap(pl, 'SCS', _fs, _fx1 - _fx0):
                start = pl.find(ln, off); start = off if start < 0 else start
                xx, i = _fx0, 0
                while i < len(ln):                        # draw runs of equal weight
                    j = i
                    b_ = bold[start + i] if start + i < len(bold) else False
                    while j < len(ln) and (bold[start + j] if start + j < len(bold) else False) == b_: j += 1
                    seg = ln[i:j]; f_ = 'SCB' if b_ else 'SCS'
                    c.setFont(f_, _fs); c.setFillColor(_fink); c.drawString(xx, _fy, seg); xx += sw(seg, f_, _fs)
                    i = j
                off = start + len(ln); _fy -= _fl
    c.showPage(); c.save()
    if CAP is None: print('saved', d['out'])

case_ = load_case(CASE_FILE)
render(case_)
# the editable companion: same page, illustrations as one picture, every piece of text a real text box
if '--no-pptx' not in sys.argv:
    try:
        import export_pptx
    except ImportError as e:
        print(f'（未出 PPT 可编辑版：缺 {e.name}，pip install python-pptx pymupdf）')
    else:
        export_pptx.build(case_, render, os.path.join(CASE, os.path.splitext(case_['out'])[0] + '.pptx'), wrap)
