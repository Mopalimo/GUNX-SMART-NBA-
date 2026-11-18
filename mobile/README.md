# GUNX SMART NBA — React Native mobile frontend

This is a parallel React Native / Expo frontend in `mobile/`. The existing Python/Kivy Android app at the repository root is intentionally preserved while the new frontend is validated.

## Local development
- Node.js 20+
- From this directory: `npm install`
- Start Expo: `npx expo start`

## Android build
The `Mobile Android APK` GitHub Actions workflow generates the native Android project with Expo Prebuild and builds a debug APK. Download it from the workflow run's Artifacts section.

## Data integrity
All picks, odds, confidence percentages, scores and performance values currently shown are demo placeholders. They are not live fixtures, predictions, or betting recommendations. Connect the approved server-side NBA data/prediction API before production. Do not put provider API keys in this app.

## Existing app
The root Python/Kivy project and its current APK workflow remain unchanged. Do not remove or replace them until the React Native build and feature parity have been verified on a real Android device.