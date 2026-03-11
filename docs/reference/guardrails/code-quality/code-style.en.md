---
aliases:
  - Code Style
  - Implementation Style
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Shared Python and TypeScript style rules for the rewrite branch.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Code Style

The style rules in this project optimize for code that is readable, changeable, and testable.
If an implementation looks convenient in one layer but scatters shared rules across UI, API, and CLI, it is not acceptable.

## Cross-Language Principles

- prefer small diffs over broad refactors
- one function, one responsibility
- use explicit names; avoid vague abbreviations
- do not bury business logic inside route handlers, React components, or CLI commands
- when logic repeats, extract it into a shared layer before adding more call sites

## Python Rules

- use modern syntax: `list[str]`, `str | None`
- keep imports and formatting aligned with Ruff
- in scientific code, include units in names when that removes ambiguity, such as `frequency_hz`
- no `print()` in `core/` or service layers

## TypeScript Rules

- use TypeScript strict mode
- no unjustified `any`
- component props, service return types, and schema parse results must be typed
- React components should stay presentation-focused; data loading and mutation logic belongs in hooks / services

## Refactoring Rule

- make small, verifiable changes first
- solve structure before adding abstraction
- if an abstraction only serves one call site and does not reduce complexity, do not introduce it yet

## Agent Rule { #agent-rule }

```markdown
## Code Style
- **Standard**:
    - Python uses Ruff + modern Python syntax
    - TypeScript uses strict typing and consistent formatting
- **Naming**:
    - variables use clear nouns
    - functions use clear verb phrases
    - scientific names may include units when that removes ambiguity
- **Boundaries**:
    - do not put business workflow logic inside route handlers, React components, or CLI commands
    - shared logic belongs in services or `src/core/`
- **Refactoring**: prefer small, atomic changes
- **Complexity**: keep functions focused; split code when one function starts handling multiple responsibilities
```
