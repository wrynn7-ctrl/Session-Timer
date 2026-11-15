#!/usr/bin/env python3
"""Drives the installed app on a running emulator to check Export CSV end to end.

Logs a short session, taps Export CSV, saves through Android's real "save as" screen, then checks
the CSV landed in Downloads. Screenshots of each step and the saved file go into the output folder.

Usage: python3 scripts/emulator-export-test.py <output-folder>
"""
import os, re, subprocess, sys, time
import xml.etree.ElementTree as ET

OUT = sys.argv[1] if len(sys.argv) > 1 else 'emulator-out'
APP = 'com.sessiondial.app'
os.makedirs(OUT, exist_ok=True)
shot_no = 0


def adb(*args, binary=False, check=True):
    r = subprocess.run(['adb', *args], capture_output=True, timeout=120)
    if check and r.returncode != 0:
        raise RuntimeError('adb %s failed: %s' % (' '.join(args), r.stderr.decode(errors='replace')))
    return r.stdout if binary else r.stdout.decode(errors='replace')


def shot(label):
    global shot_no
    shot_no += 1
    path = os.path.join(OUT, '%02d-%s.png' % (shot_no, label))
    with open(path, 'wb') as f:
        f.write(adb('exec-out', 'screencap', '-p', binary=True))
    print('screenshot:', path, flush=True)


def nodes():
    """Everything on screen that has text, as (text, enabled, centre-x, centre-y)."""
    raw = adb('exec-out', 'uiautomator', 'dump', '/dev/tty', check=False)
    m = re.search(r'<\?xml.*</hierarchy>', raw, re.S)
    if not m:
        return []
    found = []
    for n in ET.fromstring(m.group(0)).iter('node'):
        text = (n.get('text') or n.get('content-desc') or '').strip()
        b = re.match(r'\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]', n.get('bounds') or '')
        if text and b:
            x1, y1, x2, y2 = map(int, b.groups())
            found.append((text, n.get('enabled') == 'true', (x1 + x2) // 2, (y1 + y2) // 2, y2 - y1))
    return found


def screen_size():
    w, h = re.search(r'(\d+)x(\d+)', adb('shell', 'wm', 'size')).groups()
    return int(w), int(h)


W, H = screen_size()


def find(pattern, timeout=60, scroll=False):
    """Wait for visible text matching the pattern; optionally scroll down the page to look for it."""
    rx = re.compile(pattern, re.I)
    end = time.time() + timeout
    while time.time() < end:
        for text, enabled, x, y, height in nodes():
            if rx.fullmatch(text) and height > 0 and 0.08 * H < y < 0.92 * H:
                return text, enabled, x, y
        if scroll:
            adb('shell', 'input', 'swipe', str(W // 2), str(int(H * 0.7)), str(W // 2), str(int(H * 0.4)), '400')
        time.sleep(2)
    return None


def fail(message):
    shot('FAILED')
    listing = '\n'.join('%r enabled=%s at %d,%d' % n[:4] for n in nodes())
    with open(os.path.join(OUT, 'screen-at-failure.txt'), 'w') as f:
        f.write(listing)
    print('Text on screen at failure (screen is %dx%d):\n%s' % (W, H, listing), flush=True)
    print('FAILED:', message, flush=True)
    sys.exit(1)


def tap(pattern, **kw):
    hit = find(pattern, **kw)
    if not hit:
        fail('could not find %r on screen' % pattern)
    text, enabled, x, y = hit
    if not enabled:
        fail('%r is on screen but disabled' % text)
    print('tap %r at %d,%d' % (text, x, y), flush=True)
    adb('shell', 'input', 'tap', str(x), str(y))


adb('shell', 'rm', '-f', '/sdcard/Download/*.csv', check=False)
adb('shell', 'am', 'start', '-W', '-n', APP + '/.MainActivity')

# 1. Log a short session so there is something to export.
tap(r'Start session', timeout=120)
time.sleep(6)
shot('session-running')
tap(r'End and log', scroll=True)
time.sleep(2)

# 2. Export.
tap(r'Export CSV', scroll=True)
time.sleep(4)
shot('save-as-screen')

# 3. Android's "save as" screen: press its Save button.
tap(r'Save', timeout=60)
time.sleep(5)
shot('after-save')

# 4. The page should say it saved, and the file should exist in Downloads.
msg = find(r'Saved .*\.csv with 1 session\.', timeout=30, scroll=True)
if not msg:
    fail('the page did not report "Saved ... with 1 session."')
print('page says:', msg[0], flush=True)
shot('saved-message')

listing = adb('shell', 'ls', '/sdcard/Download/', check=False)
csvs = [l.strip() for l in listing.splitlines() if l.strip().endswith('.csv')]
if not csvs:
    fail('no .csv in Downloads; it holds: %r' % listing)
if not re.fullmatch(r'\d{6} - \d{6}\.csv', csvs[0]):
    fail('unexpected file name %r' % csvs[0])
content = adb('shell', 'cat', '/sdcard/Download/' + csvs[0].replace(' ', '\\ '))
with open(os.path.join(OUT, csvs[0]), 'w') as f:
    f.write(content)
lines = [l for l in content.splitlines() if l.strip()]
print('saved file:', csvs[0])
print(content)
if len(lines) != 2 or not lines[0].startswith('Date,Start,End'):
    fail('the CSV should be a header plus one session, got %d lines' % len(lines))
print('PASSED: Export CSV saved %s through the save-as screen.' % csvs[0])
