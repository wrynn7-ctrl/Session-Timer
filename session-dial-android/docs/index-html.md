# www/index.html

`www/index.html`

The whole timer in one file of about 1,100 lines. It has three parts:

| Part | Lines (about) | What it holds |
|---|---|---|
| Styling | 7 to 288 | Colours, fonts and layout, inside `<style>`. |
| Structure | 290 to 393 | The dial, buttons, switches and lists, as HTML. |
| Logic | 396 to 1117 | Everything that happens, inside `<script>`. |

The same file runs in an ordinary browser and inside the Android app. Wherever the two differ,
the code checks which one it is in and takes the matching path.

---

## Part 1: Styling

### Fonts (line 8)

Four `@font-face` rules load Instrument Serif (the large digits and the title) and Instrument
Sans (everything else) from the `fonts/` folder, so the app looks the same with no connection.

### Colours (line 23)

```css
:root {
  --bg: #ECE9F0;      --surface: #F6F4F8;   --ink: #2B1A30;
  --track: #DCD5E1;   --accent: #B5562A;    --wind: #E6C3AD;   --over: #93305F;
  ...
}
```

Every colour is a named variable, used everywhere else as `var(--accent)` and so on.

| Variable | Used for |
|---|---|
| `--bg`, `--surface` | Page background and input backgrounds. |
| `--ink`, `--muted` | Main text and quieter text. |
| `--line`, `--track` | Borders and the empty dial ring. |
| `--accent`, `--accent-ink` | Copper: the progress arc and highlighted text. |
| `--wind` | The pale wind-down zone on the ring. |
| `--over` | Plum: over-time, and buttons waiting for a second tap. |

The same names are defined again with dark values inside
`@media (prefers-color-scheme: dark)`, so the page follows the phone's dark mode with no other
code.

### Base layout (line 72)

- `body` sets the font, background and padding. `env(safe-area-inset-...)` keeps content clear of
  notches and rounded corners.
- `.sr-only` hides an element visually but leaves it readable by screen readers.
- `.stage` is the main layout. On a phone the dial sits above the settings. From 880 pixels wide
  it becomes two columns: dial on the left, settings in a 320-pixel rail on the right.

### The dial (search for `---------- dial`)

- `.dial` is a square that fills the available width, up to 520 pixels.
  `container-type: inline-size` lets the text inside size itself relative to the dial (the `cqi`
  units below).
- `.track`, `.windzone`, `.prog`, `.overring` give the four rings their colours. `.prog` and
  `.overring` have a quarter-second transition, so the arc glides between updates.
- `.tip` and `.halo` are the dot at the end of the arc and the glow behind it. While running, the
  glow pulses through the `halo` animation.
- `.tick` and `.scale-label` style the minute marks and numbers round the outside.
- `.readout`, `.phase`, `.digits`, `.sub` style the text in the middle: the status word, the big
  time, and the line beneath. `font-size: 26cqi` makes the digits 26% of the dial's width.
- Rules such as `.dial[data-zone="wind"] .digits` recolour the digits by phase. The script only
  sets `data-status` and `data-zone` on the dial; the CSS does the rest.

### Controls (search for `---------- controls`)

`.btn` is the pill-shaped button. `.primary` is the large filled one, `.ghost` the borderless
one. `.btn[data-armed]` turns a button plum while it waits for a confirming second tap.

### CPT strip (search for `---------- CPT strip`)

Three boxes under the dial for the billing-code time bands. `.reached` and `.current` mark the
bands passed and the band the session is in now.

### The rail (search for `---------- rail`)

Styles for the settings column: `.chip` (the length and wind-down choices, filled when
selected), `.switch` and `.knob` (the sliding switches, built from a hidden checkbox), `.log-list`
(today's sessions as a four-column grid), and `.range` (the two export date boxes).

### Reduced motion (near line 283)

If the phone is set to reduce motion, the transitions are switched off and the halo stops
pulsing.

---

## Part 2: Structure

Every element the script needs has an `id`. The script looks them up once at the start.

### Header (line 291)

The title, and today's date and time (`nowDate`, `nowTime`).

### The dial (line 298)

```html
<div class="dial" id="dial" data-status="idle" data-zone="main">
  <svg viewBox="0 0 400 400">
    <g transform="rotate(-90 200 200)" fill="none">
      <circle class="track" .../>
      <circle class="windzone" id="windzone" .../>
      <circle class="prog" id="prog" .../>
      <circle class="overring" id="overring" r="132" .../>
    </g>
    <g id="scale"></g>
    <circle class="halo" id="halo" .../>
    <circle class="tip" id="tip" .../>
  </svg>
```

The drawing is an SVG 400 units square with the ring centred at (200, 200).

- Four circles are stacked: the grey track, the wind-down zone, the progress arc, and a thinner
  inner ring for over-time.
- `rotate(-90 ...)` turns them a quarter turn. A circle's outline normally starts at 3 o'clock;
  this makes it start at 12.
- `<g id="scale">` is empty. The script fills it with tick marks and numbers.

```html
  <div class="readout" id="readout" role="timer">
    <div class="phase" id="phase">Ready</div>
    <div class="digits" id="digits"></div>
    <div class="sub" id="sub"></div>
  </div>
```

The text laid over the middle. `role="timer"` tells screen readers what it is.

### Main buttons (line 318)

`btnMain` (Start, Pause or Resume), `btnEnd` (End and log) and `btnReset` (Discard). The last
two are `hidden` until a session starts.

### CPT strip (line 324)

A list of the three bands. Each `<li>` carries `data-min`, its starting minute.

### `live` (line 334)

An invisible element. When the phase changes, the script writes the new phase here, and screen
readers announce it.

### The settings rail (line 337)

Four groups:

1. **Session length**: an empty `lenChips` box, which the script fills with preset buttons, and
   the "Other" number box (`customMin`).
2. **Wind-down**: the `cueChips` box, then the three switches (`optChime`, `optCpt`, `optAwake`).
   `chimeNotice` is a hidden warning line with the "Allow exact timing" button (`btnExact`).
3. **Sessions**: the total (`logSum`), two chips that choose what the list shows (`viewToday`
   and `viewRange`), a pair of date boxes that appear for "Date range" (`viewFrom`, `viewTo`
   inside `viewDates`), the list (`logList`), "Copy list" and "Clear today", and a hidden text
   box (`copyFallback`) used if copying to the clipboard is blocked.
4. **Export**: the two date boxes (`expFrom`, `expTo`), "Export CSV" (`btnExport`), "Delete all"
   (`btnWipe`), a message line (`exportMsg`) and another fallback text box (`csvFallback`).

### Scripts (line 394)

`<script src="capacitor.js">` loads Capacitor's library, then the page's own script follows.

---

## Part 3: Logic

All of it sits inside `(() => { ... })();`, a function that runs at once. This keeps its names
private to the page.

### Storage (line 397)

```js
const LS_STATE = 'session-dial:state:v1';
const LS_LOG = 'session-dial:log:v1';
const store = { get(k) {...}, set(k, v) {...} };
```

Two things are saved on the device, each under its own key: the current timer state and the
session log. `store` wraps the browser's `localStorage`. Both methods swallow errors, so the
timer keeps working even if storage is full or blocked.

### Finding the Android plugins (line 406)

```js
const cap = window.Capacitor;
const isNative = !!(cap && typeof cap.isNativePlatform === 'function' && cap.isNativePlatform());
const nativePlugin = name => (isNative && window.capacitorExports ? window.capacitorExports.registerPlugin(name) : null);
const Notif = nativePlugin('LocalNotifications');
const Files = nativePlugin('Filesystem');
const Sharing = nativePlugin('Share');
const Saver = nativePlugin('SaveFile');
const Awake = nativePlugin('KeepAwake');
const Widget = nativePlugin('WidgetBridge');
```

`isNative` is true only inside the Android app. Each plugin variable is either a working object
(in the app) or `null` (in a browser). The rest of the code asks `if (Notif)`, `if (Saver)` and
so on to choose its path. This is the whole mechanism by which one file serves both.

### Constants (line 416)

| Name | Value | Meaning |
|---|---|---|
| `NOTE` | 101, 102 | ID numbers for the two chime notifications, so they can be cancelled later. |
| `CHANNEL` | `wind-down-v1`, `session-end-v1` | Names of the two notification channels. |
| `PRESETS` | 30, 45, 50, 53, 60, 90 | The session-length buttons. |
| `CUES` | 0, 5, 10, 15 | The wind-down choices; 0 is "Off". |
| `CPT` | 16 → 90832, 38 → 90834, 53 → 90837 | The minute at which each billing code begins. |
| `DEFAULTS` | | The state of a brand-new install: idle, 53 minutes, 10-minute wind-down, chime off, CPT shown, keep-awake on. |
| `CX`, `CY`, `R`, `R2` | 200, 200, 150, 132 | The dial's centre and the two ring sizes. |
| `CIRC`, `CIRC2` | | The length of each ring's outline, used to draw arcs. |

### Element lookups (line 427)

A block of `const dial = $('dial')` lines. `$` is short for `document.getElementById`.

### Working variables (line 439)

- `state` is the current timer state, and `log` is the list of finished sessions.
- `exportMode` is `'save'` normally and `'copy'` once saving has failed.
- `rangeTouched` remembers whether the user changed an export date by hand, so the code stops
  overwriting it.
- `logView` is `'today'` or `'range'`: which sessions the list shows. `viewTouched` does for the
  list's two date boxes what `rangeTouched` does for export's.
- `lastDigits`, `lastPhase`, `lastMinute`, `scaleKey` remember what was last drawn, so the page
  is only touched when something changed.

### Formatting helpers (search for `---------- formatting`)

| Function | Turns | Into |
|---|---|---|
| `pad` | 7 | `07` |
| `fmtMS` | seconds | `53:00` |
| `fmtClock` | a timestamp | `2:15 PM` |
| `fmtTotal` | milliseconds | `1 h 46 min` |
| `isToday` | a timestamp | true or false |
| `cptFor` | a length | the highest code whose minute has been reached, or nothing under 16 minutes |
| `dayKey` | a timestamp | `2026-11-15`, used to compare days |
| `mmddyy` | a day key | `111526`, for the file name |
| `csvDate`, `csvTime`, `csvLen` | a timestamp or length | `11/15/2026`, `4:26 AM`, `0:53:00` |

The CSV ones are built by hand instead of using the phone's language settings, so the file is the
same on every device.

### Timing (search for `---------- timing`)

```js
const elapsedMs = (now = Date.now()) =>
  state.accumulated + (state.status === 'running' ? Math.max(0, now - state.runStart) : 0);
```

**The most important line in the file.** The timer does not count ticks. It stores when the
current stretch began (`runStart`) and how much time was banked before the last pause
(`accumulated`), and works the elapsed time out from the clock whenever it is needed. That is why
the timer is still right after the phone sleeps or Android closes the app.

- `cueEff()` returns the wind-down minutes, or 0 if it is off or not shorter than the session.
- `save()` writes `state` to storage.

### Browser chime (search for `---------- chime (scheduled`)

Used only outside the Android app.

- **`ensureAudio()`** creates the browser's sound engine, or wakes it if the browser suspended
  it.
- **`bell(at, freq, vol)`** plays one bell at a future moment. It is two pure tones, the note and
  a quieter overtone, fading out over about three seconds.
- **`clearChimes()`** silences and forgets any bells already queued.
- **`scheduleChimes()`** is the entry point for both worlds. In the app it hands over to
  `scheduleNative`. In a browser it queues one bell for the wind-down point and two, 0.7 seconds
  apart, for the end.

`nativeQueue = nativeQueue.then(scheduleNative, scheduleNative)` chains the Android calls so that
each finishes before the next begins. Quick taps cannot then leave stale notifications behind.

### Android chime (search for `chime inside the Android app`)

- **`showChimeMsg(text, offerExact)`** shows or hides the warning line under the chime switch,
  with or without the "Allow exact timing" button.
- **`ensureChannels()`** creates the two notification channels once. A channel is Android's
  grouping for notifications. Each has its own sound file from `res/raw`, high importance (4) so
  it makes a sound, and vibration.
- **`scheduleNative()`** does the scheduling:
  1. Cancels both chime notifications if they exist.
  2. Stops there if the chime is off or the timer is not running.
  3. Works out how long until the wind-down point and until the end.
  4. For each one more than a second away, builds a notification with a title, a body and
     `schedule: { at: ... }`. `allowWhileIdle: true` lets it fire even when the phone is in deep
     sleep.
  5. Hands them to Android. If Android refuses, it shows a message.
- **`checkNativeChime(ask)`** checks the two permissions and shows a warning if either is
  missing. With `ask` true it requests notification permission, which is what brings up Android's
  prompt the first time the switch is turned on.

Because Android holds the schedule, the chimes fire with the screen off or the app closed.

### Keeping the screen on (search for `---------- screen wake lock`)

- **`holdWake()`** keeps the screen from dimming while a session runs, if the switch is on. In
  the app it uses the KeepAwake plugin; in a browser, the browser's own wake lock.
- **`dropWake()`** releases it, on pause, end or switch-off.

### Drawing the scale (search for `---------- dial scale`)

- **`polar(frac, r)`** converts "this fraction of the way round, at this distance from the
  centre" into x and y. 0 is the top; fractions go clockwise.
- **`addTick`** and **`addLabel`** add one line or one number to the `scale` group.
- **`buildScale()`** redraws the marks when the length, wind-down or CPT setting changes. It
  first checks a key made of those three values and does nothing if they are unchanged. Then it:
  1. Sizes the wind-down zone to its share of the ring and places it at the end.
  2. Chooses spacing by session length: a tick every 5 minutes up to two hours, and numbers
     every 10 minutes up to an hour, with wider spacing for longer sessions.
  3. Adds the ticks and numbers, skipping any that would crowd the top or a CPT mark.
  4. Adds heavier copper marks at the CPT minutes (16, 38, 53) that fall inside the session.
  5. Marks the top with the total length.

### Drawing the current moment (search for `---------- render`)

**`setDigits(text)`** rebuilds the big time, one fixed-width box per character, so the digits do
not shift sideways as they change.

**`render()`** runs four times a second and brings the whole screen up to date:

1. **Work out where things stand.** Elapsed seconds, seconds left, seconds over, and the zone:
   `main`, `wind` (inside the wind-down period) or `over` (past the planned length).
2. **Set `data-status` and `data-zone`** on the dial; the CSS recolours accordingly.
3. **Phase word**: Ready, Paused, In session, Wind-down or Over time. A change is also written to
   the `live` element for screen readers.
4. **Digits** and, once a minute, the spoken label ("12 minutes elapsed of 53").
5. **The line beneath**: before starting, when a session started now would end; while running,
   time left and end time; when over, how far past.
6. **The progress arc.**

   ```js
   prog.style.strokeDasharray = CIRC + ' ' + CIRC;
   prog.style.strokeDashoffset = CIRC * (1 - frac);
   ```

   The circle's outline is drawn as one dash as long as the whole ring, followed by an equally
   long gap. Sliding that dash along by `strokeDashoffset` uncovers just the fraction that has
   elapsed. The over-time ring is done the same way.
7. **The tip dot and halo** are moved to the end of the arc and hidden once over time.
8. **CPT strip**: marks the bands passed and the current one, and shows how long until the next
   code.
9. **Date and time** in the header. When the date changes at midnight, it also refreshes the log
   so "Today" is correct.

**`syncControls()`** makes the buttons and switches match `state`: which chips are selected, the
main button's label, whether End and Discard are visible. It ends by calling `buildScale()`.

### Actions (search for `---------- actions`)

```js
function commit() { save(); syncControls(); scheduleChimes(); pushWidget(); render(); }
```

Called after every change: save, update the controls, reschedule the chimes, tell the widget,
redraw. Because
everything goes through it, the chimes are always scheduled from the current settings.

`commit()` also calls `pushWidget()`, which sends the new state to the home screen widget. That
and `widgetAction()`, which carries out a tap on the widget's button, are explained in
[widget.md](widget.md).

- **`toggleMain()`** is Start, Pause and Resume in one. Pausing banks the elapsed time and clears
  `runStart`. Starting or resuming records a new `runStart`; a fresh start also records
  `startedAt` for the log.
- **`resetTimer()`** returns to idle, clears delivered chime notifications, and is what Discard
  calls.
- **`endSession()`** adds the session to the log if it lasted at least a second, then resets. The
  entry holds the start time, end time, length in milliseconds and planned minutes.
- **`setTarget(min)`** changes the session length, held between 1 and 600 minutes.
- **`twoTap(btn, prompt, fn)`** and **`disarm(btn)`** give destructive buttons a confirmation.
  The first tap changes the label ("Tap again to discard") for 3.5 seconds; a second tap in that
  time runs the action. It exists because the web view shows no confirmation pop-ups.

### The log (search for `---------- log`)

- **`saveLog()`** keeps at most the newest 5,000 sessions, stores them and redraws.
- **`orderedRange(a, b)`** reads two date boxes and swaps the dates if they are the wrong way
  round. The session list and export both use it.
- **`shownSessions()`** returns the sessions the list is showing. In "Today" view that is
  today's. In "Date range" view it is every session from the first chosen day to the last,
  oldest first.
- **`sessionCount(n)`** writes "1 session" or "3 sessions". **`dayTitle(ts)`** writes a short
  date such as "Sun, Nov 15", adding the year when it is not the current one.
- **`setLogView(view)`** runs when a chip is tapped. It records the choice, marks the chip,
  shows or hides the date boxes and redraws the list.
- **`renderLog()`** has three parts:
  - *Default dates.* Until the user picks dates, the range is the last seven days, ending today.
  - *The list.* One row per session with start and end times, length, CPT code and a remove
    button. In "Date range" view each day starts with a heading giving the date, the number of
    sessions and the total time for that day. The line above the list gives the count and total
    for everything shown. "Clear today" is hidden in "Date range" view, since it only clears
    today.
  - *Export summary.* "N sessions since *date*", and default dates for the export boxes (first
    logged day to today) unless the user has set them by hand.
- **`logText()`** builds the listed sessions as plain text. For a date range it writes a
  heading for each day with a blank line between days.
- **`copyLog()`** puts that text on the clipboard. If the clipboard is blocked, it shows the text
  in a box to copy by hand.

The view choice is not saved. The list goes back to "Today" each time the app starts.

### CSV export (search for `---------- CSV export`)

- **`setExportMsg(text)`** shows or hides the message line under the button.
- **`exportRange()`** reads the two export dates through `orderedRange()`.
- **`buildCsv(rows)`** turns sessions into CSV text: a header row, then one row per session with
  date, start, end, length, whole minutes, planned minutes and, if CPT is shown, the code. Any
  value containing a comma, quote or line break is wrapped in quotes.
- **`useCopyMode()`** and **`copyCsv()`** are the last resort: the button becomes "Copy as CSV"
  and the text goes to the clipboard, or into a box.
- **`exportCsv()`** runs when Export CSV is pressed:
  1. Collects the sessions in the date range, oldest first. With none, it says so and stops.
  2. Builds the file name, `mmddyy - mmddyy.csv`, and the text.
  3. **In the app**, calls `Saver.save(...)`, which opens Android's "save as" screen (see
     [SaveFilePlugin.md](SaveFilePlugin.md)). Then it shows "Saved *name* with N sessions." or
     "Export cancelled."
  4. If the phone has no file picker (error code `UNAVAILABLE`), it falls back to writing the
     file into the app's cache and opening the share sheet. Any other failure switches to copy
     mode.
  5. **In a browser**, it triggers an ordinary download.

### Wiring (search for `---------- wiring`)

**`bind()`** connects each control to its function. It runs once at startup.

- The three main buttons, the log buttons and the export buttons call the functions above.
  Discard, Clear today and Delete all go through `twoTap`.
- The length and wind-down chips share one click handler per group, which reads the value from
  the chip that was tapped.
- **Today and Date range chips** call `setLogView`. Changing either of the list's date boxes
  redraws the list.
- **Chime switch**: plays a sample bell in a browser. In the app it checks permissions first,
  asking if needed, and then commits.
- **Allow exact timing**: opens Android's settings page for exact alarms, then re-checks.
- **Keep-awake and CPT switches**: update `state` and apply at once.
- **Space bar** starts and pauses, unless the cursor is in a button or text box.
- **Returning to the app** (`visibilitychange`): redraws immediately, re-takes the wake lock,
  reschedules the chimes and re-checks permissions.
- **First touch** after a reload: browsers only allow sound after a touch, so this reschedules
  the bells in a browser if a session is already running.

**`buildChips()`** creates the preset and wind-down buttons from `PRESETS` and `CUES`.

### Startup (search for `function start`)

**`start()`** runs once, as the last line of the script:

1. **Load the saved state** on top of the defaults, so settings added in later versions get
   sensible values.
2. **Tidy it.** Each value is checked and corrected: length within 1 to 600, wind-down one of the
   four choices, status one of the three. Storage could hold anything, so nothing is trusted.
3. **Stale sessions.** A session that has apparently run for over 12 hours is reset. The comment
   in the code reads: "a session left running overnight is stale, not a 14-hour appointment".
4. **Load the log**, dropping malformed entries.
5. **Build and draw**: chips, wiring, controls, log, dial.
6. **In the app**, put the chimes back on Android's schedule, in case Android restarted the app
   during a session. Also send the state to the widget and ask whether a widget tap opened the
   app.
7. **Start the clock**: `setInterval(render, 250)` redraws four times a second from then on.
