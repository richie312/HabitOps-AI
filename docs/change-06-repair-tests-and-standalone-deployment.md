# Change 06 — Repair Tests and Establish Standalone Deployment Runbook

## Objective
Repair the current mobile test/typecheck blockers and establish a reusable Standalone Deployment documentation category for all future APK releases.

## Part A — Repair test blockers
1. Inspect package.json, package-lock.json, Jest/Babel configuration, and all affected tests.
2. Fix the malformed assertion in tests/cycling.test.tsx.
3. Resolve the missing @testing-library/react-native dependency appropriately.
4. Fix test/component mismatches and asynchronous test cleanup where necessary.
5. Run npm run typecheck and npm test. Report exact results.
6. Do not conceal or bypass failing tests. Do not run npm audit fix --force.
7. Do not change application behavior merely to satisfy incorrect tests.

## Part B — Create the Standalone Deployment documentation category
Inspect docs/SUMMARY.md, existing README/runbook files, GitBook configuration, docs/gitbook-docs.yaml, and docs/change-04-embedded-flask-offline-sync.md and docs/change-05-standalone-apk-shipping.md.

Create a dedicated docs/standalone-deployment/ category containing:
- README.md: category overview and navigation.
- release-runbook.md: repeatable end-to-end release instructions.

Register the category in docs/SUMMARY.md and any applicable navigation/index configuration. Preserve existing links and do not move or delete existing documentation unnecessarily. If documentation paths are protected, report the exact limitation and provide the complete proposed files.

## Part C — Required release runbook

Document the following repeatable process for future customisations and redeployments:

1. Finish and review app changes. Inspect Git status/diff. Keep secrets, keystores, and passwords out of Git.
2. From HabitOpsMobile, run npm ci, npm run typecheck, and npm test. A failed check blocks release until resolved or explicitly assessed and documented; never silently skip checks.
3. Review dependency audit findings without applying broad automatic upgrades. Document known warnings.
4. Verify Android SDK/build-tools/NDK and compatible JDK configuration against the project requirements.
5. Verify the release keystore and all required user-level Gradle properties without printing secrets:
   HABITOPS_RELEASE_STORE_FILE
   HABITOPS_RELEASE_STORE_PASSWORD
   HABITOPS_RELEASE_KEY_ALIAS
   HABITOPS_RELEASE_KEY_PASSWORD
   HABITOPS_MYSQL_PASSWORD
6. Verify the configured keystore exists, and maintain a protected backup. Use the same release key for compatible future updates.
7. Verify the Raspberry Pi MySQL service, database, required schema/tables, and application-user connectivity. Do not delete, recreate, or reset the existing MySQL container or its persistent volume. Apply reviewed, versioned schema migrations only when required.
8. Confirm architecture: React Native JavaScript is bundled into the release; Flask/Python runs inside the APK on 127.0.0.1:8765; MySQL stays on the Raspberry Pi; SQLite retains offline writes and supports subsequent sync. Do not substitute laptop-hosted Flask or Metro.
9. Validate release configuration, then build using the repository's documented command (currently ./gradlew.bat clean assembleRelease from HabitOpsMobile/android), after prerequisites pass.
10. Verify the APK exists and is signed. Inspect its contents for assets/index.android.bundle, embedded Python/runtime/backend modules, required native libraries, and expected ABIs. Do not infer standalone readiness from a debug build.
11. Calculate SHA-256, archive a versioned APK and release evidence, and record app version, build date, commit, hash, test outcomes, and known limitations.
12. Transfer to the Android phone via the documented Termux SSH/SCP workflow. Compare source and destination SHA-256 before installation.
13. Install manually and test cold launch with Metro stopped and the laptop unavailable. Verify navigation, activities, GPS/routes, vitals, history, analytics, settings, embedded backend readiness, MySQL writes, offline SQLite persistence, sync without duplicates, and error/retry behavior.
14. Record results in a release verification checklist. Mark only actually executed tests as passed.
15. Explain versionCode/versionName updates for subsequent releases and signing compatibility when upgrading an existing installation.

## Architecture and safety constraints
- MySQL remains on Raspberry Pi 192.168.1.50:3306.
- Do not change the existing MySQL container or volume.
- No Metro, ADB pairing, or laptop-hosted Flask dependency for the installed APK.
- Do not expose passwords in logs, command output, Git, or documentation.
- Do not build, transfer, or install an APK as part of this change.
- Do not generate or replace the user's release keystore.
- Do not invent a public GitBook URL. Document the GitBook publication limitation if relevant.

## Verification and reporting
Run the Part A checks and report exact results.
Review the runbook against the current Change 04/05 implementation; distinguish confirmed behavior from pending physical-device tests.
Report every file created or changed, navigation changes, commands to use for future releases, and any remaining blockers.
