#!/usr/bin/env python3
"""Native-audio analysis: Vosk word timing/confidence + Praat acoustics.

Usage: python3 analyze.py [speech-16k.wav]
Needs: pip packages vosk, praat-parselmouth, numpy; a Vosk English model
(set VOSK_MODEL, default /tmp/vosk-model-small-en-us-0.15).
EDIT PER CASE: TARGET (the expected text), SYL (syllable counts), sent_words
(sentence word lists). The Toto case below is the worked example.
Convert the recording first: ffmpeg -i recording.m4a -ar 16000 -ac 1 speech-16k.wav"""
import json, wave, contextlib
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
import parselmouth
from parselmouth.praat import call

SetLogLevel(-1)
import os, sys
WAV = sys.argv[1] if len(sys.argv) > 1 else 'speech-16k.wav'

TARGET = ("Hi I am Toto. This is my big round yellow face. These are my three big round blue eyes "
          "with six big black and yellow eyebrows. These are my two big pink ears. "
          "This is my big oval red mouth. I love the ugly silly and scary me.")
SYL = {'hi':1,'i':1,'am':1,'toto':2,'this':1,'is':1,'my':1,'big':1,'round':1,'yellow':2,'face':1,
 'these':1,'are':1,'three':1,'blue':1,'eyes':1,'with':1,'six':1,'black':1,'and':1,'eyebrows':2,
 'two':1,'pink':1,'ears':1,'oval':2,'red':1,'mouth':1,'love':1,'the':1,'ugly':2,'silly':2,'scary':2,'me':1}

# ---------- Vosk ----------
model = Model(os.environ.get('VOSK_MODEL', '/tmp/vosk-model-small-en-us-0.15'))
words = []
with contextlib.closing(wave.open(WAV, 'rb')) as wf:
    rec = KaldiRecognizer(model, wf.getframerate()); rec.SetWords(True)
    while True:
        data = wf.readframes(4000)
        if not data: break
        rec.AcceptWaveform(data)
    res = json.loads(rec.FinalResult())
words = res.get('result', [])
vosk_text = res.get('text', '')
print('VOSK TEXT:', vosk_text)
print(f'WORDS: {len(words)}')
for w in words:
    print(f"  {w['start']:6.2f}-{w['end']:6.2f}  conf={w['conf']:.2f}  {w['word']}")

dur_total = words[-1]['end'] if words else 0
speech_time = sum(w['end'] - w['start'] for w in words)
gaps = []
for a, b in zip(words, words[1:]):
    g = b['start'] - a['end']
    if g > 0.20:
        gaps.append({'after': a['word'], 'before': b['word'], 'gap': round(g, 2), 'at': round(a['end'], 2)})
print('GAPS>0.2s:', json.dumps(gaps))
syl_total = sum(SYL.get(w['word'], 1) for w in words)
print(f'SYL(vosk words)={syl_total} speech_time={speech_time:.1f}s artic_rate={syl_total/speech_time:.2f} syl/s')
low = sorted(words, key=lambda w: w['conf'])[:10]
print('LOWEST CONF:', [(w['word'], round(w['conf'], 2)) for w in low])
print('MEAN CONF:', round(float(np.mean([w['conf'] for w in words])), 3))

# word duration rhythm (nPVI over word durations)
durs = np.array([w['end'] - w['start'] for w in words])
npvi = float(np.mean(np.abs(np.diff(durs)) / ((durs[:-1] + durs[1:]) / 2)) * 100)
print(f'WORD-DUR nPVI={npvi:.0f}  CV={durs.std()/durs.mean():.2f}')

# ---------- Praat ----------
snd = parselmouth.Sound(WAV)
print('DURATION:', round(snd.get_total_duration(), 2))
pitch = snd.to_pitch(time_step=0.01, pitch_floor=150, pitch_ceiling=600)
f0 = pitch.selected_array['frequency']; f0v = f0[f0 > 0]
times = pitch.xs()
print(f'F0 voiced frames {len(f0v)}/{len(f0)}  mean={f0v.mean():.0f} median={np.median(f0v):.0f} '
      f'p10={np.percentile(f0v,10):.0f} p90={np.percentile(f0v,90):.0f} min={f0v.min():.0f} max={f0v.max():.0f}')
st_range = 12 * np.log2(np.percentile(f0v, 95) / np.percentile(f0v, 5))
print(f'F0 range p5-p95 = {st_range:.1f} semitones')
intensity = snd.to_intensity(time_step=0.01)
ival = intensity.values[0]; ival = ival[ival > 0]
print(f'INTENSITY mean={ival.mean():.1f} dB  sd={ival.std():.1f}  min={ival.min():.1f} max={ival.max():.1f}')
harm = call(snd, 'To Harmonicity (cc)', 0.01, 150, 0.1, 1.0)
print('HNR mean:', round(call(harm, 'Get mean', 0, 0), 1), 'dB')
pp = call(snd, 'To PointProcess (periodic, cc)', 150, 600)
jit = call([snd, pp], 'Get jitter (local)', 0, 0, 0.0001, 0.02, 1.3)
shi = call([snd, pp], 'Get shimmer (local)', 0, 0, 0.0001, 0.02, 1.3, 1.6)
print(f'JITTER={jit*100:.2f}%  SHIMMER={shi*100:.2f}%')

# per-sentence F0: sentence boundaries by target word sequence
sent_words = [['hi','i','am','toto'], ['this','is','my','big','round','yellow','face'],
 ['these','are','my','three','big','round','blue','eyes','with','six','big','black','and','yellow','eyebrows'],
 ['these','are','my','two','big','pink','ears'], ['this','is','my','big','oval','red','mouth'],
 ['i','love','the','ugly','silly','and','scary','me']]
idx = 0
print('SENTENCES:')
for si, sw_ in enumerate(sent_words):
    seg = words[idx:idx + len(sw_)]; idx += len(sw_)
    if not seg: continue
    t0, t1 = seg[0]['start'], seg[-1]['end']
    m = (times >= t0) & (times <= t1) & (f0 > 0)
    seg_f0 = f0[m]
    # terminal: last 0.35s voiced vs the 0.35s before
    mt = (times >= t1 - 0.35) & (times <= t1) & (f0 > 0)
    mp = (times >= t1 - 0.8) & (times < t1 - 0.35) & (f0 > 0)
    term = f0[mt].mean() if mt.sum() > 3 else float('nan')
    pre = f0[mp].mean() if mp.sum() > 3 else float('nan')
    slope_st = 12 * np.log2(term / pre) if pre == pre and term == term else float('nan')
    sp_time = sum(w['end'] - w['start'] for w in seg)
    syl = sum(SYL.get(w['word'], 1) for w in seg)
    print(f"  S{si+1} {t0:5.2f}-{t1:5.2f}s  words={len(seg)} syl={syl} rate={syl/max(sp_time,0.01):.1f} syl/s "
          f"F0mean={seg_f0.mean():.0f} F0max={seg_f0.max():.0f} terminal={slope_st:+.1f} st  conf={np.mean([w['conf'] for w in seg]):.2f}")

# stress check on 2-syllable words: split word span in half, compare intensity
print('STRESS (int+F0 peak half):')
inten_t = intensity.xs(); inten_v = intensity.values[0]
for w in words:
    if SYL.get(w['word'], 1) == 2:
        mid = (w['start'] + w['end']) / 2
        m1 = (inten_t >= w['start']) & (inten_t < mid); m2 = (inten_t >= mid) & (inten_t <= w['end'])
        mf1 = (times >= w['start']) & (times < mid) & (f0 > 0); mf2 = (times >= mid) & (times <= w['end']) & (f0 > 0)
        i1, i2 = inten_v[m1].max() if m1.sum() else 0, inten_v[m2].max() if m2.sum() else 0
        p1 = f0[mf1].max() if mf1.sum() > 2 else 0; p2 = f0[mf2].max() if mf2.sum() > 2 else 0
        print(f"  {w['word']:9s} {w['start']:5.2f}s dur={w['end']-w['start']:.2f}  int {i1:.0f}/{i2:.0f} dB  F0peak {p1:.0f}/{p2:.0f} Hz  conf={w['conf']:.2f}")

# formants for anchor vowels (child: max formant 8000, 5 formants)
print('FORMANTS (midpoint of word):')
for target_w, vowel in [('blue','u'), ('big','I'), ('pink','I'), ('red','e'), ('yellow','e'), ('face','eI')]:
    for w in words:
        if w['word'] == target_w:
            mid = (w['start'] + w['end']) / 2
            frm = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5, maximum_formant=8000, window_length=0.025, pre_emphasis_from=50)
            f1 = frm.get_value_at_time(1, mid); f2 = frm.get_value_at_time(2, mid)
            print(f"  {target_w:7s} /{vowel}/  F1={f1:.0f} F2={f2:.0f}")
            break
