# HabitOps AI — Lab Environment

## Development Machine

- Device: Lenovo laptop
- OS: Windows 11 Home Single Language
- CPU: AMD Ryzen AI 7 350
- RAM: 24 GB
- Graphics: AMD Radeon integrated/shared memory
- Git: 2.52.0
- Python: 3.11.0
- Docker: 29.1.3
- Node.js: 24.21.0
- npm: 11.19.0
- WSL: 2
- WSL Distribution: Ubuntu

## Home Lab

### Kubernetes

- Raspberry Pi 4
- Kubernetes master
- ArgoCD
- Existing home-cluster infrastructure

## Planned AI Infrastructure

### Local Model

Ollama will initially run on the Lenovo development machine.

Purpose:

- Local LLM inference
- AI coding experiments
- Agent/model experiments
- Local/private processing

### Cloud AI

A cloud-based AI agent/model will be used alongside Ollama.

Purpose:

- Higher-capability reasoning
- Agent orchestration
- Code generation/review
- Tool-use experiments

## Application Infrastructure

Planned components:

- React Native
- Android
- Flask
- SQL Server
- Docker
- Kubernetes
- ArgoCD

## Development Principle

Start with the simplest working environment.

Add infrastructure only when required by the next learning stage.

## AI Lab Status

### Local LLM

- Runtime: Ollama
- Deployment: Docker
- Container: `nirvikalpa-ollama`
- API: `http://localhost:11434`
- Model: `qwen2.5-coder:7b`
- Model size: approximately 4.7 GB

### Cloud AI

- OpenAI Python SDK: 3.23.0
- API authentication: verified
- API connectivity: verified
- API usage currently blocked by exhausted API credit balance

### Python AI Environment

- Virtual environment: `habitops-lab`
- Location: `C:\Users\Richie\envs\habitops-lab`

### Important

API keys must never be committed to Git.

The cloud model and local Ollama model will be used together
in later agent experiments. 