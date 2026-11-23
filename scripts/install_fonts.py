#!/usr/bin/env python3
"""Install the report's three fonts on THIS computer, so the editable PPT looks like the PDF.

The fonts ship inside the skill (assets/fonts, SIL Open Font License — licence texts beside them):
  Noto Sans SC Regular + SemiBold (思源黑体) — all body text
  ZCOOL KuaiLe (站酷快乐体)                   — title, headings, 老师说, the verdict stamps
Installs for the current user only: no administrator password, nothing system-wide.
  macOS    ~/Library/Fonts
  Windows  %LOCALAPPDATA%\\Microsoft\\Windows\\Fonts + the per-user font registry key
  Linux    ~/.local/share/fonts, then fc-cache
Already-installed fonts are skipped. Quit and reopen PowerPoint / WPS / Keynote afterwards.
Usage:  python3 scripts/install_fonts.py        (Windows: py scripts\\install_fonts.py)
Needs only the Python standard library."""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.normpath(os.path.join(HERE, '..', 'assets', 'fonts'))
FONTS = {  # file -> name shown in Office's font list (and the Windows registry entry)
    'NotoSC-Regular.ttf': 'Noto Sans SC Regular',
    'NotoSC-SemiB.ttf': 'Noto Sans SC SemiBold',
    'ZCOOLKuaiLe.ttf': 'ZCOOL KuaiLe Regular',
}

def target_dir():
    if sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Fonts')
    if sys.platform.startswith('win'):
        return os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Windows', 'Fonts')
    return os.path.expanduser('~/.local/share/fonts')

def main():
    missing = [f for f in FONTS if not os.path.isfile(os.path.join(FONTDIR, f))]
    if missing:
        sys.exit(f'skill 包里缺字体：{", ".join(missing)}（在 {FONTDIR}）。可先运行 scripts/download_fonts.py')
    dst = target_dir(); os.makedirs(dst, exist_ok=True)
    done, skipped = [], []
    for fn, name in FONTS.items():
        to = os.path.join(dst, fn)
        if os.path.isfile(to) and os.path.getsize(to) == os.path.getsize(os.path.join(FONTDIR, fn)):
            skipped.append(name); continue
        shutil.copyfile(os.path.join(FONTDIR, fn), to)
        if sys.platform.startswith('win'):              # per-user fonts must also be registered
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows NT\CurrentVersion\Fonts',
                                0, winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, f'{name} (TrueType)', 0, winreg.REG_SZ, to)
        done.append(name)
    if sys.platform.startswith('win') and done:          # tell running programs the font list changed
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0x0002, 1000, None)
    if not sys.platform.startswith(('win', 'darwin')) and done and shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f', dst], check=False)
    if done: print('已安装：' + '、'.join(done) + f'（{dst}）')
    if skipped: print('已存在，跳过：' + '、'.join(skipped))
    print('完成。请退出并重新打开 PowerPoint / WPS / Keynote，再打开 report-simple.pptx。')

if __name__ == '__main__':
    main()
