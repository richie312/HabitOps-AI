# Change 01 — GPS Walking and Running

## Objective
Enhance HabitOps AI with real-time GPS tracking and a live map for Walking and Running activities.

## Architecture
- React Native handles phone location permissions, GPS updates, distance calculations, activity timing, and live map rendering.
- Flask/Python remains responsible for backend persistence and processing in a later integration step.
- Keep the existing Python 3.14 environment and OpenAI Agents SDK unchanged.

## Requirements
1. Support separate Walking and Running activity types using a shared GPS tracking implementation.
2. Display a live map centred on the phone's current location.
3. Draw the travelled route as GPS updates arrive.
4. Display elapsed time, distance in kilometres, and current and average pace in min/km.
5. Provide Start, Pause, Resume, and Finish controls.
6. Request and handle Android location permissions properly.
7. Filter inaccurate GPS readings and prevent stationary GPS drift from inflating distance.
8. Save completed activities and route coordinates through the existing local repository.
9. Handle denied permissions, unavailable GPS, and temporary location interruptions gracefully.
10. Keep existing Dashboard, History, Analytics, Vitals, Cycling, Workout, Drum Practice, and Settings functionality working.

## Scope restrictions
- No Flask integration or SQL Server schema changes in this change.
- No cloud maps API key requirement unless genuinely necessary.
- No background tracking when the app is minimized in this initial version.
- Use libraries compatible with the existing bare React Native project and Android setup.
- Do not replace or rewrite unrelated screens.

## Verification
- Install and run on the Android emulator and, where possible, a physical Android phone.
- Verify permissions, live location, route drawing, distance, pause/resume, and activity saving.
- Run available TypeScript checks and Android build verification.
- Report changed files, added dependencies, commands executed, and any remaining limitations.