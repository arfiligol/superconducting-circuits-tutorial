---
aliases:
  - "Guardrails"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Guardrails

Development standards that ensure code quality and consistency.

!!! important "Source of Truth"
    This is the single source of truth for guardrails. All developers (human and AI agents) must follow it.

## How to Use

- **Humans**: Read each page for the "why" and detailed rules.
- **AI Agents**: Jump to the **[#agent-rule](#)** anchor at the bottom of each page and copy the block into the system prompt.

## Quick Reference

### Project Basics

| Rule | Description | Agent Rule |
|---|---|---|
| [Project Overview](./project-basics/project-overview.en.md) | Mission, scope, and audience | [#agent-rule](./project-basics/project-overview.en.md#agent-rule) |
| [Tech Stack](./project-basics/tech-stack.en.md) | Python (uv) + Julia (juliaup) | [#agent-rule](./project-basics/tech-stack.en.md#agent-rule) |
| [Folder Structure](./project-basics/folder-structure.en.md) | Clean Architecture layers | [#agent-rule](./project-basics/folder-structure.en.md#agent-rule) |

### Execution & Verification

| Rule | Description | Agent Rule |
|---|---|---|
| [Build Commands](./execution-verification/build-commands.en.md) | `uv sync`, `mkdocs serve`, script runs | [#agent-rule](./execution-verification/build-commands.en.md#agent-rule) |
| [Linting & Formatting](./execution-verification/linting.en.md) | Ruff, Pre-commit, BasedPyright | [#agent-rule](./execution-verification/linting.en.md#agent-rule) |
| [Testing](./execution-verification/testing.en.md) | Pytest, Julia Pkg.test | [#agent-rule](./execution-verification/testing.en.md#agent-rule) |
| [CI Gates](./execution-verification/ci-gates.en.md) | Required checks before merge | [#agent-rule](./execution-verification/ci-gates.en.md#agent-rule) |

### Code Quality

| Rule | Description | Agent Rule |
|---|---|---|
| [Code Style](./code-quality/code-style.en.md) | Clean Code, PEP 8, Type Hints | [#agent-rule](./code-quality/code-style.en.md#agent-rule) |
| [Type Checking](./code-quality/type-checking.en.md) | BasedPyright configuration | [#agent-rule](./code-quality/type-checking.en.md#agent-rule) |
| [Script Authoring](./code-quality/script-authoring.en.md) | CLI entrypoint structure | [#agent-rule](./code-quality/script-authoring.en.md#agent-rule) |
| [Data Handling](./code-quality/data-handling.en.md) | Paths and I/O rules | [#agent-rule](./code-quality/data-handling.en.md#agent-rule) |

### Documentation Design

| Rule | Description | Agent Rule |
|---|---|---|
| [Documentation Design](./documentation-design/documentation.en.md) | Index: standards / style / maintenance | [#agent-rule](./documentation-design/documentation.en.md#agent-rule) |
| [Circuit Diagrams](../../how-to/contributing/circuit-diagrams.en.md) | Schemdraw rules | [#agent-rule](../../how-to/contributing/circuit-diagrams.en.md#agent-rule) |

---

## Verification Commands

```bash
# Lint & Format
uv run ruff check . --fix && uv run ruff format .

# Type Check
uv run basedpyright src

# Test
uv run pytest

# Docs
uv run mkdocs build
```
