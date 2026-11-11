#!/usr/bin/env python3
"""Band the three sound dimensions from measured indicators — fixed written rules, no hand-tuning.

Usage (in the case directory):  python3 score_sound.py [speech-16k.wav] [sound_scores.json]

Inputs
  speech-16k.wav   the recording
  asr/*.json       one word list per recogniser (transcribe.py writes them); at least three strong ones
  case.json        optional: "task" ("read" = 朗读 a given text, "speak" = 自由表达, the default) and,
                   for a read-aloud, "original" (the book text, without the child's own hello/thank-you)

What is measured (thresholds in references/rubric.md — keep both in step):
  发音准确度  speak: share of spoken tokens a two-thirds majority of recognisers hear alike.
              read:  share of the ORIGINAL text's tokens that a two-thirds majority hear as written —
                     recognisers repair words from context, so agreement alone can't see a mule read
                     as "meal"; the original can. Either way a content word the systems split on
                     (2 of 3) is listed and blocks 5 flowers; whisper words with p < 0.5 are listed, and a
              content word below 0.4 (not the child's name, not a spelled letter) also blocks 5 flowers.
              Agreement is computed only over stretches a majority of recognisers actually cover:
              a recogniser silent for >= 1 s where others hear speech is flagged under "coverage",
              and when the evidence base drops to two systems that is stated, not hidden.
  流利度      articulation rate (words per minute of actual speaking time — page turns and breaths
              between sentences don't count against it), long pauses (>= 1 s, counted wherever they
              fall: recogniser punctuation cannot locate a child's sentence boundaries reliably, so
              the inside/between-sentence split is still reported but no longer gates the band),
              repeats, and fillers. Recognisers silently drop "um/嗯", so fillers are also found
              acoustically: a voiced stretch of 0.2–1.5 s that no recogniser turned into a word.
  语调与重音  pitch span (5th–95th percentile, semitones) and the share of statements ending falling.
              The top band also requires at least one measured ending that rises or levels: identical
              falling contours prove one tune, not control of melody. With few endings, the 4-flower
              falling share may be missed by a single ending (calibrated 2026-11-11, see rubric).
Not calibrated against human examiners: a formative banding, never an exam score (references/claims.md)."""
import difflib, glob, json, math, os, re, sys
import numpy as np
import parselmouth

WAV = sys.argv[1] if len(sys.argv) > 1 else 'speech-16k.wav'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'sound_scores.json'
CASE = os.path.dirname(os.path.abspath(WAV))

NUM = dict(zip('0123456789', 'zero one two three four five six seven eight nine'.split()))
SAME = {'to': 'two', 'too': 'two', 'for': 'four', 'ate': 'eight', 'won': 'one', 'chose': 'choose'}
FILLERS = {'uh', 'um', 'er', 'erm', 'ah', 'eh', 'hmm', 'mm', 'umm', 'uhh'}
FUNC = {'the', 'a', 'an', 'of', 'to', 'two', 'and', 'is', 'are', 'am', 'in', 'on', 'at', 'my', 'me', 'i',
        'it', 'he', 'she', 'you', 'we', 'his', 'her', 'this', 'that', 'but', 'then', 'so'}

def tokens(words):
    """Normalise words so different spellings of one sound compare equal: digits become number
    words, spelled letters ('CE', 'HADEC4') become one token per character."""
    out = []
    for w in words:
        raw = str(w['w']).strip()
        core = re.sub(r"[^A-Za-z0-9']", '', raw)
        if not core: continue
        spelled = (core.isalpha() and core.isupper() and 1 < len(core) <= 8) or (len(core) > 1 and any(ch.isdigit() for ch in core))
        parts = list(core) if spelled else [core]
        for k, p in enumerate(parts):
            t = p.lower(); t = NUM.get(t, t); t = SAME.get(t, t)
            out.append({'t': t, 's': float(w.get('s', 0)), 'e': float(w.get('e', 0)), 'p': w.get('p'),
                        'end': raw[-1:] in '.?!' and k == len(parts) - 1, 'q': raw.endswith('?'), 'word0': k == 0})
    return out

case = {}
if os.path.isfile(os.path.join(CASE, 'case.json')):
    case = json.load(open(os.path.join(CASE, 'case.json'), encoding='utf-8'))
task = case.get('task', 'speak')

recs = {os.path.splitext(os.path.basename(p))[0]: tokens(json.load(open(p, encoding='utf-8')))
        for p in sorted(glob.glob(os.path.join(CASE, 'asr', '*.json')))}
recs = {n: r for n, r in recs.items() if r}
if len(recs) < 3:
    print('提示：只有 %d 套识别结果；标准是三套强识别（transcribe.py）' % len(recs))
if len(recs) < 2:
    sys.exit('至少需要两套识别结果（asr/*.json）才能评发音准确度')

def sm(a, b):
    return difflib.SequenceMatcher(None, [x['t'] for x in a], [x['t'] for x in b], autojunk=False)
def matched(a, b):
    return {i for blk in sm(a, b).get_matching_blocks() for i in range(blk.a, blk.a + blk.size)}
names = list(recs)
# reference = the most central transcript, measured both ways: a system that skipped a stretch
# must not win just because what little it wrote matches
central = {n: np.mean([2 * len(matched(recs[n], recs[m])) / max(1, len(recs[n]) + len(recs[m])) for m in names if m != n]) for n in names}
ref_name = max(central, key=central.get); ref = recs[ref_name]
need = max(2, math.ceil(len(names) * 2 / 3))
# sentence ends (pauses inside/between sentences, statement endings) come from the recogniser that
# punctuates most finely — transducer models like Parakeet often run sentences together
sent_ref = max(recs.values(), key=lambda r: sum(x['end'] for x in r))

# ---------- 发音准确度 ----------
votes = [1] * len(ref); heard_other = [set() for _ in ref]
for n in names:
    if n != ref_name:
        for i in matched(ref, recs[n]): votes[i] += 1
        for tag, i1, i2, j1, j2 in sm(ref, recs[n]).get_opcodes():
            if tag == 'replace':                       # heard as a different word (a skipped stretch is not a split)
                for i in range(i1, i2): heard_other[i] |= {x['t'] for x in recs[n][j1:j2]}
skip = {i + 3 for i in range(len(ref) - 3) if [x['t'] for x in ref[i:i + 3]] == ['my', 'name', 'is']}   # own name
scored = [i for i in range(len(ref)) if i not in skip]
split = [{'token': ref[i]['t'], 'at': round(ref[i]['s'], 1), 'votes': f'{votes[i]}/{len(names)}', 'also_heard': sorted(heard_other[i])}
         for i in scored if need <= votes[i] < len(names) and heard_other[i] and ref[i]['t'] not in FUNC]
not_alike = [{'token': ref[i]['t'], 'at': round(ref[i]['s'], 1), 'votes': f'{votes[i]}/{len(names)}'}
             for i in scored if votes[i] < need]
intel = sum(votes[i] >= need for i in scored) / max(1, len(scored))

misread, accuracy = [], None
if task == 'read':
    if not case.get('original'):
        sys.exit('朗读案例（task=read）必须在 case.json 写 original（课文原文），否则读错的词会被识别器按上下文改对、查不出来')
    orig = tokens([{'w': w} for w in case['original'].split()])
    ok = [0] * len(orig); heard = [[] for _ in orig]; when = [None] * len(orig)
    for n in names:
        for tag, i1, i2, j1, j2 in sm(orig, recs[n]).get_opcodes():
            for k in range(i1, i2):
                if tag == 'equal':
                    ok[k] += 1; when[k] = when[k] or recs[n][j1 + k - i1]['s']
                elif tag == 'replace':
                    j = j1 + min(k - i1, j2 - j1 - 1); heard[k].append(recs[n][j]['t']); when[k] = when[k] or recs[n][j]['s']
                else:
                    heard[k].append('（没读到）')
    for k, x in enumerate(orig):
        if ok[k] < need:
            misread.append({'word': x['t'], 'heard': heard[k], 'at': round(when[k], 1) if when[k] is not None else None,
                            'votes_as_written': f'{ok[k]}/{len(names)}'})
    accuracy = sum(o >= need for o in ok) / max(1, len(orig))

own_name = {str(case.get('name', '')).lower()}
for r in recs.values():                                  # whatever each system made of the child's name
    own_name |= {r[i + 3]['t'] for i in range(len(r) - 3) if [x['t'] for x in r[i:i + 3]] == ['my', 'name', 'is']}
soft = {}
for n in names:
    for x in recs[n]:
        if (x['p'] is not None and x['p'] < 0.5 and x['t'] not in FUNC and x['t'] not in FILLERS
                and x['t'] not in own_name and len(x['t']) > 1):
            key = (x['t'], round(x['s']))
            soft[key] = min(soft.get(key, 1), x['p'])
soft = [{'token': t, 'at': s, 'p': round(p, 2)} for (t, s), p in sorted(soft.items(), key=lambda kv: kv[0][1])]

# ---------- 流利度 ----------
snd = parselmouth.Sound(WAV)
inten = snd.to_intensity(minimum_pitch=150, time_step=0.01)
t_i, v_i = inten.xs(), inten.values[0]
on = v_i > (np.percentile(v_i, 95) - 15)
runs, st = [], None
for k, x in enumerate(on):
    if x and st is None: st = t_i[k]
    if not x and st is not None: runs.append([st, t_i[k]]); st = None
if st is not None: runs.append([st, t_i[-1]])
merged = []
for r in runs:
    if merged and r[0] - merged[-1][1] < 0.2: merged[-1][1] = r[1]
    else: merged.append(r)
merged = [r for r in merged if r[1] - r[0] >= 0.08]
if not merged: sys.exit('录音里没有检测到语音')
span = merged[-1][1] - merged[0][0]
speech_time = sum(b - a for a, b in merged if b - a >= 0.15)
pauses = []
for a, b in zip(merged, merged[1:]):
    d = b[0] - a[1]
    if d >= 1.0:
        mid = (a[1] + b[0]) / 2
        before = [x for x in sent_ref if x['s'] <= mid]
        pauses.append({'start': round(float(a[1]), 2), 'end': round(float(b[0]), 2), 'seconds': round(float(d), 1),
                       'inside_sentence': bool(before) and not before[-1]['end']})
n_words = sum(1 for x in ref if x['word0'])
rate = n_words / span * 60
artic = n_words / max(speech_time, 1e-6) * 60
inside = [p for p in pauses if p['inside_sentence']]
between = [p['seconds'] for p in pauses if not p['inside_sentence']]
inside_per_min = len(inside) / span * 60
long_per_min = len(pauses) / span * 60          # all >= 1 s pauses; the banding gate (see rubric)

def repeats(toks):
    out = []
    for n in (3, 2, 1):
        for i in range(len(toks) - 2 * n + 1):
            a = [x['t'] for x in toks[i:i + n]]; b = [x['t'] for x in toks[i + n:i + 2 * n]]
            if a == b and (n > 1 or len(a[0]) > 1) and all(abs(toks[i + n]['s'] - o) > 1.0 for o in out):
                out.append(toks[i + n]['s'])
    return out
rep_times = []
for n in names:
    for tt in repeats(recs[n]):
        hit = next((r for r in rep_times if abs(r['at'] - tt) <= 1.5), None)
        if hit: hit['by'].add(n)
        else: rep_times.append({'at': tt, 'by': {n}})
rep_times = [r for r in rep_times if len(r['by']) >= 2]

pitch = snd.to_pitch_ac(time_step=0.01, pitch_floor=150, pitch_ceiling=600, octave_jump_cost=0.6)
f0 = pitch.selected_array['frequency']; t_p = pitch.xs()
all_words = [x for n in names for x in recs[n]]
orphans = []                                             # voiced sounds no recogniser wrote down = fillers
for a, b in merged:
    if not 0.2 <= b - a <= 1.5: continue
    if any(x['s'] - 0.25 < b and x['e'] + 0.25 > a for x in all_words): continue
    m = (t_p >= a) & (t_p <= b)
    if m.sum() and (f0[m] > 0).mean() >= 0.5:
        orphans.append({'start': round(float(a), 2), 'seconds': round(float(b - a), 2)})
asr_fillers = max((sum(1 for x in recs[n] if x['t'] in FILLERS) for n in names), default=0)
fillers = asr_fillers + len(orphans)
disfl_per_min = (len(rep_times) + fillers) / span * 60

# ---------- 语调与重音 ----------
voiced = f0[f0 > 0]
if len(voiced) < 20: sys.exit('有声片段太少，无法测音高')
med = float(np.median(voiced))
okf = (f0 >= med * 0.6) & (f0 <= med * 1.75)            # octave jumps are tracker errors, not melody
clean = f0[okf]
span_st = float(12 * np.log2(np.percentile(clean, 95) / np.percentile(clean, 5)))
ends = []
for x in sent_ref:
    if not x['end'] or x['q']: continue
    # the sentence ends where the speech run holding its last word ends (word end stamps can run
    # into the following silence, so the word's START is the anchor)
    own = [r for r in merged if r[1] - r[0] >= 0.15 and r[0] <= x['s'] + 0.3]
    edge = max(own, key=lambda r: r[0])[1] if own else x['e']
    idx = np.where(okf & (t_p >= edge - 0.5) & (t_p <= edge + 0.02))[0]
    stretches, cur = [], []
    for i in idx:
        if cur and i - cur[-1] > 1: stretches.append(cur); cur = []
        cur.append(i)
    if cur: stretches.append(cur)
    stretches = [s_ for s_ in stretches if len(s_) >= 8]
    if not stretches: ends.append({'at': round(float(edge), 1), 'move': None}); continue
    last = np.array(stretches[-1]); t_last = t_p[last[-1]]
    lead = f0[last[(t_p[last] >= t_last - 0.30) & (t_p[last] <= t_last - 0.12)]]
    if len(lead) < 3: lead = f0[last[:3]]
    move = float(12 * np.log2(np.median(f0[last[-4:]]) / np.median(lead)))
    ends.append({'at': round(float(edge), 1), 'move': round(move, 1), 'shape': 'fall' if move <= -1 else 'rise' if move >= 1 else 'level'})
measured = [e for e in ends if e['move'] is not None]
falls = sum(e['shape'] == 'fall' for e in measured)
fall_share = falls / len(measured) if measured else 0.0

# ---------- 覆盖检查：任一识别器在别人听到语音的地段整段沉默，必须标记 ----------
# 有声段 (merged) 是"这里有语音"的地面真值；识别器在一段里写出至少一个词即算"醒着"。
# 一致率只在 >= need 套识别器都醒着的地段上算；参考转写本身漏掉的地段也要量出来。
COVER_MIN_RUN = 0.5      # 短于 0.5 秒的有声段不参与覆盖判定（词界间隙不算沉默）
COVER_MIN_SILENT = 1.0   # 沉默 >= 1 秒才标记（Parakeet 案是约 17 秒）
def _awake(n, a, b):
    return any(x['s'] - 0.25 < b and x['e'] + 0.25 > a for x in recs[n])
cover_runs = [r for r in merged if r[1] - r[0] >= COVER_MIN_RUN]
silent_stretches = []
for n in names:
    for a, b in cover_runs:
        others = [m for m in names if m != n and _awake(m, a, b)]
        if not _awake(n, a, b) and others and b - a >= COVER_MIN_SILENT:
            silent_stretches.append({'recogniser': n, 'start': round(float(a), 2),
                                     'end': round(float(b), 2), 'seconds': round(float(b - a), 1),
                                     'heard_by': sorted(others)})
def _run_of(t):
    for a, b in cover_runs:
        if a - 0.25 <= t <= b + 0.25:
            return (a, b)
    return None
covered_scored = []
for i in scored:
    r = _run_of(ref[i]['s'])
    if r is None or sum(1 for n in names if _awake(n, *r)) >= need:
        covered_scored.append(i)
intel_all = intel
intel = (sum(votes[i] >= need for i in covered_scored) / len(covered_scored)) if covered_scored else intel_all
voiced_seconds = sum(b - a for a, b in cover_runs)
ref_covered_seconds = sum(b - a for a, b in cover_runs
                          if any(x['s'] - 0.25 < b and x['e'] + 0.25 > a for x in ref))
ref_coverage = ref_covered_seconds / voiced_seconds if voiced_seconds else 1.0

# ---------- fixed banding rules (mirror references/rubric.md) ----------
def band(rules):
    for flowers, cond in rules:
        if cond: return flowers
    return 1
acc = accuracy if task == 'read' else intel
unsure = [m for m in soft if m['p'] < 0.4]                  # a content word the recogniser itself doubts
pron = band([(5, acc >= 0.98 and not split and not unsure), (4, acc >= 0.93), (3, acc >= 0.85), (2, acc >= 0.70)])
flu = band([(5, artic >= 150 and long_per_min <= 6 and disfl_per_min <= 0.5),
            (4, artic >= 120 and long_per_min <= 11 and disfl_per_min <= 1.5),
            (3, artic >= 90 and long_per_min <= 16 and disfl_per_min <= 4),
            (2, artic >= 60)])
enough = len(measured) >= 3
varied = any(e['shape'] in ('rise', 'level') for e in measured)   # one tune repeated is not melody control
near4 = falls >= len(measured) - 3 and fall_share >= 0.55          # few endings: one ending is worth ~12 points
pros = band([(5, enough and span_st >= 9 and fall_share >= 0.85 and varied),
             (4, enough and span_st >= 6 and (fall_share >= 0.65 or near4)),
             (3, span_st >= 4 and (fall_share >= 0.40 or not enough)),
             (2, span_st >= 2)])

result = {
    'task': task, 'recognisers': names, 'reference': ref_name, 'majority_needed': f'{need}/{len(names)}',
    'pronunciation': {'flowers': pron, 'basis': 'original text' if task == 'read' else 'recogniser agreement',
                      'read_accuracy': None if accuracy is None else round(accuracy, 3), 'misread': misread,
                      'intelligibility': round(intel, 3), 'not_heard_alike': not_alike, 'split_votes': split,
                      'low_probability': soft},
    'fluency': {'flowers': flu, 'words': n_words, 'speaking_span_seconds': round(float(span), 1),
                'speech_seconds': round(float(speech_time), 1), 'articulation_wpm': round(artic),
                'overall_wpm': round(rate), 'pauses_1s_plus': pauses,
                'inside_sentence_pauses': len(inside), 'inside_sentence_pauses_per_minute': round(inside_per_min, 1), 'long_pauses_per_minute': round(long_per_min, 1),
                'between_sentence_pause_median': round(float(np.median(between)), 1) if between else None,
                'repeats': [{'at': round(r['at'], 1), 'heard_by': sorted(r['by'])} for r in rep_times],
                'fillers': fillers, 'fillers_unwritten': orphans},
    'prosody': {'flowers': pros, 'median_hz': round(med, 1), 'span_semitones': round(span_st, 1),
                'statement_endings': ends, 'falling': falls, 'measured': len(measured)},
    'coverage': {'voiced_seconds': round(float(voiced_seconds), 1),
                 'reference_coverage': round(ref_coverage, 3),
                 'silent_stretches': silent_stretches,
                 'intelligibility_all_tokens': round(intel_all, 3),
                 'intelligibility_covered_tokens': round(intel, 3),
                 'covered_tokens': len(covered_scored),
                 'scored_tokens': len(scored)},
    'note_low_probability': '低把握词：Whisper 对该词的把握 < 0.5；< 0.4 的内容词会挡住 5 朵',
    'note': '固定规则分档，未经真人评分校准；结果为形成性分档，不与任何考试成绩等效。',
}
with open(OUT, 'w', encoding='utf-8') as f: json.dump(result, f, ensure_ascii=False, indent=2)
print(f'recognisers: {", ".join(names)}  (reference: {ref_name}, majority {need}/{len(names)}, task {task})')
if task == 'read':
    print(f'发音准确度 {pron} 朵 — 原文按原样读出 {accuracy:.0%}；读成别的：{[(m["word"], m["heard"]) for m in misread]}')
else:
    print(f'发音准确度 {pron} 朵 — 多数听得一致 {intel:.0%}；没听一致：{[m["token"] for m in not_alike]}')
print(f'           有分歧：{[(m["token"], m["votes"]) for m in split]}；低把握词：{[(m["token"], m["p"]) for m in soft]}')
print(f'流利度     {flu} 朵 — 说话时语速 {round(artic)} 词/分（整段 {round(rate)}）；长停顿 {len(pauses)} 次（{long_per_min:.1f} 次/分，其中句中 {len(inside)} 次）；'
      f'句间停顿中位 {result["fluency"]["between_sentence_pause_median"]} 秒；重说 {len(rep_times)}；填充 {fillers}（其中未被转写 {len(orphans)}）')
print(f'语调与重音 {pros} 朵 — 音高跨度 {span_st:.1f} 半音；陈述句尾 {falls}/{len(measured)} 下降')
print('saved', OUT)
if silent_stretches:
    print('覆盖告警：' + '；'.join(
        f"{s['recogniser']} 在 {s['start']}–{s['end']} 秒沉默 {s['seconds']} 秒（{','.join(s['heard_by'])} 听到了）"
        for s in silent_stretches))
if ref_coverage < 0.9:
    print(f'覆盖告警：参考转写只覆盖了 {ref_coverage:.0%} 的有声时长，一致率分母不完整')
