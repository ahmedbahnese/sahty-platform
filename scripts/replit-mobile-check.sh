#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

printf '%s\n' '== Sehaty mobile Replit check =='
printf 'Flutter: '
if command -v flutter >/dev/null 2>&1; then
  flutter --version | head -n 1
else
  printf '%s\n' 'NOT AVAILABLE'
  printf '%s\n' 'Install/enable the Flutter package from replit.nix before running mobile checks.' >&2
  exit 2
fi

printf 'Dart: '
if command -v dart >/dev/null 2>&1; then
  dart --version 2>&1
else
  printf '%s\n' 'NOT AVAILABLE' >&2
  exit 2
fi

flutter doctor -v
cd mobile
flutter pub get
flutter analyze
flutter test
