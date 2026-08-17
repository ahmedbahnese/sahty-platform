# Sahty Mobile Release Status

**Repository:** `ahmedbahnese/sahty-platform`
**Scope:** Flutter mobile release track only
**Status vocabulary:** `WORKING`, `PARTIAL`, `NOT VERIFIED`, `BROKEN`, `NOT IMPLEMENTED`

## Executive status

The repository contains a Flutter foundation, not a verified mobile release. The current environment is Linux without Flutter, Dart, Android SDK, Xcode, CocoaPods, or `xcodebuild`. No Android or iOS build is claimed.

| Area | Status | Evidence / limitation |
|---|---|---|
| Flutter toolchain | NOT VERIFIED | `flutter` and `dart` are unavailable in this environment. Required versions are Flutter 3.32.0 and Dart SDK `^3.8.0`. |
| Android | NOT VERIFIED | Native project exists; no Android SDK/Flutter CLI/Gradle build was available. |
| iOS | NOT VERIFIED | Native project exists; iOS requires macOS/Xcode/CocoaPods/signing and was not built. |
| Real API integration | PARTIAL | Authentication endpoints are wired in the foundation; feature workflows are not present in Flutter. |
| Secure storage | PARTIAL | `flutter_secure_storage` is used by the session foundation, but Flutter tests could not be run here. |
| Arabic/RTL/theme | PARTIAL | Arabic locale and theme are present; visual verification was not possible without Flutter. |
| Offline/network errors | PARTIAL | API client maps timeout, socket, non-JSON, and unauthorized responses; end-to-end mobile verification is pending. |

## Required workflow status

| Workflow | Status | Current finding |
|---|---|---|
| Login | PARTIAL | Real `POST /api/auth/login` repository method exists; Flutter execution not verified. |
| Logout | PARTIAL | Real `POST /api/auth/logout` plus local session clearing exists; Flutter execution not verified. |
| Session restoration | PARTIAL | Real `GET /api/auth/profile` restoration exists; Flutter execution not verified. |
| Registration | NOT IMPLEMENTED | No Flutter registration repository/screen was found. |
| Patient profile | PARTIAL | Profile is consumed during authentication restoration; dedicated patient feature is not implemented. |
| Appointments | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Doctors | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Hospitals | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Pharmacies | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Laboratories | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Radiology | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Blood bank | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Emergency | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Medical records | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Medications | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Prescriptions | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Vaccinations | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Family members | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| Notifications | NOT IMPLEMENTED | No Flutter feature repository/screen was found. |
| AI assistant | NOT IMPLEMENTED | No Flutter AI feature was found; backend support cannot be treated as mobile integration. |

## Role status

| Role | Status | Current finding |
|---|---|---|
| Patient | PARTIAL | Foundation session model supports the base user and active roles; patient workflows are not implemented. |
| Doctor | NOT VERIFIED | Backend role exists, but no Flutter professional dashboard or tested role flow exists. |
| Nurse | NOT VERIFIED | Backend role exists, but no Flutter professional dashboard or tested role flow exists. |
| Admin | NOT VERIFIED | Backend admin boundary exists, but no Flutter admin dashboard or tested role flow exists. |
| Hospital | NOT VERIFIED | Backend role exists, but no Flutter workflow or tested role flow exists. |
| Pharmacy | NOT VERIFIED | Backend role exists, but no Flutter workflow or tested role flow exists. |
| Laboratory | NOT VERIFIED | Backend role exists, but no Flutter workflow or tested role flow exists. |
| Radiology | NOT VERIFIED | Backend role exists, but no Flutter workflow or tested role flow exists. |
| Blood bank | NOT IMPLEMENTED | No verified Flutter role or workflow was found. |

The backend remains the security boundary. The Flutter foundation sends bearer tokens and uses the backend's role-switching endpoint; client-side role data is not sufficient evidence of authorization.

## Native configuration status

Android uses application ID `com.sahty.sahty_mobile`. Its manifest currently has no runtime camera, location, notification, or file/photo permissions. The release Gradle build type uses the debug signing configuration and must be replaced with a private release keystore before distribution.

iOS uses bundle identifier `com.sahty.sahtyMobile`. The checked-in `Info.plist` lacks camera, photo, location, and notification usage descriptions. Team, provisioning, CocoaPods, and actual Xcode build status are not verified.

## Tests and builds

| Check | Status |
|---|---|
| Flutter `--version` | NOT VERIFIED — executable unavailable |
| Dart `--version` | NOT VERIFIED — executable unavailable |
| `flutter doctor -v` | NOT VERIFIED — executable unavailable |
| `flutter pub get` | NOT VERIFIED |
| `flutter analyze` | NOT VERIFIED |
| `flutter test` | NOT VERIFIED |
| Existing mobile test files | PARTIAL — API client, session manager, and user model tests exist but were not run |
| `flutter build apk --debug` | NOT VERIFIED |
| `flutter build appbundle --release` | NOT VERIFIED |
| `flutter build ios --release` | NOT VERIFIED |
| Web/backend pytest | WORKING — 108 tests passed in the final web/backend QA run |
| Web lint/build | WORKING — lint completed with warnings and Vite production build succeeded |

## GitHub

The mobile documentation changes are intended to be committed as one logical mobile-release documentation phase after final diff review. No force push, reset, remote deletion, or history overwrite is permitted.

## Remaining blockers

The release track is blocked by the missing Flutter/Dart toolchain in the current environment, missing Android SDK/build tools, missing macOS/Xcode/CocoaPods for iOS, Android release signing, iOS signing/provisioning, native permission declarations, and the absence of the feature-level Flutter/API workflows listed above.
