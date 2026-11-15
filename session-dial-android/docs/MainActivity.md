# MainActivity.java

`android/app/src/main/java/com/sessiondial/app/MainActivity.java`

This is the first code Android runs when you tap the app's icon. It is short because Capacitor
does almost all of the work.

```java
package com.sessiondial.app;
```

The app's ID. It has to match `appId` in `capacitor.config.ts` and `applicationId` in
`android/app/build.gradle`.

```java
public class MainActivity extends BridgeActivity {
```

An "activity" is one screen of an Android app. `BridgeActivity` is Capacitor's ready-made screen:
it creates a full-screen web view, loads `index.html` into it, and sets up the bridge that lets
the page's JavaScript call native Android code. By extending it, this app gets all of that for
free.

```java
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(SaveFilePlugin.class);
        super.onCreate(savedInstanceState);
    }
```

`onCreate` runs once when the screen is created.

- `registerPlugin(SaveFilePlugin.class)` tells the bridge that a plugin named `SaveFile` exists
  (see [SaveFilePlugin.md](SaveFilePlugin.md)). Without this line the page's call to
  `Saver.save(...)` would fail with "plugin not implemented".
- It must come **before** `super.onCreate(...)`, because that call is what starts the bridge, and
  the bridge only picks up plugins registered before it starts.

The four plugins installed through npm (notifications, filesystem, share, keep-awake) are not
listed here. Capacitor finds those by itself from `capacitor.plugins.json`, which `npx cap sync`
writes. Only plugins written inside this app need registering by hand.
