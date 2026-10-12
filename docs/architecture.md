-- Active: 1769684204190@@192.168.1.5@3306
# HabitOps AI — System Architecture

## High-Level Architecture

```text
                         ┌──────────────────────┐
                         │     Android App      │
                         │    React Native      │
                         └──────────┬───────────┘
                                    │
                                  HTTPS
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Flask API       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      SQL Server      │
                         └──────────────────────┘


                         AI ENGINEERING LAYER

                    ┌────────────────────────────┐
                    │       Cloud Agent          │
                    │                            │
                    │ Planning / Tools / Tasks   │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
                    ▼                            ▼
             ┌─────────────┐              ┌─────────────┐
             │ Cloud Model │              │   Ollama    │
             │             │              │             │
             │ Reasoning   │              │ Local LLM   │
             └─────────────┘              └─────────────┘
                                                │
                                                │
                         ┌──────────────────────┴───────┐
                         │                              │
                         ▼                              ▼
                  Local Development               Home Lab
                  Environment                    Raspberry Pi 4
                         │                              │
                         │                              │
                    Git / Docker                 Kubernetes
                                                   ArgoCD
                                                   Logs

## AI Agent flow

User
 |
 v
Cloud Agent
 |
 +---- Cloud Model
 |
 +---- Ollama / Local Model
 |
 +---- Tools
        |
        +---- Git
        +---- Files
        +---- Docker
        +---- Kubernetes
        +---- Logs
        +---- SQL
        +---- ArgoCD

Agent Operating Model

Understand
    |
    v
Plan
    |
    v
Select Tool
    |
    v
Execute Tool
    |
    v
Observe Result
    |
    v
Reason
    |
    +---- More investigation
    |
    v
Act
    |
    v
Verify


Deployment Architecture

Git Repository
      |
      v
    ArgoCD
      |
      v
 Kubernetes
      |
      +---- Flask API
      +---- Agent services
      +---- Supporting services