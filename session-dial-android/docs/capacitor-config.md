# capacitor.config.ts

`capacitor.config.ts`

Capacitor's settings for the project. The command `npx cap sync` reads it and writes a copy into
the Android project as `android/app/src/main/assets/capacitor.config.json`, which the app reads
when it starts.

```ts
import type { CapacitorConfig } from '@capacitor/cli';
```

Only brings in the list of allowed settings, so an editor can flag a mistyped one. This file is
TypeScript, which is why `typescript` is in `package.json`: the Capacitor command needs it to
read the file.

```ts
appId: 'com.sessiondial.app',
```

The app's permanent ID on the phone. Android uses it to tell apps apart. If it changes after the
app is installed, Android treats the new build as a different app with an empty session log. The
same ID appears in `android/app/build.gradle` and as the Java package name, and all three must
agree.

```ts
appName: 'Session Dial',
```

The name used when the Android project is first created.

```ts
webDir: 'www',
```

The folder holding the web page. `npx cap sync` copies everything in it into the Android project.

```ts
plugins: {
  LocalNotifications: {
    iconColor: '#B5562A'
  }
}
```

A setting for the notifications plugin: the tint of the small icon beside a chime notification.
It is the dial's copper colour.
