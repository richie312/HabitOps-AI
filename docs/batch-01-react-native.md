# Batch 01 — React Native Android Application

## Objective

Build the first working version of HabitOps as a native Android application
using React Native and TypeScript.

This batch must be completely independent of the Flask backend and SQL Server.

Use local/dummy data only.

The purpose of this batch is to establish the mobile application architecture
and UI so that the data layer can later be replaced with REST APIs.

---

## Current Scope

The application is a generic personal habit, activity and life tracker.

It should support tracking activities such as:

- Walking
- Workout
- Cycling
- Drum Practice

It should also support recording personal vitals:

- Blood pressure
- Glucose
- Pulse
- SpO2
- Weight

The application should not be designed exclusively as a health application.
The architecture should allow additional habits and activities to be added later.

---

## Required Screens

Implement the following screens:

1. Dashboard
2. Walking
3. Workout
4. Cycling
5. Drum Practice
6. Vitals
7. History
8. Settings

Provide clear navigation between these screens.

Use a consistent Android-friendly navigation experience.

---

## Dashboard

The Dashboard is the primary screen.

It should provide:

- Today's date
- Today's activity summary
- Activity completion/progress
- Quick visibility into tracked activities
- Recent or latest vitals where appropriate

The Dashboard should use reusable components rather than hard-coded
repeated UI blocks.

---

## Activity Screens

The following activities should have their own screens:

### Walking

Track dummy/local values such as:

- Distance
- Duration
- Steps

### Workout

Track dummy/local values such as:

- Workout duration
- Workout type
- Completion status

### Cycling

Track dummy/local values such as:

- Distance
- Duration
- Average speed

### Drum Practice

Track dummy/local values such as:

- Practice duration
- Practice type
- Completion status

The exact data model should be designed so that additional activity types
can be introduced without rewriting the application architecture.

---

## Vitals

The Vitals screen should allow local/dummy recording and displaying of:

- Blood pressure
- Glucose
- Pulse
- SpO2
- Weight

Use appropriate units.

Support displaying historical dummy records where practical.

Do not connect to any real medical device or external health API in this batch.

---

## History

Provide a screen for viewing previously recorded dummy/local activity and
vital records.

The history architecture should allow future replacement of local data with
records retrieved from the Flask backend.

---

## Settings

Provide a basic Settings screen.

It should establish a place for future application configuration.

Do not implement authentication, cloud synchronization or backend settings
in this batch.

---

## Data Architecture

Use local/dummy data for Batch 01.

Keep the following concerns separated:

### UI

React Native screens and reusable components.

### Models

TypeScript types/interfaces representing activities, workouts, cycling,
walking, drum practice and vitals.

### Data

Local dummy data and/or a simple local repository/service.

### Future API

The UI must not directly depend on hard-coded dummy data.

The architecture should make it possible to replace:

Local Data
→
REST API
→
Flask
→
SQL Server

without rewriting the screens.

---

## Reusable Components

Create reusable components where appropriate.

Examples include:

- Activity cards
- Progress indicators
- Metric cards
- Vital cards
- Buttons
- Input components
- Section headers
- Empty states

Avoid duplicating the same JSX structure across multiple screens.

---

## TypeScript

Use TypeScript throughout the application.

Define explicit types for application data.

Avoid using `any` unless there is a genuine technical reason.

Prefer strongly typed props and state.

---

## UI Requirements

The application should have:

- Clean Android-first UI
- Consistent spacing
- Consistent typography
- Reusable styles
- Clear visual hierarchy
- Scrollable content where required
- Reasonable empty states
- Basic form validation where input is required

Do not add unnecessary UI libraries.

Prefer React Native's built-in components unless a dependency is genuinely
required.

---

## Dependencies

Keep dependencies minimal.

Before adding a dependency:

1. Determine whether React Native already provides the required capability.
2. Check whether the existing project already has an equivalent dependency.
3. Add a dependency only when it provides meaningful value.

Do not add libraries simply for visual effects.

---

## Android

The application must run on the existing Android emulator.

The current development environment uses:

- React Native
- TypeScript
- Android
- Android API 37 emulator

The application must continue to build using the existing React Native
project configuration.

Do not modify Android build configuration unless required.

---

## Backend Boundary

Batch 01 must NOT implement:

- Flask
- SQL Server
- REST API
- Authentication
- Docker
- Kubernetes
- ArgoCD
- Cloud AI services

Those belong to later batches.

The mobile application should nevertheless be structured so that the backend
can be introduced without major UI restructuring.

---

## AI-Assisted Development

The project is intentionally being developed with AI assistance.

AI-generated code must be treated as proposed implementation rather than
automatically trusted code.

The coding agent should:

1. Read this document before implementing Batch 01.
2. Inspect the existing React Native project.
3. Reuse existing working code where appropriate.
4. Plan the required changes.
5. Modify the application files.
6. Review the resulting structure for consistency.
7. Report files created and modified.
8. Report anything that requires manual verification.

The coding agent should not modify this documentation unless explicitly
instructed.

---

## Definition of Done

Batch 01 is complete when:

- The React Native Android application builds successfully.
- The application launches on the Android emulator.
- Navigation between required screens works.
- Dashboard is functional using local/dummy data.
- Walking screen exists.
- Workout screen exists.
- Cycling screen exists.
- Drum Practice screen exists.
- Vitals screen exists.
- History screen exists.
- Settings screen exists.
- Reusable components are used.
- TypeScript types are defined.
- UI is separated from the local data layer.
- No Flask or SQL Server dependency exists.
- No backend is required to run the application.
- The project remains ready for Batch 02.

---

## Batch 01 Completion

After implementation, manually verify the application on the Android emulator.

Record any issues discovered during testing.

Do not proceed to Batch 02 until Batch 01 has been reviewed and accepted.