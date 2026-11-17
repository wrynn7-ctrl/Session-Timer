# package.json

`package.json`

The project's description for npm, the tool that downloads JavaScript libraries. It lists what
the project needs and defines a few shortcut commands.

## Identity

```json
"name": "session-dial",
"version": "1.0.0",
"private": true
```

`private: true` stops the project being published to the public npm registry by accident. The
version here is only a label; the version Android shows comes from `android/app/build.gradle`.

## Scripts

```json
"scripts": {
  "postinstall": "node scripts/copy-libs.js",
  "sync": "cap sync android",
  "build:debug": "cap sync android && cd android && ./gradlew assembleDebug",
  "run:phone": "cap run android"
}
```

| Command | What it does |
|---|---|
| `postinstall` | Runs by itself after every `npm install`. See [copy-libs.md](copy-libs.md). |
| `npm run sync` | Copies `www` into the Android project and registers the plugins. |
| `npm run build:debug` | Syncs, then builds the debug APK. |
| `npm run run:phone` | Builds and installs on a phone connected by USB. |

## Dependencies: what ends up in the app

```json
"dependencies": {
  "@capacitor/core": "^8.6.0",
  "@capacitor/android": "^8.6.0",
  "@capacitor/local-notifications": "^8.3.1",
  "@capacitor/filesystem": "^8.1.5",
  "@capacitor/share": "^8.0.3",
  "@capacitor-community/keep-awake": "^8.0.1"
}
```

| Library | Used for |
|---|---|
| `@capacitor/core` | The bridge between the page's JavaScript and Android. |
| `@capacitor/android` | The Android half of that bridge, including `BridgeActivity`. |
| `@capacitor/local-notifications` | Scheduling the chimes as notifications. |
| `@capacitor/filesystem` and `@capacitor/share` | The export fallback: write the CSV to the cache, then open the share sheet. |
| `@capacitor-community/keep-awake` | The "Keep the screen on while timing" switch. |

The `^` means "this version or a newer one with the same first number".

## Dev dependencies: tools used only while building

```json
"devDependencies": {
  "@capacitor/cli": "^8.6.0",
  "typescript": "^7.0.2"
}
```

- `@capacitor/cli` provides the `cap` command.
- `typescript` is there because `capacitor.config.ts` is a TypeScript file and the `cap` command
  cannot read it otherwise. Without it, `npx cap sync` stops with "Could not find installation
  of TypeScript".
