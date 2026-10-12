-- Active: 1769684204190@@192.168.1.5@3306
-- Active: 1769684204190@@192.168.1.5@3306
# Batch 03 — Flask + SQL Server Backend

## Objective

Build the HabitOps AI backend using Python, Flask and SQL Server.

Batch 03 creates the persistent REST API required by the application.

The React Native application must remain unchanged and must NOT be
connected to this backend during Batch 03.

React Native ↔ Flask integration will be implemented in Batch 04.

---

# Source of Truth

The Cloud Agent must:

1. Read this document completely.
2. Inspect the existing repository.
3. Inspect Batch 01 and Batch 02 documentation.
4. Inspect the existing backend directory.
5. Determine what already exists.
6. Identify missing functionality.
7. Create an implementation plan.
8. Implement the requirements.
9. Re-read important modified files.
10. Run available tests and verification.
11. Inspect Git status and diff.
12. Report exactly what was created, modified, tested and not tested.

The agent must not invent requirements outside this specification.

---

# 1. Technology

Use:

- Python
- Flask
- SQL Server
- pyodbc or an appropriate SQL Server database driver
- REST API
- JSON
- environment-based configuration

The backend must be maintainable and modular.

---

# 2. Backend Structure

The backend must reside under:

backend/

A suitable architecture is:

backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── routes/
│   ├── validators.py
│   └── ...
├── tests/
├── requirements.txt
├── .env.example
├── README.md
└── run.py

The exact structure may differ if the existing implementation has a
reasonable alternative.

Keep these responsibilities separated:

REST API
   ↓
Routes
   ↓
Services
   ↓
Repositories
   ↓
SQL Server

Routes must not contain large amounts of database logic.

# 3. Flask Application

Create a Flask application that:

- starts successfully
- uses an application factory where appropriate
- exposes REST endpoints
- returns JSON
- supports environment-based configuration
- has centralized error handling
- has useful logging

The application must not contain hardcoded credentials.

---

# 4. Configuration

Use environment variables for configuration.

Support configuration for:

- FLASK_ENV
- SQL_SERVER_HOST
- SQL_SERVER_PORT
- SQL_SERVER_DATABASE
- SQL_SERVER_USERNAME
- SQL_SERVER_PASSWORD

Create:

backend/.env.example

The example must contain placeholders only.

Never commit real credentials.

---

# 5. SQL Server

Use SQL Server as the persistent database.

Implement:

- connection management
- database access layer
- transaction handling
- database error handling
- schema creation or migrations

The database schema must be repeatable.

Document database setup in backend/README.md.

---

# 6. Data Model

The backend must support:

- Walking
- Workout
- Cycling
- Drum Practice
- Vital records

## Activity Record

Support:

- unique ID
- activity type
- recorded date/time
- duration
- distance
- steps
- workout type
- completion status
- cycling average speed
- drum practice type
- created timestamp
- updated timestamp

Activity-specific fields may be nullable.

A common activity model/table is preferred unless there is a strong
architectural reason otherwise.

## Vital Record

Support:

- unique ID
- recorded date/time
- systolic blood pressure
- diastolic blood pressure
- glucose
- pulse
- SpO2
- weight
- created timestamp
- updated timestamp

Use appropriate SQL Server data types.

---

# 7. Database Schema

Create the required SQL Server schema.

Include appropriate:

- primary keys
- indexes where useful
- NOT NULL constraints
- uniqueness constraints where appropriate
- sensible numeric/date types

The schema creation mechanism must be repeatable.

If migrations are used, document how they are created and applied.

---

# 8. Repository Layer

Database operations must be separated from routes.

Repositories should handle:

- create activity
- retrieve activity
- update activity
- delete activity
- filter activities
- create vital
- retrieve vital
- update vital
- delete vital
- filter vitals
- query analytics data

Repositories should not depend unnecessarily on Flask request objects.

---

# 9. Service Layer

Use a service layer for application/business operations where
appropriate.

Services should handle:

- activity creation
- activity retrieval
- activity updates
- activity deletion
- vital creation
- vital retrieval
- vital updates
- vital deletion
- analytics queries
- validation/business rules

Services should not depend directly on Flask request parsing.

# 10. Health Endpoint

Provide:

GET /api/health

Example:

{
  "status": "ok"
}

The health endpoint does not require authentication in Batch 03.

---

# 11. Activity API

Provide:

GET    /api/activities
POST   /api/activities
GET    /api/activities/<id>
PUT    /api/activities/<id>
DELETE /api/activities/<id>

Support filtering by:

- activity type
- start date
- end date

---

# 12. Vital API

Provide:

GET    /api/vitals
POST   /api/vitals
GET    /api/vitals/<id>
PUT    /api/vitals/<id>
DELETE /api/vitals/<id>

Support filtering by date range.

---

# 13. Analytics API

Provide:

GET /api/analytics/activity

Parameters:

- type
- days

Supported days:

- 7
- 14
- 30
- 90
- 180
- 365

Example:

GET /api/analytics/activity?type=Walking&days=30

Return data suitable for the Batch 02 Analytics screen.

The response should identify:

- activity
- time range
- metric
- unit
- records

The backend provides data only. It must not generate graphical UI.

---

# 14. Validation

Validate all incoming API data.

Validate:

- required fields
- data types
- activity types
- numeric values
- positive values where appropriate
- duration
- dates/timestamps
- workout type
- drum practice type
- completion status
- blood pressure
- glucose
- pulse
- SpO2
- weight

Invalid data must be rejected.

Invalid data must never silently become valid database records.

---

# 15. HTTP Status Codes

Use appropriate HTTP status codes, including:

- 200 OK
- 201 Created
- 204 No Content
- 400 Bad Request
- 404 Not Found
- 409 Conflict
- 500 Internal Server Error

Do not return HTTP 200 for every condition.

---

# 16. Error Responses

Use a consistent JSON error structure.

Example:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid activity duration"
  }
}

Do not expose:

- database passwords
- connection strings
- stack traces
- internal implementation details

---

# 17. Date and Time

Use a clearly documented date/time representation.

Prefer timezone-aware timestamps.

Document how timestamps are represented by:

- SQL Server
- Flask
- REST API

The design must be suitable for future React Native integration.

---

# 18. API Response Format

Use consistent JSON response structures.

A collection may use:

{
  "data": [],
  "count": 0
}

A single resource may use:

{
  "data": {}
}

The exact wrapper may differ if required by the existing architecture,
but responses must remain consistent.

Document the actual response format in backend/README.md.

---

# 19. Logging

Implement useful application logging.

Logs should help diagnose:

- startup
- requests
- validation failures
- database failures
- unexpected errors

Never log:

- passwords
- database credentials
- API keys
- secrets

Logging should be suitable for future Docker and Kubernetes operation.

---

# 20. Centralized Error Handling

Implement centralized Flask error handling for:

- validation errors
- malformed requests
- not found
- database errors
- unexpected exceptions

Return safe JSON responses.

Do not expose stack traces through the REST API.

---

# 21. CORS

Prepare the backend for future React Native access.

CORS may be enabled for development.

Keep the configuration structured so allowed origins can be
restricted later.

Do not implement authentication in Batch 03.

---

# 22. API Documentation

Create:

backend/README.md

Document:

- prerequisites
- Python environment
- installation
- dependencies
- environment variables
- SQL Server setup
- database schema/migrations
- how to start Flask
- health endpoint
- activity endpoints
- vital endpoints
- analytics endpoint
- request examples
- response examples
- testing instructions

The documentation must describe the actual implemented API.

---

# 23. Backend Tests

Create tests under:

backend/tests/

Tests should cover at least:

- application startup
- health endpoint
- activity creation
- activity retrieval
- activity filtering
- activity validation
- activity not found
- vital creation
- vital retrieval
- vital filtering
- vital validation
- analytics endpoint
- error handling

Tests must not require production credentials.

Use an appropriate test strategy.

If SQL Server is available, include integration tests.

If SQL Server is unavailable, provide unit/API tests using an
appropriate isolated or mocked database strategy and clearly document
the limitation.

---

# 24. Security

Authentication is out of scope.

Nevertheless:

- never hardcode credentials
- never commit secrets
- never expose credentials in responses
- never expose stack traces
- never construct unsafe SQL using string concatenation
- validate incoming data
- use parameterized queries or an appropriate ORM/database abstraction

---

# 25. Mobile Application Boundary

Batch 03 must NOT modify the React Native application to consume the
backend.

The Batch 02 application remains local/dummy-data based.

Batch 02 architecture:

React Native UI
       ↓
Typed Models
       ↓
Local Repository
       ↓
Local / Dummy Data

Batch 04 will introduce:

React Native UI
       ↓
Typed Models
       ↓
Repository Interface
       ↓
REST Repository
       ↓
Flask API
       ↓
SQL Server

---

# 26. Explicitly Out of Scope

Do NOT implement:

- React Native REST integration
- mobile API client
- authentication
- login
- OAuth
- JWT
- Docker
- Docker Compose
- Kubernetes
- ArgoCD
- Ollama
- local LLM
- cloud AI
- AI agent integration
- SRE automation
- autonomous remediation
- production deployment

These belong to later batches.

---

# AI-Assisted Development Workflow

The Cloud Agent is the primary development agent.

Workflow:

Read Batch 03 specification
        ↓
Inspect repository
        ↓
Inspect backend
        ↓
Inspect Batch 01 / Batch 02 architecture
        ↓
Identify existing functionality
        ↓
Create implementation plan
        ↓
Implement backend
        ↓
Re-read modified files
        ↓
Run tests
        ↓
Verify API structure
        ↓
Verify database configuration
        ↓
Inspect Git status/diff
        ↓
Report results

The agent must not claim implementation or verification that it did
not actually perform.

---

# Verification Requirements

Before reporting Batch 03 complete, verify:

1. Flask application starts or explain why it could not be started.
2. Configuration loads correctly.
3. SQL Server configuration is present.
4. Database schema exists.
5. Models exist.
6. Repository layer exists.
7. Service layer exists where appropriate.
8. Routes exist.
9. Validation exists.
10. Error handling exists.
11. Health endpoint works.
12. Activity API works.
13. Vital API works.
14. Analytics API works.
15. Backend tests are executed where possible.
16. SQL Server connectivity is tested if available.
17. Git status/diff is inspected.
18. All created/modified files are reported.
19. Any unverified requirement is explicitly reported.

The agent must not claim SQL Server connectivity works unless it
actually tested it.

---

# Definition of Done

Batch 03 is complete when:

- Flask backend exists
- configuration is implemented
- credentials are not hardcoded
- SQL Server integration exists
- database schema exists
- activity model exists
- vital model exists
- repository layer exists
- service layer exists where appropriate
- health endpoint works
- activity CRUD API exists
- activity filtering works
- vital CRUD API exists
- vital filtering works
- analytics API exists
- all four activity types are supported
- validation is implemented
- invalid data is rejected
- appropriate HTTP status codes are returned
- error responses are consistent
- centralized error handling exists
- logging exists
- API documentation exists
- backend tests exist
- available tests pass
- React Native remains unchanged
- no Docker/Kubernetes/AI infrastructure is introduced

If SQL Server or another required dependency cannot be accessed during
verification, the agent must clearly report that limitation.

Do not proceed to Batch 04 until Batch 03 has been reviewed and
accepted.