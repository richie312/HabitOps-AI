# Change 03 — Cycling GPS and React Native UI Fix

## Objective

Fix the React Native text-rendering error and extend the existing GPS tracking system to Cycling.

## Issue 1 — UI rendering error

The Walking screen displays:

`Text strings must be rendered within a <Text> component.`

Requirements:
- Inspect App.tsx and all GPS-related React Native components.
- Identify and fix text nodes rendered outside React Native Text components.
- Check conditional rendering expressions, fragments, View components and map overlays.
- Apply the same correction to Running and Cycling where necessary.
- Do not suppress the warning or hide the error overlay as a workaround.

## Issue 2 — GPS Cycling

- Reuse the existing native GPS location service and route map.
- Support Start, Pause, Resume and Finish.
- Display live GPS position and travelled route.
- Calculate distance, duration, current speed and average speed.
- Use km/h for cycling speed.
- Preserve existing GPS accuracy and drift filtering, with appropriate cycling speed thresholds.
- Save cycling sessions and route coordinates using the existing local repository.
- Include saved cycling data in History and Analytics.
- Ensure Walking, Running and Cycling share reusable GPS logic rather than three independent implementations.

## Scope

- Preserve React Native 0.87.1 and the existing Android native modules.
- Preserve the SoLoader initialization fix.
- Do not modify Python 3.14, Flask or SQL Server.
- Preserve all other application features.
- Keep foreground-only GPS tracking for now.

## Verification

- Check TypeScript.
- Check for invalid React Native text rendering.
- Verify native package registration.
- Build the Android debug APK if command execution is available.
- Report files changed, dependencies, tests and remaining limitations.