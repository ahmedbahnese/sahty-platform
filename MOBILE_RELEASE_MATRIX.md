# Mobile Release Matrix

## Release rule

A Flutter project, a successful Dart analysis, or a successful build alone does not prove release readiness. Each platform needs integration evidence, a signed artifact, a real-device smoke test, and a beta acceptance result.

## Android

| Gate | Required evidence | Current status |
|---|---|---|
| Flutter integration tests | `flutter test integration_test` against production-like API | NOT VERIFIED; Flutter unavailable |
| Debug APK | `flutter build apk --debug --dart-define=API_BASE_URL=...` | NOT VERIFIED |
| Real Android phone | Install APK and test login, profile, doctors, appointments, records, prescriptions, medications | NOT VERIFIED |
| Release signing | Private keystore and `mobile/android/key.properties` supplied through secure CI secrets | Guard implemented; key not supplied |
| AAB | `flutter build appbundle --release --dart-define=API_BASE_URL=...` with release signing | NOT VERIFIED |
| Beta | Internal testing track, crash/log review, acceptance checklist | NOT STARTED |

The Android Gradle configuration now refuses a release build when `key.properties` is absent instead of silently using the debug key. `key.properties.example` documents the required fields and real keys remain ignored by Git.

## iOS

| Gate | Required evidence | Current status |
|---|---|---|
| Flutter integration tests | Run on simulator/device against production-like API | NOT VERIFIED; Flutter unavailable |
| Xcode build | `flutter build ios --release` on macOS with Xcode and CocoaPods | NOT VERIFIED |
| Signing | Apple Team, Bundle ID, certificates, provisioning profile, and secure CI credentials | NOT CONFIGURED |
| IPA | Archive/export signed IPA from Xcode or Flutter | NOT VERIFIED |
| TestFlight | Upload, internal beta, device acceptance, crash review | NOT STARTED |
| App Store | Review metadata, privacy declarations, signing, and submission | NOT STARTED |

## Production dependency

Both platforms require a reachable HTTPS API backed by the production-like staging/production path. The API base URL must be supplied through `--dart-define=API_BASE_URL`; no database credentials or service secrets are embedded in the mobile application.

## Current environment limitation

The current Linux environment has no Flutter or Dart executable, no Android SDK/Gradle toolchain suitable for a verified Flutter build, and no macOS/Xcode/CocoaPods for iOS. Android and iOS therefore remain `NOT VERIFIED` until their native toolchains and real devices are used.
