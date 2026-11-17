# scripts/emulator-export-test.py

`scripts/emulator-export-test.py`

A Python script that drives the installed app on a running emulator and checks Export CSV from
start to finish. The workflow in
[emulator-export-test-workflow.md](emulator-export-test-workflow.md) runs it on GitHub. It also
works against any emulator or phone that `adb` can see:

```
python3 scripts/emulator-export-test.py emulator-out
```

It needs a **debug** build of the app, because it uses the web view's debugging connection.

## Two ways of pressing buttons, and why

The script controls the app in two different ways.

- **The app's own buttons** are pressed by running JavaScript in the page through the web view's
  debugging connection. The obvious method, reading the screen and tapping, does not work while
  the timer runs: Android's screen-reading tool waits for the screen to go still, and a ticking
  timer never does.
- **Android's "save as" screen** is not part of the page, so the script reads what is on screen,
  finds the Save button and taps it like a finger would. This is the part the test is really
  about.

## Setup (top of the file)

```python
OUT = sys.argv[1] if len(sys.argv) > 1 else 'emulator-out'
APP = 'com.sessiondial.app'
os.makedirs(OUT, exist_ok=True)
```

The output folder (from the command line) and the app's ID.

## Helpers for talking to the device

**`adb(*args)`** runs one `adb` command and returns what it printed. It raises an error if the
command fails, unless called with `check=False`.

**`shot(label)`** takes a screenshot and saves it as a numbered file such as
`02-save-as-screen.png`, so the pictures sort in the order they were taken.

**`nodes()`** asks Android to describe the current screen (`uiautomator dump`) and returns every
piece of visible text with whether it is enabled and where its centre is. The description comes
back as XML; the function picks out the `text` and `bounds` of each element.

**`screen_size()`** reads the screen's width and height, used for scrolling and for ignoring
things too close to the edges.

**`find(pattern, timeout, scroll)`** waits until text matching the pattern is on screen and
returns its position. It ignores matches in the top and bottom 8% of the screen, where the status
and navigation bars are. With `scroll=True` it swipes up between attempts.

**`fail(message)`** takes a screenshot, writes a list of everything on screen to
`screen-at-failure.txt`, prints the same list, and exits with an error so the GitHub run is
marked failed.

**`tap(pattern)`** finds text on screen and taps its centre. It fails if the text is missing or
the button is disabled.

## Helpers for talking to the page

**`page(expression)`** runs one line of JavaScript inside the app's page and returns the result.
Step by step:

1. `adb shell pidof` finds the app's process number.
2. `adb forward` connects port 9222 on the computer to that process's debugging socket.
3. A request to `http://127.0.0.1:9222/json` lists the pages open in the web view.
4. It opens a WebSocket to the page and sends a `Runtime.evaluate` message containing the
   JavaScript. This is the same protocol Chrome's developer tools use.
5. It reads replies until the one answering its message arrives, and returns the value.

The WebSocket handling is written out by hand (the handshake, then packing and unpacking
messages) so the script needs nothing beyond standard Python.

**`press(button_id, expect)`** presses one of the app's buttons. First it waits, for up to a
minute, until the button exists, is visible, and shows the expected label. That check doubles as
"wait for the page to load" and catches the app being in an unexpected state. Then it scrolls the
button into view and clicks it.

## The test itself (bottom of the file)

```python
adb('shell', 'rm', '-f', '/sdcard/Download/*.csv', check=False)
adb('shell', 'am', 'start', '-W', '-n', APP + '/.MainActivity')
```

Removes any CSV left in Downloads by an earlier run, then starts the app.

**1. Log a short session**

```python
press('btnMain', 'Start session')
time.sleep(6)
shot('session-running')
press('btnEnd', 'End and log')
```

Export needs at least one logged session, and the app only logs sessions of a second or more.

**2. Export**

```python
press('btnExport', 'Export CSV')
time.sleep(4)
shot('save-as-screen')
```

After this, Android's "save as" screen should be showing. The screenshot records it.

**3. Save**

```python
tap(r'Save', timeout=60)
```

Finds the picker's Save button on screen and taps it. Matching ignores capitals, since the
button reads "SAVE".

**4. Check the result**

```python
said = page("document.getElementById('exportMsg').textContent")
...
if not re.fullmatch(r'Saved .*\.csv with 1 session\.', said or ''):
    fail(...)
```

The page must report "Saved *name*.csv with 1 session."

```python
listing = adb('shell', 'ls', '/sdcard/Download/', check=False)
csvs = [l.strip() for l in listing.splitlines() if l.strip().endswith('.csv')]
```

Then it checks three things about the file itself:

- A `.csv` exists in the emulator's Downloads folder.
- Its name has the form `mmddyy - mmddyy.csv`.
- Its contents are exactly two lines: the header starting `Date,Start,End` and one session.

The file is also copied into the output folder. If everything holds, the script prints `PASSED`.

## What it does not check

- Choosing a different folder or renaming the file in the picker. It saves to wherever the
  picker opens.
- The chimes. Those need a real phone with the screen off.
