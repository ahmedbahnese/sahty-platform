# Sahty Mobile Release Guide

The Flutter project lives under `mobile/` and consumes the existing Flask API. It does not replace the React/Vite web application or create a second backend.

## Declared toolchain

The repository declares Flutter 3.32.0 and Dart 3.8.0 in `MOBILE_SETUP.md`/`pubspec.yaml`. The current sandbox does not include the `flutter` or `dart` executables, so these versions are requirements to verify on a Flutter workstation, not a build result from this environment.

## Run and test

```bash
cd mobile
flutter pub get
flutter analyze
flutter test
flutter run --dart-define=API_BASE_URL=https://your-api.example.com/api
```

The app reads `API_BASE_URL` at compile time. The default Android emulator URL is `http://10.0.2.2:5001/api`; use an HTTPS URL for physical devices.

## Android verification

```bash
cd mobile
flutter build apk --debug --dart-define=API_BASE_URL=https://your-api.example.com/api
flutter build appbundle --release --dart-define=API_BASE_URL=https://your-api.example.com/api
```

Android release signing is not configured in the checked-in Gradle file; it currently uses the debug signing configuration. A release owner must configure a private keystore, Gradle signing properties, application ID ownership, launcher assets, and production permissions before publishing.

## iOS verification

Run on macOS with Xcode and CocoaPods:

```bash
cd mobile
flutter pub get
cd ios && pod install && cd ..
flutter analyze
flutter test
flutter build ios --release --dart-define=API_BASE_URL=https://your-api.example.com/api
```

The iOS project has a bundle identifier and generated Xcode structure, but signing, Apple team, provisioning, CocoaPods, permission usage descriptions, and a successful Xcode build still require verification on macOS.

## Implemented mobile foundation

The checked-in foundation includes the real login, logout, profile/session restoration, role switching, secure token storage, bearer-token API client, timeout and network error mapping, Arabic locale, RTL-ready theme, routing, and a session home screen. It intentionally does not provide fake medical data.

Feature screens and repositories for appointments, doctors, hospitals, pharmacies, laboratories, radiology, blood bank, emergency, medical records, medications, prescriptions, vaccinations, family members, notifications, and AI are not yet verified as mobile workflows. They must be connected to the existing Flask endpoints one at a time, with authentication and authorization tests, before being called release-ready.
