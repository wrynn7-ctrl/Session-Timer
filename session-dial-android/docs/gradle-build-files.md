# The Gradle build files

Gradle is the tool that turns the Android project into an APK. Three files hold the settings that
matter. All three came from the Capacitor template; the only project-specific values are the app
ID and version in the third.

## `android/variables.gradle`: version numbers in one place

```groovy
ext {
    minSdkVersion = 24
    compileSdkVersion = 36
    targetSdkVersion = 36
    androidxAppCompatVersion = '1.7.1'
    ...
}
```

| Setting | Meaning |
|---|---|
| `minSdkVersion = 24` | The oldest Android the app installs on: Android 7. |
| `compileSdkVersion = 36` | The Android version the code is compiled against. The build machine needs SDK level 36 installed. |
| `targetSdkVersion = 36` | The Android version the app says it was made for. Android applies that version's rules to it, for example asking before showing notifications. |
| The rest | Versions of Google's support libraries that Capacitor uses. |

The plugins read these same values, so the whole build agrees on them.

## `android/build.gradle`: settings for the whole project

```groovy
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.13.0'
        classpath 'com.google.gms:google-services:4.4.4'
    }
}
```

Says where to download build tools from (Google's library site and Maven Central) and which ones
are needed. The first is the Android build plugin. The second is for Google services such as
push messaging; this app does not use it, and it stays switched off (see the end of this page).

```groovy
apply from: "variables.gradle"
```

Loads the version numbers above.

```groovy
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
```

The same two download sites, for the app's own libraries.

```groovy
task clean(type: Delete) {
    delete rootProject.buildDir
}
```

Defines `./gradlew clean`, which deletes build output.

## `android/app/build.gradle`: settings for the app itself

```groovy
apply plugin: 'com.android.application'
```

Says this module builds an installable app.

```groovy
android {
    namespace = "com.sessiondial.app"
    compileSdk = rootProject.ext.compileSdkVersion
    defaultConfig {
        applicationId "com.sessiondial.app"
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1
        versionName "1.0"
        ...
    }
```

- `applicationId` is the app's ID on the phone. It must match `appId` in `capacitor.config.ts`.
- `namespace` is the Java package of the app's own code (`MainActivity`, `SaveFilePlugin`).
- `versionCode` is a whole number Android uses to decide whether a build is newer. Raise it for
  each release you hand out. `versionName` is the version people see.
- `aaptOptions.ignoreAssetsPattern` controls which files in `www` are left out of the app. The
  template adjusts the default so that web files are not skipped by mistake.

```groovy
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
```

Settings for a release build. `minifyEnabled false` means the code is not shrunk or renamed. The
project only builds debug APKs so far, so this block is not yet in use.

```groovy
dependencies {
    implementation "androidx.appcompat:appcompat:$androidxAppCompatVersion"
    implementation "androidx.coordinatorlayout:coordinatorlayout:$androidxCoordinatorLayoutVersion"
    implementation "androidx.core:core-splashscreen:$coreSplashScreenVersion"
    implementation project(':capacitor-android')
    implementation project(':capacitor-cordova-android-plugins')
    testImplementation ...
}
```

The libraries compiled into the app: Google's support libraries and Capacitor's Android half.
The `test...` lines are for the template's example tests.

```groovy
apply from: 'capacitor.build.gradle'
```

Loads the generated file that adds the four npm plugins and sets Java 21. `npx cap sync` rewrites
that file, so it should not be edited by hand.

```groovy
try {
    def servicesJSON = file('google-services.json')
    if (servicesJSON.text) {
        apply plugin: 'com.google.gms.google-services'
    }
} catch(Exception e) {
    logger.info("google-services.json not found, ...")
}
```

Turns on Google services only if a `google-services.json` file exists. This project has none, so
the block does nothing. The log line it prints is harmless.

## Related settings

- `android/gradle.properties` gives Gradle 1.5 GB of memory and switches on the AndroidX
  libraries.
- `android/gradle/wrapper/gradle-wrapper.properties` pins Gradle 8.14.3. The `gradlew` script
  downloads that version on first run, which is why the first build is slow.
