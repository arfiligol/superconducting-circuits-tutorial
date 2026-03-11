---
aliases:
  - Script Authoring
  - CLI Authoring
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/code-quality
status: stable
owner: docs-team
audience: contributor
scope: Placement, responsibility, and documentation rules for CLI commands.
version: v1.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Script Authoring

In this project, the CLI is not a secondary utility layer. It is a formal product interface.

## Placement

- new CLI commands should go to `cli/`
- during migration, legacy entry bridges may remain, but new workflows should not keep accumulating in legacy `src/scripts/`

## Structure

- use `typer`
- each command handles arguments, user input/output, and error presentation
- real workflows call shared services or `src/core/`
- command names use `kebab-case`

## Rules

- every command must provide `--help`
- exit behavior must be explicit
- do not copy internal API-handler logic into CLI code
- if a feature exists only in UI and cannot be triggered from CLI, treat that as a product gap

## Agent Rule { #agent-rule }

```markdown
## Script Authoring
- CLI is a first-class interface, not a leftover utility layer.
- New CLI work should go to `cli/`; avoid growing new workflows inside legacy `src/scripts/`.
- Use Typer for commands.
- Commands handle argument parsing, user I/O, and error presentation only.
- Real workflow logic must live in shared services or `src/core/`.
- Command names use `kebab-case`, and every command must have usable `--help`.
```
