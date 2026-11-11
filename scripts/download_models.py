#!/usr/bin/env python3
"""Download the three speech-recognition models into ../assets/models/ (NOT bundled in the repo).

All three run fully offline afterwards, on CPU, no API key.
  whisper-small.en/    Systran/faster-whisper-small.en   (~460 MB, MIT)
  whisper-medium.en/   Systran/faster-whisper-medium.en  (~1.5 GB, MIT)
  parakeet-tdt-0.6b-v2-int8/   NVIDIA Parakeet TDT 0.6b v2, sherpa-onnx int8 build (~630 MB, CC-BY-4.0)
transcribe.py finds them here by itself (no PARAKEET_DIR needed).

Usage:  python3 scripts/download_models.py [--only whisper|parakeet]
Mirrors (when huggingface.co / github.com are slow or blocked):
  HF_ENDPOINT=https://hf-mirror.com python3 scripts/download_models.py
  GH_PROXY=https://<your github proxy>/ python3 scripts/download_models.py   (prefixed to the release URL)
Skips what is already complete; a broken download resumes where it stopped.
Needs only the Python standard library."""
import argparse, os, sys, tarfile, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.normpath(os.path.join(BASE, '..', 'assets', 'models'))
HF = os.environ.get('HF_ENDPOINT', 'https://huggingface.co').rstrip('/')
GH = os.environ.get('GH_PROXY', '')
WHISPER = {'whisper-small.en': 'Systran/faster-whisper-small.en', 'whisper-medium.en': 'Systran/faster-whisper-medium.en'}
WHISPER_FILES = ['config.json', 'tokenizer.json', 'vocabulary.txt', 'model.bin']
PARAKEET = 'sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8'
PARAKEET_URL = f'{GH}https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{PARAKEET}.tar.bz2'
PARAKEET_DIR = 'parakeet-tdt-0.6b-v2-int8'

def fetch(url, path, tries=8):
    """Resumable: a broken transfer continues from the .part file (HTTP Range), up to `tries` times."""
    import time
    tmp = path + '.part'
    for attempt in range(1, tries + 1):
        have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        hdr = {'User-Agent': 'Mozilla/5.0'}
        if have: hdr['Range'] = f'bytes={have}-'
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=30) as r:
                if have and r.status != 206: have = 0                 # server ignored Range: start over
                total = have + int(r.headers.get('Content-Length') or 0)
                with open(tmp, 'ab' if have else 'wb') as f:
                    done, last = have, -1
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk: break
                        f.write(chunk); done += len(chunk)
                        if total and int(done * 10 / total) != last:
                            last = int(done * 10 / total)
                            print(f'    {os.path.basename(path)} {last * 10}% of {total / 1e6:.0f} MB', flush=True)
            if total and os.path.getsize(tmp) < total: raise IOError('transfer ended early')
            os.replace(tmp, path); return
        except Exception as e:
            if attempt == tries: raise
            print(f'    retry {attempt}/{tries - 1} after: {e}', flush=True); time.sleep(3 * attempt)

def whisper():
    for name, repo in WHISPER.items():
        d = os.path.join(MODELS, name); os.makedirs(d, exist_ok=True)
        for fn in WHISPER_FILES:
            p = os.path.join(d, fn)
            if os.path.exists(p): continue
            print(f'  {name}/{fn}  <- {HF}/{repo}')
            fetch(f'{HF}/{repo}/resolve/main/{fn}', p)
        print(f'ok  {name}')

def parakeet():
    d = os.path.join(MODELS, PARAKEET_DIR)
    need = ['encoder.int8.onnx', 'decoder.int8.onnx', 'joiner.int8.onnx', 'tokens.txt']
    if all(os.path.exists(os.path.join(d, f)) for f in need):
        print(f'ok  {PARAKEET_DIR} (already present)'); return
    arc = os.path.join(MODELS, PARAKEET + '.tar.bz2')
    if not os.path.exists(arc):
        print(f'  {PARAKEET}.tar.bz2  <- {PARAKEET_URL}')
        fetch(PARAKEET_URL, arc)
    os.makedirs(d, exist_ok=True)
    with tarfile.open(arc) as t:
        for m in t.getmembers():
            fn = os.path.basename(m.name)
            if m.isfile() and fn in need:
                with t.extractfile(m) as src, open(os.path.join(d, fn), 'wb') as dst: dst.write(src.read())
    if all(os.path.exists(os.path.join(d, f)) for f in need):
        try: os.remove(arc)
        except OSError: pass
        print(f'ok  {PARAKEET_DIR}')
    else:
        sys.exit('Parakeet 压缩包不完整，请删掉 assets/models/*.tar.bz2 重下')

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--only', choices=['whisper', 'parakeet'])
a = ap.parse_args()
os.makedirs(MODELS, exist_ok=True)
try:
    if a.only in (None, 'whisper'): whisper()
    if a.only in (None, 'parakeet'): parakeet()
except Exception as e:
    sys.exit(f'下载失败：{e}\n连不上时换镜像：HF_ENDPOINT=https://hf-mirror.com（Whisper），GH_PROXY=<github 代理前缀>（Parakeet）')
print('models in', MODELS)
