# Session Dial for Android: setup

This folder is a ready-to-build Capacitor project. It wraps the Session Dial timer page in an
Android app so that Android itself plays the wind-down and end chimes. That is what makes them
sound with the screen off or the app in the background.

## What you need on the computer

| Tool | Version | Why |
|---|---|---|
| Node.js | 22 or newer | Capacitor 8's tools refuse to run on anything older. |
| Android Studio | a current release | It supplies the Android SDK (level 36) and Java 21 that the build uses. |
| A phone with USB debugging on | Android 7 or newer | To install and test the app. |

If you have built a Capacitor app on this computer before, check the Node version first
(`node -v`). An older project may have been set up with Node 18 or 20.

## The quick way: hand it to Claude Code

Unzip the folder into your projects directory, open it in Claude Code, and paste this:

> Follow SETUP.md in this folder. Install the dependencies, sync the Android project, build a
> debug APK, and install it on my connected phone. Do not change `www/index.html` or the files in
> `android/app/src/main/res/raw`. If a step fails, show me the error before trying a fix.

## The steps, and why each one matters

1. **Install the dependencies**

   ```
   npm install
   ```

   The zip leaves out `node_modules` because it is large. This downloads Capacitor and the four
   plugins listed in `package.json`. It also copies Capacitor's browser library into
   `www/capacitor.js`, which the page loads to talk to Android.

2. **Sync the web page into the Android project**

   ```
   npx cap sync android
   ```

   Android does not read the `www` folder directly. This copies it into the Android project and
   registers the plugins. Run it again after any change to `www`.

3. **Build and install**

   With the phone plugged in:

   ```
   npx cap run android
   ```

   Or build the APK file and install it yourself:

   ```
   cd android
   ./gradlew assembleDebug        (Windows: gradlew.bat assembleDebug)
   ```

   The APK lands in `android/app/build/outputs/apk/debug/app-debug.apk`. The first build is slow
   because Gradle downloads its own tools.

## First run on the phone

1. Turn on **Chime at wind-down and at the end**. Android asks to allow notifications. Say yes;
   the chime is delivered as a notification, so without this it stays silent.
2. If a line appears saying the chime may be late, tap **Allow exact timing**. This should only
   happen on Android 12; newer versions grant it automatically.
3. Samsung and some other phones put background apps to sleep. If a chime ever arrives late or not
   at all, open Android settings, then Apps, Session Dial, Battery, and choose **Unrestricted**.

The chime follows the phone's notification volume and Do Not Disturb. If the phone is muted, the
notification vibrates but makes no sound.

## A six-minute test

1. Set **Other** to 6 minutes and wind-down to 5 minutes.
2. Turn the chime on and press **Start session**.
3. Lock the phone.
4. The single wind-down bell should sound after 1 minute, and the double end bell after 6.

## What is where

| Path | What it is |
|---|---|
| `www/index.html` | The whole timer. Search for "chime inside the Android app" to find the notification code. |
| `www/fonts/`, `www/capacitor.js` | Bundled fonts and Capacitor's library, so the app needs no connection. |
| `android/app/src/main/res/raw/` | `chime_wind.wav` and `chime_end.wav`, the two notification sounds. |
| `android/app/src/main/AndroidManifest.xml` | The alarm and notification permissions, with comments. |
| `capacitor.config.ts` | App name and app ID. |

## Things that behave differently from the web version

- **Export CSV** opens Android's share sheet, so the file can go to Drive, Files or email. The file
  name is the same: `mmddyy - mmddyy.csv`.
- **Keep the screen on while timing** is a new switch. It only stops the phone dimming by itself;
  you can still lock it by hand and the chimes will sound.
- The session log lives inside the app on this phone. It does not carry over from the web page.

## If you change something later

- **Changing a chime sound:** replace the `.wav` file, and also rename its channel in
  `www/index.html` (`wind-down-v1` to `wind-down-v2`, or `session-end-v1` to `session-end-v2`).
  Android remembers a channel's sound from the first time it is created and ignores later changes,
  so a new name is the only way to make it pick up the new file.
- **Changing the app ID** (`com.sessiondial.app`): do it before the first install, in both
  `capacitor.config.ts` and `android/app/build.gradle`. Changing it afterwards makes Android treat
  it as a separate app with an empty log.
- **App icon:** the project still has Capacitor's default icon. Android Studio's Image Asset tool
  (right-click `res`, New, Image Asset) replaces it.

## What has and has not been tested

Tested: the page's logic was run in Chrome against a stand-in for Android. Starting a 6-minute
session with a 5-minute wind-down scheduled the two notifications 60 and 360 seconds out, pausing
cancelled them, and export wrote the correctly named file and opened the share call. `npx cap sync`
completes with all four plugins found.

Not tested: the project has not been compiled into an APK or run on a phone, because the machine it
was prepared on has no Android SDK. Treat the first build and the six-minute test above as the real
check.
