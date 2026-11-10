#!/usr/bin/env python3
"""Download the report fonts into ../assets/fonts/ (they are NOT bundled in the repo).

All four families are open-licensed (SIL OFL): Noto Sans SC, Inter, ZCOOL KuaiLe,
Patrick Hand. Sources are the google/fonts GitHub repository. The two variable
fonts are instanced to the static weights the builders expect:
  Noto Sans SC -> NotoSC-Regular.ttf (wght 400), NotoSC-SemiB.ttf (wght 600)
  Inter        -> Inter-Reg.ttf (wght 400),    Inter-BoldF.ttf (wght 700), Inter-Light.ttf (wght 300)
Skips files that already exist. Needs: fonttools (pip install fonttools)."""
import os, sys, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.normpath(os.path.join(BASE, '..', 'assets', 'fonts'))
TMP = os.path.join(FONTDIR, '.dl')
GF = 'https://github.com/google/fonts/raw/main/ofl'
STATIC = {
    'ZCOOLKuaiLe.ttf': f'{GF}/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf',
    'PatrickHand.ttf': f'{GF}/patrickhand/PatrickHand-Regular.ttf',
}
VARIABLE = {  # out_name -> (url, axis pins)
    'NotoSC-Regular.ttf': (f'{GF}/notosanssc/NotoSansSC%5Bwght%5D.ttf', {'wght': 400}),
    'NotoSC-SemiB.ttf':   (f'{GF}/notosanssc/NotoSansSC%5Bwght%5D.ttf', {'wght': 600}),
    'Inter-Reg.ttf':      (f'{GF}/inter/Inter%5Bopsz%2Cwght%5D.ttf', {'opsz': 14, 'wght': 400}),
    'Inter-BoldF.ttf':    (f'{GF}/inter/Inter%5Bopsz%2Cwght%5D.ttf', {'opsz': 14, 'wght': 700}),
    'Inter-Light.ttf':    (f'{GF}/inter/Inter%5Bopsz%2Cwght%5D.ttf', {'opsz': 14, 'wght': 300}),
}

def fetch(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r, open(path, 'wb') as f:
        f.write(r.read())

def main():
    os.makedirs(TMP, exist_ok=True)
    cache = {}
    todo = {k: v for k, v in {**STATIC, **VARIABLE}.items()
            if not os.path.exists(os.path.join(FONTDIR, k))}
    if not todo:
        print('all fonts already present in', FONTDIR); return
    for out, src in todo.items():
        dest = os.path.join(FONTDIR, out)
        if isinstance(src, str):  # static
            print('downloading', out); fetch(src, dest)
        else:
            url, pins = src
            if url not in cache:
                tmp = os.path.join(TMP, os.path.basename(out) + '.vf.ttf')
                print('downloading variable font for', out); fetch(url, tmp); cache[url] = tmp
            from fontTools import ttLib
            from fontTools.varLib.instancer import instantiateVariableFont
            f = ttLib.TTFont(cache[url])
            instantiateVariableFont(f, pins, inplace=True, updateFontNames=True)
            f['OS/2'].usWeightClass = pins['wght']
            f.save(dest); print('instanced', out, pins)
    import shutil; shutil.rmtree(TMP, ignore_errors=True)
    print('fonts ready in', FONTDIR)

if __name__ == '__main__':
    main()
