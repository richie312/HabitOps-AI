# Change 02 — Fix Android Startup Crash

## Problem
HabitOpsMobile crashes immediately on startup on the Android emulator.

Log evidence:
- `ExceptionInInitializerError`
- `IllegalStateException: SoLoader.init() not yet called`
- Stack trace points to `DefaultNewArchitectureEntryPoint.load()` and `MainApplication.kt:20`.

## Required changes
1. Inspect the current `HabitOpsMobile/android/app/src/main/java/` MainApplication.kt file and the React Native Android configuration.
2. Fix the initialization order so SoLoader is initialized before any New Architecture initialization that requires it.
3. Follow the correct initialization pattern for the project's installed React Native version and current architecture settings.
4. Preserve GPS native module/package registration and all existing application features.
5. Do not downgrade React Native, change Python, regenerate the project, or make unrelated changes.

## Verification
- Build the Android application using the existing project configuration.
- Report the exact files changed and build result.
- If the build cannot be verified, clearly state why and provide the command to run manually.