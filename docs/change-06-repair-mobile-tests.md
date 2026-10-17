# Change 06 — Repair Mobile Test and Typecheck Blockers

## Objective
Repair the existing React Native test setup so typechecking and Jest tests can run reliably before standalone APK release.

## Evidence
- `npm ci` completed successfully.
- `npm run typecheck` failed at `tests/cycling.test.tsx:9`, where `toBeOn ON SCREEN()` is malformed.
- Jest cannot resolve `@testing-library/react-native` in multiple test files.
- The existing `__tests__/App.test.tsx` passes, but emits asynchronous state-update warnings.
- The test run reports 9 failed suites and 1 passed suite.

## Requirements
1. Inspect `package.json`, the lockfile, Jest/Babel configuration, and every existing test file before changing dependencies.
2. Correct the malformed cycling assertion using an assertion supported by the installed test framework and actual component behavior.
3. Resolve the missing React Native Testing Library dependency appropriately. Update the lockfile if a dependency change is necessary.
4. Ensure test imports and screen/component assumptions match the current application. Do not fabricate UI behavior merely to make tests pass.
5. Address asynchronous test cleanup or waiting where needed.
6. Preserve app functionality, GPS tracking, embedded Flask, SQLite offline storage, MySQL sync, release signing, and all existing application screens.
7. Do not change database schema or credentials.
8. Do not modify release-signing secrets, generate a new keystore, build/install an APK, or apply broad dependency upgrades.
9. Run `npm run typecheck` and `npm test` after the fixes, reporting exact results and any remaining failures.
10. Update the relevant documentation with the changes and verification results.

## Acceptance criteria
- TypeScript typechecking succeeds.
- Jest tests pass, or remaining failures are explicitly explained with evidence.
- No release build is attempted during this change.
