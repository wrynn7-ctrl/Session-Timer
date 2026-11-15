#!/usr/bin/env python3
"""Drives the installed app on a running emulator to check Export CSV end to end.

Logs a short session, presses Export CSV, saves through Android's real "save as" screen, then
checks the CSV landed in Downloads. Screenshots of each step and the saved file go into the output
folder.

The app's own buttons are pressed through the WebView's debugging connection (debug builds only),
because Android's screen reader cannot read the page while the timer is ticking. The "save as"
screen belongs to Android, so there the script finds the Save button on screen and taps it.

Usage: python3 scripts/emulator-export-test.py <output-folder>
"""
import base64, json, os, re, socket, struct, subprocess, sys, time
import urllib.request
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


def page(expression):
    """Run a line of JavaScript in the app's page and return its value."""
    pid = adb('shell', 'pidof', APP).split()[0]
    adb('forward', 'tcp:9222', 'localabstract:webview_devtools_remote_' + pid)
    pages = json.load(urllib.request.urlopen('http://127.0.0.1:9222/json', timeout=20))
    path = '/' + pages[0]['webSocketDebuggerUrl'].split('/', 3)[3]
    sock = socket.create_connection(('127.0.0.1', 9222), timeout=30)
    try:
        key = base64.b64encode(os.urandom(16)).decode()
        sock.sendall(('GET %s HTTP/1.1\r\nHost: 127.0.0.1:9222\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                      'Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (path, key)).encode())
        buf = b''
        while b'\r\n\r\n' not in buf:
            buf += sock.recv(4096)
        if b' 101 ' not in buf.split(b'\r\n')[0]:
            raise RuntimeError('debugging connection refused: %r' % buf[:200])
        buf = buf.split(b'\r\n\r\n', 1)[1]
        body = json.dumps({'id': 1, 'method': 'Runtime.evaluate',
                           'params': {'expression': expression, 'returnByValue': True}}).encode()
        mask = os.urandom(4)
        head = bytes([0x81, 0x80 | len(body)]) if len(body) < 126 else bytes([0x81, 0xFE]) + struct.pack('>H', len(body))
        sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(body)))

        def need(n):
            nonlocal buf
            while len(buf) < n:
                chunk = sock.recv(65536)
                if not chunk:
                    raise RuntimeError('debugging connection closed')
                buf += chunk
            out, buf = buf[:n], buf[n:]
            return out

        while True:
            b0, b1 = need(2)
            size = b1 & 0x7F
            if size == 126:
                size = struct.unpack('>H', need(2))[0]
            elif size == 127:
                size = struct.unpack('>Q', need(8))[0]
            payload = need(size)
            if b0 & 0x0F != 1:
                continue
            msg = json.loads(payload)
            if msg.get('id') == 1:
                result = msg.get('result', {})
                if 'exceptionDetails' in result:
                    raise RuntimeError('page error: %s' % json.dumps(result['exceptionDetails'])[:300])
                return result.get('result', {}).get('value')
    finally:
        sock.close()


def press(button_id, expect):
    """Press one of the app's buttons, after checking it shows the expected label."""
    label = None
    for _ in range(30):
        try:
            label = page("(function(){var b=document.getElementById('%s');"
                         "return b&&!b.hidden&&!b.disabled?b.textContent.trim():null})()" % button_id)
        except Exception as e:
            label = 'not ready: %s' % e
        if label == expect:
            break
        time.sleep(2)
    else:
        fail('expected a %r button (#%s), found %r' % (expect, button_id, label))
    page("(function(){var b=document.getElementById('%s');b.scrollIntoView({block:'center'});b.click()})()" % button_id)
    print('pressed %r' % expect, flush=True)


adb('shell', 'rm', '-f', '/sdcard/Download/*.csv', check=False)
adb('shell', 'am', 'start', '-W', '-n', APP + '/.MainActivity')

# 1. Log a short session so there is something to export.
press('btnMain', 'Start session')
time.sleep(6)
shot('session-running')
press('btnEnd', 'End and log')
time.sleep(2)

# 2. Export.
press('btnExport', 'Export CSV')
time.sleep(4)
shot('save-as-screen')

# 3. Android's "save as" screen: find its Save button on screen and tap it.
tap(r'Save', timeout=60)
time.sleep(5)

# 4. The page should say it saved, and the file should exist in Downloads.
said = None
for _ in range(15):
    said = page("document.getElementById('exportMsg').textContent")
    if said:
        break
    time.sleep(2)
page("document.getElementById('exportMsg').scrollIntoView({block:'center'})")
time.sleep(1)
shot('after-save')
print('page says: %r' % said, flush=True)
if not re.fullmatch(r'Saved .*\.csv with 1 session\.', said or ''):
    fail('the page should say "Saved ... with 1 session."')

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
