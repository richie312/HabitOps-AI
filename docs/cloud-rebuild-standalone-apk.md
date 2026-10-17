# HabitOps AI — Rebuild from Batch 1 with APK gates

Read the existing project documentation before editing anything.
Use batch-01-react-native.md through batch-04-mobile-api-integration.md,
the current architecture documentation, and the Android deployment runbook
where present. Locate the actual files; do not assume their directory.

OBJECTIVE
Rebuild and validate HabitOps AI sequentially from Batch 1 onward.
The final Android release APK must run without Metro, without a laptop-hosted
Flask server, and without USB/ADB pairing.

NON-NEGOTIABLE RULES
1. Start with Batch 1 and proceed in documented batch order.
2. After EACH batch, run the relevant automated tests and build a release APK.
   Do not start the next batch until the current batch passes its build gate.
3. If a batch fails, diagnose the first causal error, fix it, rerun its tests
   and release build, and report the evidence. Do not blindly upgrade/downgrade
   dependencies or change multiple versions to suppress errors.
4. Inspect the current Git status and preserve user changes. Do not overwrite
   or discard uncommitted work without explaining the impact.
5. Do not expose secrets, print signing passwords, or commit local credentials.
6. Never delete/recreate the existing MySQL container or its persistent volume
   mysql_ubuntu_rasp_device.
7. Preserve the documented React Native, embedded Python/Flask, SQLite offline
   persistence/sync, and Raspberry Pi MySQL architecture unless the docs prove
   a change is necessary. Report architectural blockers before replacing it.
8. Ensure the release JavaScript bundle is embedded in the APK. Metro may be
   used as a build-time bundler if required, but the installed release app must
   not require a running Metro server.
9. Keep a working checkpoint/commit for every passing batch, without committing
   secrets or unrelated user changes.
10. Do not claim runtime validation merely because Gradle produced an APK.

BUILD GATE AFTER EVERY BATCH
- Run the batch's relevant tests.
- Run the repository's release configuration validation if available.
- Run the Android release build.
- Confirm app-release.apk exists and record its size and SHA-256.
- Inspect the APK to confirm the JavaScript bundle is embedded.
- Record the exact commands, pass/fail results, changed files, and any blockers.
- Preserve the previous passing APK before replacing it.

FINAL DEVICE ACCEPTANCE
Verify the installed APK launches without Metro or laptop services, starts the
embedded Flask service on 127.0.0.1:8765, can save records locally offline,
and synchronizes to the existing Pi MySQL database when connectivity returns.
Do not claim these device checks passed unless they were actually performed.

FIRST ACTION
Inspect the repository, batch specifications, current diffs, Gradle/AGP/plugin
resolution, Chaquopy compatibility, release signing configuration, and existing
build scripts. Establish a documented baseline before modifying files.
Then execute Batch 1 and its APK build gate. Continue sequentially through the
remaining documented batches, stopping at a blocker rather than guessing.
