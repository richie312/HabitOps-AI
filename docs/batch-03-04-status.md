# Batch 3 and Batch 4 Status

Updated 2026-10-16.

## Summary

Batch 3 backend and Batch 4 mobile-to-local-API/offline-storage changes are implemented in the working tree. The standalone release APK has now built successfully after DNS/network access recovered on the mobile network. No Gradle, Java, Kotlin, Node, React Native, or Chaquopy version was changed.

The successful Gradle task completed `assembleRelease`, including Chaquopy's Python 3.14 runtime, React Native JS bundling, Kotlin compilation, and APK packaging. The APK signature was verified with `apksigner` (APK Signature Scheme v2).

## Work completed and checked

- Backend uses the existing configured MySQL service first and app-private SQLite as a durable local fallback. No MySQL container, volume, grant, or schema was reset or recreated.
- Flask environment loading and pure-Python MySQL Connector mode are configured for the embedded Android runtime.
- Activity and vital API persistence, activity GPS-route API round-trip, MySQL health, and cleanup of temporary verification rows were checked against the existing service.
- Direct laptop-to-Raspberry-Pi MySQL connectivity was rechecked with the configured application account. A labeled test activity was inserted and read back successfully in `habitops.activities`; the test row was retained at the user's request for verification (`client_id` is available in the session report). The active MySQL identity reported `habitops_app@192.168.1.8`.
- The laptop Flask server was also started and exercised through HTTP: `/api/health` reported `database=ok`; `POST /api/vitals` returned `sync_state=synced`; `GET /api/vitals` read the same row back. That vital test row is retained in MySQL with `client_id=e0010159-2596-5fb2-adea-034581f95e6e`.
- Backend API tests: 12 passed.
- Mobile TypeScript check: passed.
- Release build packages the backend configuration into the private APK assets; secrets were not included in this report.
- The Android build targets arm64-v8a and x86_64 to match the configured Python 3.14 runtime support.

## Remaining work / acceptance gaps

1. **Device verification:** Install/launch the generated APK on the phone with Metro stopped. Verify local backend startup, persistence, MySQL writes, offline restart persistence, automatic sync, and duplicate handling.
2. **SQL Server wording conflict:** [Batch 3](./batch-03-flask-sqlserver.md) specifically requires SQL Server, while the existing application configuration and later [Batch 4](./batch-04-mobile-api-integration.md) and [Change 04](./change-04-embedded-flask-offline-sync.md) specify MySQL. The current implementation preserves the existing MySQL architecture and does not claim SQL Server compliance.
3. **GPS mobile UI:** The backend stores and returns route points, but the current mobile app has no phone GPS capture, permission flow, or live route UI. This remains an explicit Batch 4 acceptance gap.
4. **Phone-to-MySQL access:** The user reports that the MySQL container allows connections from all systems. The phone's actual MySQL connectivity has not yet been verified. The packaged APK uses the configured MySQL host `192.168.1.50`; check that the phone can route to that host and port 3306 and that the container is bound to a reachable interface. No MySQL grant was changed.
5. **APK details:** `HabitOpsMobile/android/app/build/outputs/apk/release/app-release.apk`, 73,954,571 bytes; SHA-256 `1DBE0A6ABEA83D3021E4D16E45060E38D2CB764336A05BAA8176D8AAC3F92717`.

## Build command

```powershell
Set-Location C:\Users\Richie\Documents\HabitOps-AI\HabitOpsMobile\android
.\gradlew.bat assembleRelease
```

Expected output after a successful build:

```text
HabitOpsMobile\android\app\build\outputs\apk\release\app-release.apk
```
