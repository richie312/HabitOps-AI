# Batch 02 — Mobile Application Completion

## Objective

Complete and harden the React Native Android application created in
Batch 01 before introducing the Flask backend.

The Batch 02 implementation must use the existing Batch 01
application as its starting point.

The application must remain a local/dummy-data application during
this batch.

---

## Source of Truth

This document defines the requirements for Batch 02.

The Cloud Agent must:

1. Read this document.
2. Inspect the existing application.
3. Inspect Batch 01 documentation.
4. Compare the implementation against the requirements.
5. Identify incomplete, inconsistent, or weak implementation areas.
6. Implement the required improvements.
7. Review its own changes.
8. Report the files changed.
9. Report any requirements that could not be completed.

The agent must not invent backend requirements.

---

# Scope

## 1. Batch 01 Review

Review the existing implementation against:

`docs/batch-01-react-native.md`

Identify incomplete, inconsistent, or weak implementation areas.

Correct them as part of Batch 02.

The existing implementation must be treated as the starting point.
Do not unnecessarily rewrite working functionality.

---

## 2. Navigation

Ensure all required screens can be reached reliably.

Required screens:

- Dashboard
- Walking
- Workout
- Cycling
- Drum Practice
- Vitals
- History
- Analytics
- Settings

Navigation should be consistent and understandable.

The user should be able to move between the major application
sections without encountering dead ends or broken navigation.

---

## 3. Activity Tracking

Ensure the following activity flows are usable.

### Walking

Record:

- distance
- duration
- steps

### Workout

Record:

- duration
- workout type
- completion status

### Cycling

Record:

- distance
- duration
- average speed

### Drum Practice

Record:

- duration
- practice type
- completion status

Activity records must use the local repository/data layer.

The UI must not directly contain the application's persistent
activity data structure.

---

## 4. Vitals

Support recording and displaying:

- blood pressure
- glucose
- pulse
- SpO2
- weight

Provide appropriate input validation.

Invalid values should not silently become valid records.

The user should receive a clear message when entered values are
invalid.

Vital records must use the local repository/data layer.

---

## 5. History

History must display locally stored/dummy:

- activity records
- vital records

The presentation should be understandable and consistent.

History should use the repository/data layer rather than maintaining
a separate hardcoded history dataset inside the screen.

The user should be able to distinguish activity records from vital
records clearly.

---

## 6. Settings

Provide a basic Settings screen.

Settings must remain local.

No authentication or server configuration is required.

Settings should use appropriate local state/data structures and
should not introduce any backend dependency.

---

## 7. Activity Analytics & Graphs

Batch 02 will introduce graphical activity analytics.

The application will provide an Analytics screen with an activity
selector/dropdown allowing the user to select an individual activity:

- Walking
- Workout
- Cycling
- Drum Practice

Only one activity is selected at a time.

The selected activity will be displayed graphically over selectable
time ranges:

- 7 days
- 14 days
- 30 days
- 90 days
- 180 days
- 365 days

Only one time range is selected at a time.

The graph must update dynamically when either:

1. The selected activity changes.
2. The selected time range changes.

The graph must use the most meaningful metric for the selected
activity and clearly label the metric and units.

### Activity Metrics

| Activity | Primary Metric | Optional Metric |
|---|---|---|
| Walking | Distance | Steps |
| Workout | Duration | None |
| Cycling | Distance | Average Speed |
| Drum Practice | Duration | None |

Examples of units:

- Walking distance → km
- Walking steps → steps
- Workout duration → minutes
- Cycling distance → km
- Cycling average speed → km/h
- Drum Practice duration → minutes

The analytics remain based on local/dummy data in Batch 02.

No backend or REST API is required for the analytics feature.

The analytics implementation must obtain data through the local
repository/data layer.

Graph data must not be hardcoded directly inside the graph component.

The architecture should allow the same Analytics screen to consume
backend data later in Batch 04 without requiring the Analytics UI
to be rewritten.

### Empty State

If no records exist for the selected activity and time range,
display a clear empty-state message.

Do not display a broken, misleading, or meaningless graph.

### Analytics Interaction

The user should be able to:

1. Open the Analytics screen.
2. Select an activity.
3. Select a time range.
4. View the corresponding graph.
5. Change the activity.
6. Change the time range.
7. Immediately see the updated graph.

---

## 8. Local Data Architecture

Keep a clear separation between:

```text
UI
 ↓
Models
 ↓
Local Repository
 ↓
Local / Dummy Data