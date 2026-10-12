# Change 05 — Standalone Android APK Shipping

## 1. Objective

Prepare HabitOps AI for distribution as a standalone Android APK that can be transferred to and installed on a physical Android phone.

The installed application must operate independently of the Windows development laptop and must not require Metro, a development server, USB debugging, wireless ADB pairing, or manually starting Flask.

This change prepares the release architecture and shipping workflow. It does not authorize an immediate APK build or installation.

## 2. Project Context

- Application: HabitOps AI
- Mobile framework: React Native
- Current mobile directory: `HabitOpsMobile/`
- Backend: Flask/Python
- Central database: MySQL 8 running in the existing Docker container on the Raspberry Pi
- Local database: SQLite or another approved durable on-device database
- Existing development environment: Windows 11, Node.js, Android SDK, Java, and Python 3.14
- Coding agent: Cloud GPT agent through `agent/cloud_developer.py`
- Architecture specification: `docs/change-04-embedded-flask-offline-sync.md`

The current development application uses Metro and a separately running Flask development server. These are development dependencies and must not be required by the final installed application.

## 3. Required End-User Experience

The intended workflow is:

1. The release process produces a standalone APK.
2. The APK is copied to the Android phone using SCP or another supported file-transfer method.
3. The user initiates installation on the phone. Android installation approval may be required.
4. The installed application appears in the Android launcher.
5. The user launches HabitOps AI normally.
6. The application starts its required local backend automatically and waits for readiness.
7. The React Native interface loads from the bundle packaged inside the APK.
8. Data operations use the MySQL-first, local-persistence fallback, and automatic synchronization architecture specified in Change 04.

Copying an APK must not be treated as equivalent to installing it. The workflow must explicitly distinguish transfer, installation, and first launch.

## 4. Standalone React Native Release

Inspect the existing React Native and Android Gradle configuration.

Ensure the release APK contains the production JavaScript bundle and required assets.

Requirements:

- The installed release must not attempt to fetch its JavaScript bundle from Metro.
- The application must not depend on Metro port 8081.
- Development-only host detection and LAN API configuration must not control the release API endpoint.
- The release API endpoint must target the embedded local backend.
- Debug and release configurations must be clearly separated.
- GPS, permissions, navigation, workouts, analytics, vitals, history, settings, and other existing functionality must be retained.
- Native modules and assets must be included in the release package.

Do not assume that a successful debug build proves that a standalone release works.

## 5. Embedded Flask/Python Runtime

Follow the feasibility assessment required by Change 04 before implementing the release.

Verify that the selected Android-compatible Python runtime supports the existing Flask application and its dependencies.

The release design must specify:

- How Python and Flask are packaged into the APK.
- How the backend starts when the application launches.
- How the application detects API readiness.
- How startup failures are reported and retried.
- How backend shutdown and application lifecycle events are handled.
- How the local API is bound and accessed securely.
- How the app avoids indefinite loading if the backend cannot start.

If the selected runtime cannot support the existing dependencies, document the blocker and present alternatives before changing the architecture.

Do not silently replace embedded Flask with a remotely hosted backend.

## 6. MySQL and Offline Persistence

Retain all requirements from Change 04.

- Prefer the existing Raspberry Pi MySQL database whenever it is reachable.
- Preserve the current MySQL host, port, database, user, and credential configuration.
- Do not replace the remote MySQL host with `localhost`.
- Use `localhost` only for communication with the embedded API running on the phone.
- Persist records durably on the phone when MySQL is unavailable.
- Synchronize pending records automatically when connectivity and MySQL availability return.
- Preserve stable identifiers and idempotency to prevent duplicate records.
- Never discard a locally persisted record after an unsuccessful synchronization attempt.
- Retain data across application and phone restarts.

The existing MySQL container, database, and Docker volume must not be deleted, recreated, or reset.

## 7. Configuration and Credentials

Inspect the existing `.env`, `.env.example`, mobile configuration, and build process.

Document how configuration values are supplied to the embedded backend in the release package.

For this private APK, packaging the required configuration is permitted by the project requirements. However:

- Do not print real secrets in build logs.
- Do not commit actual credentials to documentation or source-control examples.
- Distinguish the local API address from the central MySQL address.
- Ensure the packaged backend does not accidentally load development-only paths or settings.
- Verify that the release package contains the configuration required to start the backend.

## 8. APK Build and Signing Preparation

Inspect the current Android build configuration and determine the required release settings.

Document:

- Application ID and versioning.
- Debug versus release build variants.
- Release bundle generation.
- APK signing requirements.
- Secure handling and backup of the signing key.
- Output APK location.
- Expected Android architecture and native-library compatibility.
- Required permissions.
- Build prerequisites and exact PowerShell commands.

Do not generate or expose a signing key during the preparation stage unless separately authorized.

Do not modify the installed debug application or uninstall it as part of this documentation-only stage.

## 9. Transfer and Installation Workflow

Document the eventual transfer and installation procedure.

The procedure must:

- Produce a clearly identified APK artifact.
- Copy the APK to a known location on the phone using the selected transfer method.
- Verify that the transfer completed and that the APK file is intact.
- Explain how to initiate installation from the phone.
- Account for Android's approval requirements for installing APKs from that source.
- Explain how to launch the installed application.
- Avoid requiring Metro, an active development server, or ADB pairing after installation.

Do not claim that an APK can normally install itself merely because it was copied to the phone. Any fully automated installation method must be separately justified against Android's security and permission model.

## 10. Release Verification Plan

Before declaring the release ready, define tests for:

1. Release APK builds successfully.
2. APK contains a bundled JavaScript release bundle.
3. Application launches while Metro is stopped.
4. Application launches while the Windows laptop is unavailable.
5. Embedded Flask starts and becomes ready automatically.
6. The app does not depend on the laptop's IP address.
7. MySQL operations work when the Raspberry Pi database is reachable.
8. Offline writes survive application and phone restarts.
9. Pending records synchronize without duplicates when MySQL returns.
10. GPS and route-point persistence remain functional.
11. Existing screens and features operate in release mode.
12. A clean installation on the target phone works without development tooling.
13. Startup and network failures produce actionable errors rather than endless loading.
14. The final APK can be transferred, installed, and launched using the documented workflow.

Record actual results. Tests that have not been run must be marked as pending, not passed.

## 11. Implementation Sequence

Work in the following order:

### Stage A — Architecture validation
Review Change 04 and establish that the embedded Flask/Python runtime and dependencies are viable on Android.

### Stage B — Release preparation
Configure the production JavaScript bundle, Android release settings, runtime packaging, and configuration loading.

### Stage C — Offline and synchronization readiness
Verify durable local persistence, retry behavior, idempotency, and database recovery.

### Stage D — Release build readiness
Prepare the signing and build workflow, artifact location, and verification checklist.

### Stage E — Authorized release build
Only after the preceding stages have been reviewed and approved, build the release APK.

### Stage F — Transfer and installation
Only after explicit approval, transfer the APK to the phone, install it, and test first launch without Metro or a laptop-hosted backend.

## 12. Deliverables

Provide:

- A compatibility and architecture assessment.
- A list of release configuration changes.
- Updated build and shipping documentation.
- Exact commands for the eventual release build and APK transfer.
- A test matrix with pass, fail, and pending statuses.
- A list of known limitations.
- Confirmation that the existing MySQL data and container remain untouched.

## 13. Scope Restrictions

At this stage:

- Do not build the APK.
- Do not install or uninstall applications on the phone.
- Do not reset, delete, or recreate the MySQL container or its volume.
- Do not introduce a laptop-hosted Flask dependency into the final design.
- Do not claim Metro independence until demonstrated by a release-mode test.
- Do not make broad architectural changes before the embedded runtime feasibility gate is satisfied.

The immediate deliverable is a reviewed shipping plan, not an APK artifact.