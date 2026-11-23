#!/usr/bin/env python3
"""Extract the data series the report builders draw from a recording — any audio or video file.
  peaks — max |amplitude| per 50 ms window, normalised 0..1: the bottom scene's waveform hill,
          and the recording length printed in the header (len(peaks) x 50 ms)
  f0    — Praat pitch every 50 ms (child range 150–600 Hz), 0 = unvoiced; only when
          praat-parselmouth is installed (the measured track uses it), otherwise left empty
Usage: python3 extract_audio_data.py [recording] [audio_data.json]
       recording: speech-16k.wav, or anything ffmpeg reads (mp4, m4a, mp3 …), decoded locally
Runs entirely on this machine with ffmpeg + numpy, so the listening track (听评档) uses it too:
it draws the child's own waveform and prints no measurement on the page."""
import json, os, subprocess, sys, wave, contextlib
import numpy as np

SR = 16000

def extract(src):
    """Return {'peaks': [...], 'f0': [...]} for any recording ffmpeg can read.
    Runs entirely on this machine; no cloud, no measurement printed on the page."""
    if not os.path.isfile(src):
        raise FileNotFoundError(f'找不到录音：{src}')
    raw = None
    if src.lower().endswith('.wav'):
        with contextlib.closing(wave.open(src, 'rb')) as wf:
            if wf.getframerate() == SR and wf.getnchannels() == 1 and wf.getsampwidth() == 2:
                raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(float)
    if raw is None:                       # any other format: decode to 16 kHz mono through ffmpeg
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                             capture_output=True, check=True).stdout
        raw = np.frombuffer(pcm, dtype=np.int16).astype(float)
    if not len(raw):
        raise ValueError('录音里没有读到声音')

    win = int(SR * 0.05)
    n = len(raw) // win
    peaks = [float(np.abs(raw[i * win:(i + 1) * win]).max()) for i in range(n)]
    mx = max(peaks) or 1.0
    peaks = [round(p / mx, 4) for p in peaks]

    f0 = []
    try:
        import parselmouth
        snd = parselmouth.Sound(raw / 32768.0, sampling_frequency=SR)
        pitch = snd.to_pitch(time_step=0.05, pitch_floor=150, pitch_ceiling=600)
        f0 = [round(float(v), 1) if v and v > 0 else 0 for v in pitch.selected_array['frequency']]
    except ImportError:
        pass
    return {'peaks': peaks, 'f0': f0, 'seconds': round(len(raw) / SR, 2)}

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'speech-16k.wav'
    out = sys.argv[2] if len(sys.argv) > 2 else 'audio_data.json'
    try:
        data = extract(src)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(str(e))
    except subprocess.CalledProcessError:
        sys.exit(f'ffmpeg 解不开这个文件：{src}')
    json.dump({'peaks': data['peaks'], 'f0': data['f0']}, open(out, 'w'))
    print(f"{out}: {len(data['peaks'])} peak windows, {len(data['f0'])} f0 points, duration {data['seconds']}s")

if __name__ == '__main__':
    main()
