#!/usr/bin/env python3
"""Acoustic measurements for the back page (technical indicators) — works for any case, nothing to edit.

Usage (in the case directory, after transcribe.py):  python3 analyze.py [speech-16k.wav]
Reads the word timings of asr/whisper-small.json (or the first asr/*.json); sentences are cut at
the recogniser's . ? ! marks. Writes analysis.json and prints a summary:
  per-sentence rate and terminal pitch movement, pitch range, intensity, HNR, jitter/shimmer,
  and a two-half intensity/pitch comparison on multi-syllable words (word stress).
Needs: praat-parselmouth, numpy."""
import glob, json, os, re, sys
import numpy as np
import parselmouth
from parselmouth.praat import call

WAV = sys.argv[1] if len(sys.argv) > 1 else 'speech-16k.wav'
src = 'asr/whisper-small.json' if os.path.isfile('asr/whisper-small.json') else (sorted(glob.glob('asr/*.json')) or [None])[0]
if not src: sys.exit('先运行 transcribe.py 生成 asr/*.json')
words = [w for w in json.load(open(src, encoding='utf-8')) if re.sub(r"[^A-Za-z0-9']", '', w['w'])]

def syllables(word):
    """Vowel-group estimate (good enough for children's vocabulary; silent final e dropped)."""
    w = re.sub(r"[^a-z]", '', word.lower())
    if not w: return 1
    if w.isdigit(): return 1
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and not w.endswith(('le', 'ee')) and n > 1: n -= 1
    return max(1, n)

snd = parselmouth.Sound(WAV)
pitch = snd.to_pitch(time_step=0.01, pitch_floor=150, pitch_ceiling=600)
f0 = pitch.selected_array['frequency']; times = pitch.xs(); f0v = f0[f0 > 0]
intensity = snd.to_intensity(time_step=0.01)
it, iv = intensity.xs(), intensity.values[0]
harm = call(snd, 'To Harmonicity (cc)', 0.01, 150, 0.1, 1.0)
pp = call(snd, 'To PointProcess (periodic, cc)', 150, 600)
jit = call(pp, 'Get jitter (local)', 0, 0, 0.0001, 0.02, 1.3)              # PointProcess only
shi = call([snd, pp], 'Get shimmer (local)', 0, 0, 0.0001, 0.02, 1.3, 1.6)  # Sound + PointProcess

sentences, cur = [], []
for w in words:
    cur.append(w)
    if w['w'][-1:] in '.?!': sentences.append(cur); cur = []
if cur: sentences.append(cur)
sent_out = []
for k, seg in enumerate(sentences):
    t0, t1 = seg[0]['s'], seg[-1]['e']
    mt = (times >= t1 - 0.35) & (times <= t1) & (f0 > 0)
    mp = (times >= t1 - 0.8) & (times < t1 - 0.35) & (f0 > 0)
    term = 12 * np.log2(f0[mt].mean() / f0[mp].mean()) if mt.sum() > 3 and mp.sum() > 3 else None
    syl = sum(syllables(w['w']) for w in seg)
    dur = sum(w['e'] - w['s'] for w in seg)
    sent_out.append({'text': ' '.join(w['w'] for w in seg), 'start': t0, 'end': t1, 'syllables': syl,
                     'syl_per_s': round(syl / max(dur, 0.01), 2), 'terminal_st': None if term is None else round(float(term), 1)})

stress = []
for w in words:
    if syllables(w['w']) == 2:
        mid = (w['s'] + w['e']) / 2
        m1 = (it >= w['s']) & (it < mid); m2 = (it >= mid) & (it <= w['e'])
        if m1.sum() and m2.sum():
            stress.append({'word': w['w'], 'at': w['s'], 'int_first_minus_second_db': round(float(iv[m1].max() - iv[m2].max()), 1)})

res = {
    'source_words': src, 'duration_s': round(snd.get_total_duration(), 2),
    'f0': {'median_hz': round(float(np.median(f0v)), 1), 'p5_p95_semitones': round(float(12 * np.log2(np.percentile(f0v, 95) / np.percentile(f0v, 5))), 1)},
    'intensity_db': {'mean': round(float(iv[iv > 0].mean()), 1), 'sd': round(float(iv[iv > 0].std()), 1)},
    'hnr_db': round(call(harm, 'Get mean', 0, 0), 1), 'jitter_pct': round(jit * 100, 2), 'shimmer_pct': round(shi * 100, 2),
    'syllables_per_second_speaking': round(sum(s['syllables'] for s in sent_out) / max(sum(w['e'] - w['s'] for w in words), 0.01), 2),
    'sentences': sent_out, 'two_syllable_stress': stress,
}
json.dump(res, open('analysis.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"时长 {res['duration_s']} s · 音高中位 {res['f0']['median_hz']} Hz · 跨度 {res['f0']['p5_p95_semitones']} 半音 · "
      f"HNR {res['hnr_db']} dB · jitter {res['jitter_pct']}% · shimmer {res['shimmer_pct']}% · "
      f"说话时 {res['syllables_per_second_speaking']} 音节/秒 · {len(sent_out)} 句")
print('saved analysis.json')
