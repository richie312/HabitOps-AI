## Execution

The platform is built incrementally in batches.

Each batch has a Markdown specification that acts as the source of truth.

### Batch 1 — React Native Foundation

Build the initial Android React Native application.

- TypeScript
- Android
- Dashboard
- Activities
- Vitals
- History
- Settings
- Local/dummy data
- Reusable components

Status: Initial implementation completed.

### Batch 2 — Mobile Application Completion

Complete and harden the React Native application before introducing
the backend.

- Review Batch 1 implementation against specification
- Complete missing mobile functionality
- Improve navigation
- Improve reusable components
- Improve local data architecture
- Improve validation
- Improve History
- Improve Settings
- Android usability
- Application error handling
- Prepare clean API boundary for the future Flask backend

No backend is introduced in this batch.

### Batch 3 — Flask + SQL Server Backend

Build the backend service.

- Flask
- Python
- REST API
- SQL Server
- Database schema
- Models
- CRUD APIs
- Validation
- Configuration
- Error handling
- API documentation

### Batch 4 — React Native + Flask Integration

Connect the mobile application to the Flask backend.

- REST client
- API models
- Remote data
- Activity persistence
- Vital persistence
- History from backend
- Error handling
- Network handling
- Local/remote data separation

### Batch 5 — Docker

Containerize the platform.

- Flask container
- Supporting services
- Docker Compose
- Environment configuration
- Local development deployment

### Batch 6 — Local AI + Agent

Introduce the AI layer.

- Ollama
- Local LLM
- Cloud Agent
- Agent tools
- Repository interaction
- Controlled permissions
- Agent orchestration

### Batch 7 — Kubernetes + ArgoCD

Deploy the platform.

- Kubernetes
- Deployments
- Services
- ConfigMaps
- Secrets
- Persistent storage
- ArgoCD
- GitOps deployment

### Batch 8 — SRE / Agentic Testing Laboratory

Introduce the local operational agent.

The local agent will be used for:

- automated tests
- application log analysis
- container log analysis
- failure detection
- container restart
- health checks
- troubleshooting
- correction proposals
- controlled automatic correction
- Kubernetes troubleshooting
- deployment verification
- recovery verification

The Cloud Agent remains responsible for higher-level planning,
development, architecture and independent verification.

## Development Model

From Batch 2 onward:

```text
Markdown specification
        ↓
Cloud Agent
        ↓
Implementation
        ↓
Repository
        ↓
Cloud Agent review