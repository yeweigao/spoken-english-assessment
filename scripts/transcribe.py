#!/usr/bin/env python3
"""Run the independent recognisers on the recording and write one word list per system into asr/.

Usage (in the case directory):  python3 transcribe.py [speech-16k.wav]

Writes asr/<system>.json = [{"w": "Hello,", "s": 0.72, "e": 1.06, "p": 0.98}, ...]
  whisper-small   faster-whisper small.en   (word probability p)
  whisper-medium  faster-whisper medium.en  (word probability p)
  parakeet        NVIDIA Parakeet TDT 0.6b v2 through sherpa-onnx; no p
All models run locally on CPU (no API key, the audio never leaves the machine). Get them once with
scripts/download_models.py into assets/models/ — this script uses them from there. Without them,
Whisper falls back to downloading into the Hugging Face cache, and PARAKEET_DIR can point elsewhere.
Three strong systems are the standard. Vosk small is NOT used: on a child's voice it returns
near-random words while still reporting high confidence.

Every system has a language model that repairs words from context (a mule read as "meal" is
written "meal" by all three). So agreement between systems shows the speech was understandable,
not that each word was read right — for a read-aloud, score_sound.py also compares with the
original text in case.json.

Needs: faster-whisper, numpy; optional sherpa-onnx. Audio is passed as an array, not a path
(some PyAV builds reject faster-whisper's file-open call)."""
import json, os, sys, wave
import numpy as np

WAV = sys.argv[1] if len(sys.argv) > 1 else 'speech-16k.wav'
os.makedirs('asr', exist_ok=True)
with wave.open(WAV) as wf:
    if wf.getframerate() != 16000 or wf.getnchannels() != 1:
        sys.exit('先转成 16 kHz 单声道：ffmpeg -i 输入 -ar 16000 -ac 1 speech-16k.wav')
    audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768

MODELS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'models'))
from faster_whisper import WhisperModel
for size in ('small', 'medium'):
    local = os.path.join(MODELS, f'whisper-{size}.en')
    src = local if os.path.isfile(os.path.join(local, 'model.bin')) else f'{size}.en'
    m = WhisperModel(src, device='cpu', compute_type='int8')
    segs, _ = m.transcribe(audio, word_timestamps=True, language='en', beam_size=5,
                           vad_filter=False, condition_on_previous_text=False)
    out = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2), 'p': round(w.probability, 3)}
           for s in segs for w in s.words if w.word.strip()]
    json.dump(out, open(f'asr/whisper-{size}.json', 'w'), ensure_ascii=False)
    print(f'whisper-{size}: {len(out)} words —', ' '.join(x['w'] for x in out)[:160], '…')

pdir = os.environ.get('PARAKEET_DIR') or os.path.join(MODELS, 'parakeet-tdt-0.6b-v2-int8')
if pdir and os.path.isdir(pdir):
    import sherpa_onnx
    r = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f'{pdir}/encoder.int8.onnx', decoder=f'{pdir}/decoder.int8.onnx', joiner=f'{pdir}/joiner.int8.onnx',
        tokens=f'{pdir}/tokens.txt', model_type='nemo_transducer', num_threads=4)
    st = r.create_stream(); st.accept_waveform(16000, audio); r.decode_stream(st)
    words = []
    for t, s in zip(st.result.tokens, st.result.timestamps):      # sub-word tokens -> words
        if t.startswith(' ') or not words: words.append({'w': t.strip(), 's': round(s, 2), 'e': round(s + 0.2, 2)})
        elif t.strip() in '.,?!': words[-1]['w'] += t.strip()      # punctuation doesn't extend the word in time
        else: words[-1]['w'] += t; words[-1]['e'] = round(s + 0.2, 2)
    for a, b in zip(words, words[1:]): a['e'] = min(a['e'], b['s'])
    words = [w for w in words if w['w']]
    json.dump(words, open('asr/parakeet.json', 'w'), ensure_ascii=False)
    print(f'parakeet: {len(words)} words')
else:
    print('提示：没找到 Parakeet（先运行 scripts/download_models.py），只有两套 Whisper；评发音需要三套')
