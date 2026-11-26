#!/usr/bin/env python3
"""Pronunciation coaching: diagnose -> look up -> verify. Used by build_simple.py's validate().

Every "how to make this sound" sentence in a report comes from ONE table,
references/pronunciation-coach.md, copied verbatim; nothing is improvised. case.json names the
single focus sound of the report:

    "focus_sound": {"target": "θ", "heard_as": "f", "words": ["three"]}

and this module checks, against the CMU Pronouncing Dictionary bundled in assets/dict (BSD-style
licence beside it), that
  1. target is a row of the table;
  2. every example word really carries that sound (two has no /θ/ — stopped here);
  3. a list of English words given as practice for the focus (「mouth、teeth、three」) holds only
     words that carry the sound;
  4. any sentence in 老师说 / 小目标 / 在家练 that talks about how to move the tongue, lips, teeth or
     breath contains the table's 纠音说法 for that sound, word for word;
  5. one focus: the practice words (mark) come from the focus words, and 小目标, 老师说 and at least
     one game all point at it.
Run directly to self-check the table:  python3 scripts/coach.py"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = os.path.normpath(os.path.join(HERE, '..', 'references', 'pronunciation-coach.md'))
DICT = os.path.normpath(os.path.join(HERE, '..', 'assets', 'dict', 'cmudict.dict'))

VOWELS = {'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}
MAGIC = lambda v: re.compile(rf'{v}[b-df-hj-np-tv-z]e(s|d)?$|{v}[b-df-hj-np-tv-z]e[^aeiou]')
def _has(*ph): return lambda w, p: any(x in p for x in ph)
def _cons(x): return x.rstrip('012') not in VOWELS

# how each row is checked in the dictionary (phones without stress digits, except where it matters)
PATTERNS = {
    'θ': _has('TH'), 'ð': _has('DH'), 'v': _has('V'), 'w': _has('W'), 'r': _has('R'), 'l': _has('L'),
    '词尾l': lambda w, p: p[-1] == 'L',
    'n-ŋ': _has('N', 'NG'), 'n-l': _has('N', 'L'), 'ʃ': _has('SH'), 'z': _has('Z'),
    'tʃ-dʒ': _has('CH', 'JH'), 'h': _has('HH'),
    '词尾辅音': lambda w, p: _cons(p[-1]), '词尾加音': lambda w, p: _cons(p[-1]),
    '辅音连缀': lambda w, p: any(_cons(a) and _cons(b) for a, b in zip(p, p[1:])),
    '词尾s': lambda w, p: p[-1] in ('S', 'Z'),
    'iː-ɪ': _has('IY', 'IH'), 'æ': _has('AE'), 'ʌ': None,                       # needs stress digits: handled in carries()
    'ɜː': _has('ER'), 'ʊ-uː': _has('UH', 'UW'),
    'a-e': lambda w, p: 'EY' in p and bool(MAGIC('a').search(w)),
    'i-e': lambda w, p: 'AY' in p and bool(MAGIC('i').search(w)),
    'o-e': lambda w, p: 'OW' in p and bool(MAGIC('o').search(w)),
    'u-e': lambda w, p: 'UW' in p and bool(MAGIC('u').search(w)),
    '重音': lambda w, p: sum(1 for x in p if x in VOWELS) >= 2,
}
# words that describe how to move the mouth: a sentence using any of them must carry the table's line
ARTIC = ['舌尖', '舌头', '舌身', '舌根', '上齿', '下齿', '门牙', '牙齿', '齿间', '牙床', '嘴唇', '双唇', '下唇', '上唇',
         '撅', '卷舌', '送气', '吹气', '声带', '喉咙', '软腭', '上颚', '鼻子']

# words that say a sentence is about pronouncing something (then its word lists are checked)
SOUND_TALK = ['音', '读准', '念准', '发准', '读清', '念清', '词尾', '舌', '嘴型']

_dict = None
def phones(word):
    """All pronunciations of a word in the CMU dictionary (stress digits stripped; raw kept)."""
    global _dict
    if _dict is None:
        _dict = {}
        with open(DICT, encoding='utf-8') as f:
            for line in f:
                parts = line.split('#')[0].split()
                if not parts: continue
                key = re.sub(r'\(\d+\)$', '', parts[0])
                _dict.setdefault(key, []).append(parts[1:])
    out = []
    for raw in _dict.get(word.lower(), []):
        p = [x.rstrip('012') for x in raw]
        out.append((p, raw))
    return out

def carries(target, word):
    """Does any dictionary pronunciation of `word` carry the table row `target`?"""
    for p, raw in phones(word):
        ok = (any(x in ('AH1', 'AH2') for x in raw) if target == 'ʌ'      # stressed /ʌ/, not schwa
              else PATTERNS[target](word.lower(), p))
        if ok: return True
    return False

def table():
    """Rows of references/pronunciation-coach.md: key -> dict(name, heard, tip, pairs, game)."""
    rows = {}
    for line in open(TABLE, encoding='utf-8'):
        m = re.match(r'\|\s*`([^`]+)`\s*\|(.*)\|\s*$', line)
        if not m: continue
        cells = [c.strip() for c in m.group(2).split('|')]
        if len(cells) < 5: continue
        rows[m.group(1)] = dict(name=cells[0], heard=cells[1], tip=cells[2], pairs=cells[3], game=cells[4])
    return rows

def _sentences(s):
    return [x for x in re.split(r'(?<=[。；！？])', s) if x.strip()]

def _english_lists(s):
    """Runs of English words joined by 、 or ，— the way practice words are listed in Chinese text."""
    return [re.findall(r"[A-Za-z][A-Za-z'\-]*", m.group(0))
            for m in re.finditer(r"[A-Za-z][A-Za-z'\-]*(?:\s*[、，,/]\s*[A-Za-z][A-Za-z'\-]*)+", s)]

def check(d):
    """Raise ValueError with an actionable message; return None when the case passes."""
    rows = table()
    tch = (d.get('teacher') or {}).get('comment', '')
    games = [f'{g[0]}：{g[1]}' for g in d.get('games', [])]
    places = [('小目标', d.get('goal', '')), ('老师说', tch)] + [(f'在家练「{g[0]}」', f'{g[0]}：{g[1]}') for g in d.get('games', [])]
    fs = d.get('focus_sound')
    if not fs:
        for where, text in places:
            for sen in _sentences(text):
                hit = next((k for k in ARTIC if k in sen), None)
                if hit:
                    raise ValueError(f'{where}写了发音部位（「{hit}」）却没有 focus_sound：先在 case.json 写 focus_sound，'
                                     f'纠音说法只能照抄 references/pronunciation-coach.md')
        return
    tgt = fs.get('target')
    if tgt not in rows:
        raise ValueError(f'focus_sound.target「{tgt}」不在纠音表里；可选：' + '、'.join(rows))
    words = [w.lower() for w in fs.get('words') or []]
    if not words:
        raise ValueError('focus_sound.words 为空：写上录音里出问题的那一两个词')
    for w in words:
        if not phones(w):
            raise ValueError(f'CMU 词典里查不到 {w}：换一个录音里出现、词典能查到的例词')
        if not carries(tgt, w):
            ph = ' '.join(phones(w)[0][1])
            raise ValueError(f'{w} 不含纠音表「{rows[tgt]["name"]}」这个音（词典：{ph}），不能作为它的例词')
    tip = rows[tgt]['tip']
    for where, text in places:
        for sen in _sentences(text):
            hit = next((k for k in ARTIC if k in sen), None)
            if hit and tip not in sen:
                raise ValueError(f'{where}讲了发音部位（「{hit}」），但不是纠音表的说法：这一句请照抄「{tip}」，或删掉发音部位只留练法')
        for sen in _sentences(text):
            if not any(k in sen for k in ARTIC + SOUND_TALK):     # a list only counts when the sentence is about the sound
                continue
            for run in _english_lists(sen):
                if not any(x.lower() in words for x in run):
                    continue
                bad = [x for x in run if len(x) > 1 and phones(x) and not carries(tgt, x)]
                if bad:
                    raise ValueError(f'{where}把 {"、".join(bad)} 和 {"、".join(x for x in run if x.lower() in words)} 一起当「{rows[tgt]["name"]}」练，'
                                     f'但 {"、".join(bad)} 不含这个音（词典核对）：删掉或换成含这个音的词')
    marks = [m.lower() for m in d.get('mark', [])]
    stray = [m for m in marks if m not in words]
    if stray:
        raise ValueError(f'练习词 {"、".join(stray)} 不在 focus_sound.words 里：一份报告只练一个重点音，练习词从重点音的例词里取')
    has = lambda s: any(re.search(rf'(?<![A-Za-z]){re.escape(w)}(?![A-Za-z])', s, re.I) for w in words)
    if not has(d.get('goal', '')):
        raise ValueError(f'小目标没有点到重点音的例词（{"、".join(words)}）：小目标、老师说、在家练要说同一件事')
    if tch and not has(tch):
        raise ValueError(f'老师说没有点到重点音的例词（{"、".join(words)}）：老师说的下一步要和小目标一致')
    pair_words = [x.lower() for x in re.findall(r"[A-Za-z]+", rows[tgt]['pairs'])]
    if not any(has(g) or any(re.search(rf'(?<![A-Za-z]){p}(?![A-Za-z])', g, re.I) for p in pair_words) for g in games):
        raise ValueError(f'在家练三个游戏都没练到重点音：至少一个游戏用上例词或纠音表的对比词（{rows[tgt]["pairs"]}）')

if __name__ == '__main__':                     # self-check: in every contrast pair one word carries the sound
    rows = table(); bad = 0
    for k, r in rows.items():
        if k not in PATTERNS: print('缺 PATTERNS：', k); bad += 1; continue
        for pair in r['pairs'].split('，'):
            ws = [x.strip().replace('-', '').lower() for x in pair.split('/')]
            missing = [w for w in ws if not phones(w)]
            if missing: print(f'{k}: 词典里没有 {"、".join(missing)}'); bad += 1
            elif not any(carries(k, w) for w in ws): print(f'{k}: 对比词 {pair} 都不含该音'); bad += 1
    print(f'{len(rows)} 行，{"全部通过" if not bad else f"{bad} 处问题"}')
