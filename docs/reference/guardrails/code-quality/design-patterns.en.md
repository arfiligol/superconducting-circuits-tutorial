---
aliases:
  - Design Patterns
  - Architecture Patterns
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Service boundaries, dependency direction, and shared-logic rules for the rewrite branch.
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Design Patterns

The design goal in this project is to keep shared rules in stable places instead of letting each entry layer grow its own copy of the workflow.

## Core Rules

### Dependency Direction

- React components must not own business workflow orchestration
- FastAPI routers must not own full workflow logic
- CLI commands must not duplicate backend service logic
- shared rules belong in backend services or `src/core/`

### Dependency Injection

- inject service dependencies via constructors or explicit factories
- do not instantiate repositories, clients, or adapters ad hoc inside workflow functions
- framework-specific wiring belongs in the composition root

### Canonical Definition

- circuit definitions should have one canonical representation
- schemdraw, simulation, analysis, and API responses must not each maintain drifting definitions

### API Layer Responsibility

- request parsing
- auth / permission checks
- service invocation
- response mapping

It should not contain:

- long-form business branching
- persistence details
- duplicated transformations shared by multiple modules

## Agent Rule { #agent-rule }

```markdown
## Design Patterns
- Keep shared workflow logic in backend services or `src/core/`, not in React components, FastAPI routers, or CLI commands.
- Use dependency injection or explicit factories for services, repositories, and adapters.
- Keep one canonical circuit definition that feeds schemdraw, simulation, analysis, API, and CLI.
- API handlers should do I/O, auth, validation, service invocation, and response mapping only.
- CLI commands should orchestrate user input/output, then delegate to shared services/core.
```
