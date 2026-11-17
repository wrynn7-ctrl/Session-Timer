# emulator-export-test.yml

`.github/workflows/emulator-export-test.yml` (at the top of the repository)

A GitHub Actions workflow that checks Export CSV on a real Android emulator. It builds the app,
boots an emulated phone on GitHub's server, and runs `scripts/emulator-export-test.py` against it
(see [emulator-export-test.md](emulator-export-test.md)).

It runs on GitHub because an emulator needs hardware virtualisation to be usable, and GitHub's
servers have it.

## When it runs

```yaml
on:
  workflow_dispatch:
  push:
    paths:
      - 'session-dial-android/scripts/emulator-export-test.py'
      - '.github/workflows/emulator-export-test.yml'
```

By hand from the Actions tab, or when the test itself changes. It does **not** run on ordinary
app changes, because it takes a few minutes. To check export after changing the app, start it by
hand.

## The job

```yaml
jobs:
  export-test:
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

`timeout-minutes: 30` stops the run if the emulator hangs, so it cannot sit there for hours.

## Build steps

Checkout, Node 22 and Java 21 are the same as in [build-apk-workflow.md](build-apk-workflow.md).

```yaml
- name: Build debug APK
  run: |
    npm ci
    npx cap sync android
    cd android && ./gradlew assembleDebug --no-daemon
```

Builds the APK from the current code, so the test always runs against what is in the repository.

## Switching on fast emulation

```yaml
- name: Enable KVM
  run: |
    echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger --name-match=kvm
```

KVM is Linux's hardware virtualisation. The server has it, but ordinary programs are not allowed
to use it by default. These three commands open it up. With it the emulator boots in about 25
seconds; without it, booting takes many minutes and the system keeps freezing.

## Running the test

```yaml
- name: Run the export test on an emulator
  uses: reactivecircus/android-emulator-runner@v2
  with:
    api-level: 34
    target: default
    arch: x86_64
    profile: pixel_5
    disable-animations: true
    working-directory: session-dial-android
    script: |
      adb install -r android/app/build/outputs/apk/debug/app-debug.apk
      python3 scripts/emulator-export-test.py emulator-out
```

A ready-made action that downloads an Android image, boots it, runs the script lines, and shuts
it down.

| Setting | Meaning |
|---|---|
| `api-level: 34` | Android 14. |
| `target: default` | Plain Android without Google's apps. It still has the system file picker. |
| `arch: x86_64` | Matches the server's processor, which is what allows fast emulation. |
| `profile: pixel_5` | A phone-sized screen (1080 by 2340). The default is a tiny 320-wide screen. |
| `disable-animations` | Turns off system animations so screens settle at once. |
| `script` | Installs the APK, then runs the test and puts its output in `emulator-out`. |

`adb` is Android's command-line tool for talking to a phone or emulator.

## Keeping the evidence

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: emulator-export-test
    path: session-dial-android/emulator-out/
```

Attaches the screenshots and the saved CSV to the run. `if: always()` uploads them even when the
test fails, which is when the screenshots are most useful.
