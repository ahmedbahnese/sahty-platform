# Mobile build status

This document records only verified facts about the Sahty Flutter foundation. A platform is not marked working without a successful build or test on its native toolchain.

| Target | Status | Verified fact |
|---|---|---|
| Flutter/Dart toolchain | NOT VERIFIED | Replit mobile check executed on 2026-08-18 and reported `Flutter: NOT AVAILABLE`; `flutter` and `dart` are unavailable in the current Linux sandbox. The repository declares Flutter 3.32.0 and Dart SDK `^3.8.0`. |
| Flutter analyze/test | NOT VERIFIED | Cannot run until Flutter is installed. Existing Dart tests cover the API client, secure session manager, and user model only. |
| Android debug build | NOT VERIFIED | Android project files exist, but Android SDK, Flutter CLI, and a Gradle wrapper are unavailable here. |
| Android release build | NOT VERIFIED | Release Gradle configuration currently uses the debug signing configuration. A private release keystore and signing properties are required. |
| iOS build | NOT VERIFIED | iOS project files exist, but this Linux environment has no macOS, Xcode, CocoaPods, or `xcodebuild`. |
| Web/backend integration | PARTIAL | The real Flask authentication endpoints are referenced by the mobile foundation; feature workflows are not implemented and verified in Flutter. |

## Current mobile foundation

The project under `mobile/` contains a real API client, bearer-token handling, secure token storage, login, logout, profile/session restoration, role switching, Arabic locale support, routing, theme, and a session home screen. It does not contain fake medical API responses.

The Android application ID is `com.sahty.sahty_mobile`. The Android manifest currently contains the launcher activity but no runtime permissions for camera, location, notifications, or files/photos. The release build type uses the debug signing configuration and must not be used for production distribution.

The iOS bundle identifier is `com.sahty.sahtyMobile`. The project has generated Xcode files and a basic `Info.plist`, but it does not yet declare camera/photo/location/notification usage descriptions or prove signing and provisioning. These must be completed and tested on macOS.

## Required commands on a Flutter workstation

```bash
cd mobile
flutter --version
dart --version
flutter doctor -v
flutter pub get
flutter analyze
flutter test
flutter build apk --debug --dart-define=API_BASE_URL=https://your-api.example.com/api
flutter build appbundle --release --dart-define=API_BASE_URL=https://your-api.example.com/api
```

For iOS on macOS:

```bash
cd mobile
flutter pub get
cd ios && pod install && cd ..
flutter analyze
flutter test
flutter build ios --release --dart-define=API_BASE_URL=https://your-api.example.com/api
```
