# Mobile build status

This document records the verified mobile build state for the Sahty Flutter foundation.

| Target | Verified status | Reason |
|---|---|---|
| Flutter analysis/tests | Not run on this machine | The `flutter` and `dart` executables are not installed in the current Linux environment. |
| Android APK/AAB | Not built here | The project has an Android directory, but no Gradle wrapper or Android SDK tools are available in this environment. A build must be verified on a machine with Flutter, Android SDK, and the configured JDK. |
| iOS | Not built here | iOS builds require macOS, Xcode, CocoaPods, and signing/provisioning configuration. `xcodebuild` is unavailable in this environment. |

The Flutter foundation is present under `mobile/`, with Arabic locale support, secure session storage, an API client, authentication restoration, routing, and separate Android/iOS platform directories. This is a foundation only; the table above intentionally does not claim release readiness without successful platform builds.

## Required verification commands

Run these from `mobile/` on a machine with Flutter installed:

```bash
flutter pub get
flutter analyze
flutter test
flutter build apk --release
flutter build appbundle --release
```

For iOS, run on macOS after installing Xcode and CocoaPods:

```bash
flutter pub get
cd ios && pod install && cd ..
flutter analyze
flutter test
flutter build ios --release
```

Before release, configure the API base URL, Android signing, iOS bundle identifier, Apple team, provisioning profile, and production secrets through the platform's secure build configuration.
