#!/usr/bin/env python3
"""Extract the two data series the report builders draw from a 16 kHz mono WAV:
  peaks — max |amplitude| per 50 ms window, normalised 0..1 (bubble waveform bars)
  f0    — Praat pitch every 50 ms (child range 150–600 Hz), 0 = unvoiced (melody line)
Usage: python3 extract_audio_data.py [speech-16k.wav] [audio_data.json]
Needs: praat-parselmouth, numpy."""
import json, sys, wave, contextlib
import numpy as np
import parselmouth

WAV = sys.argv[1] if len(sys.argv) > 1 else 'speech-16k.wav'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'audio_data.json'

with contextlib.closing(wave.open(WAV, 'rb')) as wf:
    sr = wf.getframerate()
    raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(float)
win = int(sr * 0.05)
n = len(raw) // win
peaks = [float(np.abs(raw[i * win:(i + 1) * win]).max()) for i in range(n)]
mx = max(peaks) or 1.0
peaks = [round(p / mx, 4) for p in peaks]

snd = parselmouth.Sound(WAV)
pitch = snd.to_pitch(time_step=0.05, pitch_floor=150, pitch_ceiling=600)
f0 = [round(float(v), 1) if v and v > 0 else 0 for v in pitch.selected_array['frequency']]
json.dump({'peaks': peaks, 'f0': f0}, open(OUT, 'w'))
print(f'{OUT}: {len(peaks)} peak windows, {len(f0)} f0 points, duration {len(raw) / sr:.2f}s')
