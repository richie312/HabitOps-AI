# Change 04 — Embedded Flask, MySQL-First Storage, and Offline Synchronization

## 1. Objective

Correct the Batch 4 architecture so HabitOps AI operates independently of the Windows development laptop. The Android application must be capable of running its backend locally, persisting data during database outages, and synchronizing pending records when the central MySQL database becomes available.

## 2. Required Architecture

### Android application
- Retain the existing React Native application and its features.
- Package the Flask backend and the required Python runtime with the Android application, using a technically supported Android integration.
- Start the embedded backend automatically when the application starts.
- Ensure the API is ready before the React Native interface sends requests.
- Expose the local API through `localhost` on a documented port.
- Do not require Flask to be started manually on Windows or hosted separately on another machine.

### Central MySQL database
- MySQL 8 runs in the existing Docker container on the Raspberry Pi.
- Preserve the existing database, container, volume, credentials, and connection configuration.
- Continue using the existing MySQL host and port settings in the backend environment configuration.
- Do not replace the MySQL host with `localhost`: the central database is on a different machine from the Android phone.
- Do not delete or recreate the existing MySQL container or volume.

### Local persistence
- Use durable on-device storage, preferably SQLite, for offline records.
- The local schema must preserve the same logical fields, data types, identifiers, timestamps, and relationships required by the MySQL schema.
- Support activities, workouts, walking, cycling, drum practice, vitals, GPS route points, and any other currently supported record types.
- Data must survive application restarts, phone restarts, and temporary loss of network connectivity.
- Do not rely solely on in-memory queues.

## 3. MySQL-First Write Strategy

For every create or update operation:

1. Check whether the central MySQL database is reachable.
2. If available, attempt the MySQL operation.
3. If the operation succeeds, return success to the application and update the local synchronization state.
4. If MySQL is unavailable or the operation fails because of a connectivity problem, persist the record locally and mark it as pending synchronization.
5. Never report a successful save unless the record has been persisted successfully in at least one durable store.
6. Never discard a locally saved record because an upload failed.

The application must not wait indefinitely for MySQL. Apply bounded connection and request timeouts, and fall back to local persistence promptly.

If a remote write has an ambiguous outcome—for example, the connection drops after MySQL commits the record—use idempotency keys or stable record identifiers to prevent duplicate records during retries.

## 4. Automatic Synchronization

- Run synchronization automatically when the application starts, when connectivity returns, and periodically while the application is active.
- Retry pending records with bounded exponential backoff.
- Upload records in a deterministic order that respects relationships, such as parent activities before GPS route points.
- Use stable identifiers and idempotent server operations.
- Mark a record synchronized only after the server confirms successful persistence.
- Retain pending records when an upload fails.
- Handle duplicate submissions, partial batches, application termination, and interrupted synchronization safely.
- Provide observable synchronization status and useful error logging.

The initial implementation must prioritize reliable synchronization while the app is active. Background synchronization must use Android-supported lifecycle mechanisms rather than assuming a permanently running process.

## 5. API and Configuration

- React Native must call the embedded Flask API using `localhost` and the configured local API port.
- The phone's local API address must not depend on the Windows laptop's LAN IP or the phone's current Wi-Fi IP.
- Preserve the existing central MySQL connection settings in the backend configuration.
- Package the required configuration with the private application build as appropriate for this project.
- Never print actual database passwords or secrets in logs.
- Clearly distinguish the local API address from the central MySQL host.
- Provide separate configuration for Android development and any future deployment environment where necessary.

## 6. Android Packaging and Startup Feasibility Gate

Before implementing the architecture, inspect the current React Native version, Android Gradle configuration, Python version, Flask dependencies, and backend imports.

Determine whether the existing Flask application and its dependencies can be packaged and executed on Android with a supported embedded Python runtime.

Document:
- The selected Python-on-Android integration and its compatibility with the current toolchain.
- Required Gradle and native Android changes.
- How the Flask process starts, stops, and recovers.
- How the local API port is allocated and readiness is detected.
- Any dependencies that cannot run on Android and their replacements.
- The impact on debug and release APK builds.

Do not silently substitute a separately hosted Flask server, a cloud API, or a different backend architecture.

If the embedded Flask approach is not technically viable with the existing stack, stop before making a broad architectural migration. Report the blocker, evidence, and smallest viable alternatives for a decision.

## 7. Database and Migration Safety

- Preserve the current MySQL database and its data.
- Keep the existing API contract wherever practical.
- Inspect and document differences between the current MySQL schema and proposed local SQLite schema.
- Ensure identifiers, timestamps, numeric values, nullable fields, and GPS coordinates round-trip correctly.
- Do not claim the system is offline-capable until persistence and synchronization tests pass.

## 8. Required Verification

The implementation is not complete until the following scenarios have been tested:

1. Android app starts and its embedded Flask API becomes ready without manually starting Flask on Windows.
2. A workout can be saved with MySQL available and is persisted centrally.
3. With MySQL unavailable, a workout saves locally and remains visible after restarting the app.
4. Multiple offline activities and their GPS points are retained without loss.
5. When MySQL returns, pending records synchronize automatically.
6. Repeated retries do not create duplicate activities, vitals, or route points.
7. Interrupted synchronization resumes safely after an app restart.
8. History and analytics behave consistently for locally pending and centrally synchronized records.
9. The Android debug APK builds and installs successfully.
10. Tests demonstrate that the application does not depend on the Windows laptop hosting Flask.

## 9. Documentation and Deliverables

Update the Batch 4 specification, backend README, mobile README, environment examples, API documentation, and architecture documentation as needed.

Provide:
- An architecture decision and dependency compatibility report.
- A list of files changed.
- Automated test results and Android build results.
- Exact commands for building, installing, and testing the application.
- Explicitly documented limitations and any tests that could not be run.

Do not mark unexecuted tests as passed.