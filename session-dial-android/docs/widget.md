# The home screen widget

Nine files make up the widget. This document covers them together, because each only makes sense
next to the others.

| File (under `android/app/src/main/`) | Role |
|---|---|
| `java/com/sessiondial/app/SessionWidgetProvider.java` | Draws the widget. |
| `java/com/sessiondial/app/WidgetBridgePlugin.java` | Carries messages between the page and the widget. |
| `res/layout/widget_session.xml` | The widget's layout. |
| `res/xml/session_widget_info.xml` | Its size and settings, for the launcher. |
| `res/values/widget.xml`, `res/values-night/widget.xml` | Its text and colours, light and dark. |
| `res/drawable/widget_background.xml`, `widget_button.xml` | The rounded shapes behind the widget and its button. |
| `AndroidManifest.xml` (the `<receiver>` block) | Announces the widget to Android. |

The page's side is in `www/index.html`; search for "home screen widget".

## The design in one paragraph

The widget does not run the timer. The page inside the app does. The page tells the widget what
to show after every change, and the widget's button opens the app with a note saying which button
was tapped. The page then starts or ends the session exactly as its own buttons would. The chimes
and the session log therefore have one owner, and the widget cannot disagree with the app.

The cost is that tapping the widget opens the app instead of acting silently in the background.

## SessionWidgetProvider.java: drawing the widget

A widget lives in the launcher, not in the app. The app cannot draw on it directly. It hands
Android a `RemoteViews` object, a description of what to show, and the launcher displays it.

**Constants**

- `PREFS` names a small settings file where the last state from the page is kept. The widget is
  sometimes redrawn while the page is not running, so the state has to be stored somewhere native
  code can read.
- `ACTION_START` and `ACTION_END` are the labels attached to a button tap.
- `EXTRA_TOKEN` is a number attached to each tap, used to ignore repeats.

**`onUpdate()`** is called by Android when a widget is added, after the phone restarts, and every
half hour. It redraws.

**`updateAll()`** redraws every copy of the widget on the home screen. The bridge calls it
whenever the page reports a change.

**`render()`** builds the picture:

1. Reads the stored status, start time, banked time and planned length.
2. Works out elapsed time with the same sum the page uses: banked time plus the current stretch.
3. Sets the status line: "Ready · 53 min", "In session · 53 min" or "Paused · 53 min".
4. Sets the clock. `setChronometer` uses Android's own ticking clock view. Given the moment the
   count began, it keeps itself up to date while running, so the app sends nothing in between and
   uses no battery for it. When paused or idle it shows a fixed time.
5. Sets the button to "Start session" when idle and "End and log" otherwise, and attaches the
   matching tap.
6. Makes a tap anywhere else on the widget simply open the app.

**`openApp()`** builds a `PendingIntent`: permission, handed to the launcher, to open
`MainActivity` on the app's behalf with a given action label and a fresh token.

## WidgetBridgePlugin.java: the messenger

A Capacitor plugin named `WidgetBridge`. The page reaches it as `Widget` in `index.html`.

**`update()`**: page to widget. Stores the four values the page sends and calls `updateAll()`.

**`takeAction()`**: widget to page, when the tap *started* the app. The page asks once as it
loads. The answer is `{ action: "start" }`, `{ action: "end" }` or nothing.

**`handleOnNewIntent()`**: widget to page, when the app was *already open*. Android delivers the
tap to the running app, and this sends the page a `widgetAction` event. The `true` argument keeps
the event until the page is listening.

**`consume()`** is shared by both paths. It turns an intent into "start", "end" or nothing, and
refuses a tap it has already handled. Android can deliver the same intent twice, for example when
the app is reopened from the recent apps list; without the token check that would start or end a
session a second time. It finishes by redrawing the widget so the buttons carry fresh tokens.

**`canPin()`** and **`requestPin()`** are for the app's "Add the home screen widget" button. The
first asks whether the launcher supports adding a widget on request (Android 8 and newer, and not
every launcher). The second opens the launcher's own confirmation prompt.

## The page's side (`www/index.html`)

```js
function commit() { save(); syncControls(); scheduleChimes(); pushWidget(); render(); }
```

`pushWidget()` was added to `commit()`, which runs after every change, so the widget is always
told.

- **`pushWidget()`** sends status, start time, banked time and planned length to
  `Widget.update`.
- **`widgetAction(action)`** does what the tap asked: "start" starts or resumes unless already
  running, and "end" ends and logs unless idle. The checks make a stale tap harmless.
- In **`start()`**, four lines send the first state, show the "Add" button if the launcher
  supports it, listen for `widgetAction` events, and ask `takeAction()` whether a tap opened the
  app.

## The layout and its resources

**`widget_session.xml`** is a row: on the left a column with the status line and the clock, on
the right the button. Widgets may only use a short list of basic views, so the button is a
`TextView` with a rounded background, not a real `Button`.

**`session_widget_info.xml`** tells the launcher:

| Setting | Meaning |
|---|---|
| `minWidth="250dp"`, `minHeight="50dp"` | About four cells wide and one tall. |
| `targetCellWidth="4"`, `targetCellHeight="1"` | The same, stated directly for Android 12 and newer. |
| `resizeMode="horizontal"`, `minResizeWidth="180dp"` | It can be made narrower or wider. |
| `updatePeriodMillis="1800000"` | Android redraws it every 30 minutes as a safety net. |
| `initialLayout`, `previewLayout` | What to show before any data arrives, and in the widget picker. |

**`values/widget.xml`** holds the widget's text and its light colours; `values-night/widget.xml`
holds the dark colours. Android picks the file to match the phone's theme. The colours are the
same ones `index.html` uses.

## The manifest entry

```xml
<receiver android:name=".SessionWidgetProvider" android:exported="true" android:label="@string/app_name">
    <intent-filter>
        <action android:name="android.appwidget.action.APPWIDGET_UPDATE" />
    </intent-filter>
    <meta-data android:name="android.appwidget.provider" android:resource="@xml/session_widget_info" />
</receiver>
```

This is what makes "Session Dial" appear in the launcher's widget list. The filter says the class
accepts widget update requests, and the `meta-data` points at the size-and-settings file.

## Limits

- Tapping the widget opens the app. It does not act in the background.
- The widget shows elapsed time counting up. It does not show the wind-down or over-time colours.
- After a session runs more than 12 hours the page treats it as stale and resets, but the widget
  only learns that the next time the app is opened.
