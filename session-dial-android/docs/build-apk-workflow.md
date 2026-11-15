# build-apk.yml

`.github/workflows/build-apk.yml` (at the top of the repository, outside `session-dial-android`)

A GitHub Actions workflow: a list of steps GitHub runs on its own servers. This one builds the
debug APK, so a fresh one is available without Android Studio.

## When it runs

```yaml
on:
  push:
    paths:
      - 'session-dial-android/**'
      - '.github/workflows/build-apk.yml'
  workflow_dispatch:
```

- `push` with `paths`: on any push that changes the project folder or this file. A push that only
  touches something else does not start a build.
- `workflow_dispatch`: adds a **Run workflow** button on the Actions tab for starting it by hand.

## Where it runs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: session-dial-android
```

`ubuntu-latest` is a fresh Linux machine that GitHub provides for each run and throws away
afterwards. It already has the Android SDK. `working-directory` makes every command below start
inside the project folder.

## The steps

```yaml
- uses: actions/checkout@v5
```

Downloads the repository onto the machine.

```yaml
- uses: actions/setup-node@v5
  with:
    node-version: 22
    cache: npm
    cache-dependency-path: session-dial-android/package-lock.json
```

Installs Node 22, which Capacitor 8 requires. `cache: npm` keeps downloaded libraries between
runs so later builds are faster.

```yaml
- uses: actions/setup-java@v5
  with:
    distribution: temurin
    java-version: 21
    cache: gradle
```

Installs Java 21, which the Android build needs, and keeps Gradle's downloads between runs.

```yaml
- name: Install dependencies
  run: npm ci
```

Installs exactly the library versions recorded in `package-lock.json`. `npm ci` is the stricter
form of `npm install` meant for automated builds. It also triggers `scripts/copy-libs.js`.

```yaml
- name: Sync web page into the Android project
  run: npx cap sync android
```

Copies `www` into the Android project and registers the plugins.

```yaml
- name: Build debug APK
  working-directory: session-dial-android/android
  run: ./gradlew assembleDebug --no-daemon
```

The build itself. `--no-daemon` stops Gradle leaving a background process running, which is
pointless on a machine that is about to be deleted.

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: session-dial-debug-apk
    path: session-dial-android/android/app/build/outputs/apk/debug/app-debug.apk
    if-no-files-found: error
```

Attaches the APK to the run. It appears under **Artifacts** on the run's page as a zip named
`session-dial-debug-apk` and is kept for 90 days. `if-no-files-found: error` makes the run fail
if no APK was produced, instead of reporting success with nothing attached.

## About the APK it produces

It is a **debug** build, signed with a throwaway key made on that machine. It installs fine by
hand, but each run's key is different, so installing a new one over an old one can fail with a
signature mismatch. If that happens, uninstall the old app first (this clears the session log) or
set up a fixed signing key.
