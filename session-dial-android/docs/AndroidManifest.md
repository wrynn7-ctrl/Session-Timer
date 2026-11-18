# AndroidManifest.xml

`android/app/src/main/AndroidManifest.xml`

Every Android app has a manifest. Android reads it at install time to learn what the app
contains and what it is allowed to do. Most of this one is the Capacitor template; the
permissions at the bottom are specific to Session Dial.

## The application block

```xml
<application
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:supportsRtl="true"
    android:theme="@style/AppTheme">
```

- `icon` and `roundIcon` point at the launcher icon (see [icon.md](icon.md)).
- `label` is the name under the icon. `@string/app_name` means "look it up in `strings.xml`",
  where it is "Session Dial".
- `allowBackup` lets Android include the app's data, which holds the session log, in the phone's
  own backup.
- `theme` is the template's colour theme, shown for a moment before the page loads.

## The one screen

```xml
<activity
    android:name=".MainActivity"
    android:launchMode="singleTask"
    android:exported="true"
    android:configChanges="orientation|keyboardHidden|...">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
```

- `name=".MainActivity"` is the class in [MainActivity.md](MainActivity.md).
- The `intent-filter` with `MAIN` and `LAUNCHER` is what puts the app in the launcher and makes
  this screen the one that opens.
- `launchMode="singleTask"` keeps a single copy of the screen. Tapping a chime notification
  returns to the running timer instead of opening a second one.
- `configChanges` lists events (rotation, keyboard, dark mode and others) that the app handles
  itself. Without it Android would destroy and rebuild the screen on each one, reloading the
  page.
- `exported="true"` is required for any screen the launcher can open.

## The home screen widget

A `<receiver>` block for `.SessionWidgetProvider` announces the widget to Android. It is
explained in [widget.md](widget.md).

## The file provider

```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
```

Lets the app hand a file to another app for a moment. Only the export fallback uses it: when a
phone has no file picker, the CSV is written to the app's cache and passed to the share sheet.
The folders it may share from are listed in `res/xml/file_paths.xml`.

## Permissions

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

Network access. It comes with the Capacitor template. The page is stored inside the app and does
not fetch anything from the network itself.

```xml
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" android:maxSdkVersion="32" />
```

These make the chimes fire on the exact minute. Without them Android may delay a scheduled
notification by several minutes to save battery.

- `USE_EXACT_ALARM` is for Android 13 and newer. It is granted automatically and is intended for
  timer and alarm apps.
- `SCHEDULE_EXACT_ALARM` covers Android 12. `maxSdkVersion="32"` stops it being requested on
  newer versions, where the first one applies. On Android 12 the user can switch it off, which is
  why the page has an "Allow exact timing" button.

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

Permission to show notifications. The chime is a notification, so without this it is silent.
Android 13 and newer ask the user the first time the chime switch is turned on.

## Permissions added by the plugins

The built app also has `RECEIVE_BOOT_COMPLETED` and `WAKE_LOCK`. They are not in this file. The
notifications plugin brings its own manifest, and the build merges it in. It uses them to
restore scheduled notifications after the phone restarts.
