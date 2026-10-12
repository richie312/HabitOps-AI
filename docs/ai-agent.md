# HabitOps AI — AI & Agent Architecture

## Objective

HabitOps AI will use both local and cloud AI models.

The purpose is to learn how LLMs, agents, tools and model orchestration
work together in a real software system.

## Initial Architecture

User
 |
 v
Cloud Agent
 |
 +---- Cloud LLM
 |
 +---- Ollama
 |       |
 |       +---- Local LLM
 |
 +---- Tools
         |
         +---- Files
         +---- Git
         +---- Docker
         +---- Kubernetes
         +---- Logs
         +---- SQL
         +---- ArgoCD

## Responsibilities

### Cloud Agent

The cloud agent will initially handle:

- Task planning
- Tool selection
- Multi-step reasoning
- Code generation
- Code review
- Troubleshooting workflows

### Ollama

Ollama will provide local model inference for:

- Local coding experiments
- Code analysis
- Log analysis
- Model comparison
- Privacy-sensitive experiments

## Agent Tool Access

The agent will initially have read-only access.

Initial tools:

- Search files
- Read files
- Git status
- Git diff
- Git log
- Docker status
- Docker logs
- Kubernetes status
- Kubernetes logs
- SQL read/query
- ArgoCD status

Write and deployment tools will be introduced later.

## Safety Model

Agent permissions will be introduced progressively.

Level 1:
Read-only

Level 2:
Generate proposed changes

Level 3:
Modify development files

Level 4:
Build and test

Level 5:
Deploy to development

Production or destructive operations will require explicit human approval.

## Learning Objective

The important goal is not simply to use an AI agent.

The goal is to understand:

LLM
 ->
Agent
 ->
Tool
 ->
Observation
 ->
Reasoning
 ->
Action
 ->
Verification

and how local and cloud models can participate in this process.