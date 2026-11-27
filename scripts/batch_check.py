#!/usr/bin/env python3
"""Batch check: after a class has been run (many children, often by parallel agents that never see
each other's work), look across all the case.json files for the same sentences, the same game
names and the same openings turning up child after child. A language model writes the likeliest
sentence; given the same examples it writes the same one for every child. One report never shows
this — only the batch does — so the batch is checked as a whole.

    python3 scripts/batch_check.py cases/            (or any folder holding <child>/case.json)

Looks at 小目标, 在家练 (names and how-tos) and 老师说 — the parts meant to be written for this child. English words are masked
(so only the Chinese frame is compared) and the pronunciation table's own 纠音说法 lines are taken
out first: those are meant to be identical. Exit code 1 and a list of children to rewrite when
something repeats too often; fix their case.json, rebuild those reports, run this again."""
import difflib, glob, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

N = 8                      # a shared run of this many Chinese characters counts as the same sentence
FIELDS = ('小目标', '在家练', '老师说')      # the readings share the rubric's terms on purpose (已建立陈述句降调 …)

def limits(n):
    """How many children may share a phrase / a game name / an opening before it is flagged."""
    return dict(phrase=max(3, round(n * 0.15)), name=max(3, round(n * 0.10)), opening=max(3, round(n * 0.20)))

def tips():
    try:
        import coach
        return sorted({r['tip'] for r in coach.table().values()}, key=len, reverse=True)
    except Exception:
        return []

def clean(s, tip_lines, name=''):
    for t in tip_lines:
        s = s.replace(t, '◇')
    if name:
        s = s.replace(name, '◇')
    return re.sub(r"[A-Za-z0-9][A-Za-z0-9'’\-. …]*", 'X', s)

def grams(s):
    out = set()
    for i in range(len(s) - N + 1):
        g = s[i:i + N]
        if 'X' in g or '◇' in g or re.search(r'[，。；：、！？「」（）—\s]', g[0] + g[-1]):
            continue
        if sum(1 for ch in g if '一' <= ch <= '鿿') >= N - 1:
            out.add(g)
    return out

def load(folder):
    cases = []
    for p in sorted(glob.glob(os.path.join(folder, '**', 'case.json'), recursive=True)):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print(f'跳过 {p}：{e}'); continue
        cases.append((os.path.basename(os.path.dirname(p)), d))
    return cases

def main():
    folder = next((a for a in sys.argv[1:] if not a.startswith('-')), 'cases')
    cases = load(folder)
    n = len(cases)
    if n < 4:
        print(f'{folder} 里只有 {n} 份，批量查重至少要 4 份'); return 0
    lim, tl = limits(n), tips()
    phrase = {f: defaultdict(set) for f in FIELDS}
    names, openings = defaultdict(set), {f: defaultdict(set) for f in ('小目标', '老师说')}
    for who, d in cases:
        nm = str(d.get('name') or '')
        texts = {'小目标': d.get('goal', ''),
                 '在家练': '；'.join(f'{g[0]}：{g[1]}' for g in d.get('games', [])),
                 '老师说': (d.get('teacher') or {}).get('comment', '')}
        for f, s in texts.items():
            c = clean(str(s), tl, nm)
            for g in grams(c):
                phrase[f][g].add(who)
            if f in openings and c.strip():
                openings[f][c.strip('◇ ，')[:6]].add(who)
        for g in d.get('games', []):
            names[clean(g[0], tl)].add(who)

    hits, redo = [], defaultdict(list)
    def flag(kind, text, whos, cap):
        whos = sorted(whos)
        hits.append(f'{kind}「{text}」出现在 {len(whos)} 份（上限 {cap}）：' + '、'.join(whos[:12]) + ('…' if len(whos) > 12 else ''))
        for w in whos[cap:]:                      # the first few may keep it; the rest rewrite
            redo[w].append(f'{kind}「{text}」')
    for f in FIELDS:
        shown = []
        for g, whos in sorted(phrase[f].items(), key=lambda kv: -len(kv[1])):
            if len(whos) <= lim['phrase']:
                continue
            same = False                        # one long sentence makes many overlapping runs: show it once
            for s_, w_ in shown:
                m = difflib.SequenceMatcher(None, g, s_).find_longest_match(0, len(g), 0, len(s_))
                if m.size >= 4 and len(whos & w_) >= 0.6 * len(whos):
                    same = True; break
            if same:
                continue
            shown.append((g, whos)); flag(f'{f}句子', g, whos, lim['phrase'])
    for nm_, whos in names.items():
        if len(whos) > lim['name']:
            flag('在家练游戏名', nm_, whos, lim['name'])
    for f, ops in openings.items():
        for op, whos in ops.items():
            if len(whos) > lim['opening']:
                flag(f'{f}开头', op + '…', whos, lim['opening'])

    if not hits:
        print(f'{n} 份报告，没有成批重复的句子、游戏名或开头'); return 0
    print(f'{n} 份报告里有成批重复（纠音表原话不算）：\n')
    for h in hits:
        print('  - ' + h)
    print(f'\n要重写的孩子（{len(redo)} 份）——按各自的阶段、最需要补的维度、视频里看得出的兴趣重新写，'
          f'不换个说法套同一个句式：')
    for w, why in sorted(redo.items()):
        print(f'  {w}：' + '；'.join(sorted(set(why))[:4]))
    return 1

if __name__ == '__main__':
    sys.exit(main())
