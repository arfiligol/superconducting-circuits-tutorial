---
aliases:
  - Guardrails
  - Development Guardrails
tags:
  - diataxis/reference
  - audience/contributor
  - sot/true
  - topic/governance
status: stable
owner: docs-team
audience: contributor
scope: Top-level guardrail index for the current workspace and rewrite branch.
version: v2.0.0
last_updated: 2026-03-11
updated_by: docs-team
---

# Guardrails

This section is the single source of truth for workspace development rules.
The current branch direction is a rewrite toward **Next.js + FastAPI + CLI**, while preserving the scientific core and bilingual docs system.

## How to Use

- Humans: read the relevant rule pages for boundaries and rationale.
- AI agents: load only task-relevant guardrails, preferably via `_agent_catalog.yml`.
- Rule sync: `docs/reference/guardrails/` is the source of truth; `.agent/rules/` is the installed copy and must match each Agent Rule block.

## Quick Reference

### Project Basics

| Rule | Description | Agent Rule |
| --- | --- | --- |
| [Project Basics](./project-basics/index.en.md) | Index for project goal, stack, and structure | [#agent-rule](./project-basics/index.en.md#agent-rule) |
| [Project Overview](./project-basics/project-overview.en.md) | Data Browser / Editor / Simulation / Characterization / Analysis / CLI scope | [#agent-rule](./project-basics/project-overview.en.md#agent-rule) |
| [Tech Stack](./project-basics/tech-stack.en.md) | Next.js + FastAPI + CLI + Julia simulation stack | [#agent-rule](./project-basics/tech-stack.en.md#agent-rule) |
| [Folder Structure](./project-basics/folder-structure.en.md) | frontend/backend/cli/core boundaries for the rewrite branch | [#agent-rule](./project-basics/folder-structure.en.md#agent-rule) |

### Code Quality

| Rule | Description | Agent Rule |
| --- | --- | --- |
| [Code Quality](./code-quality/index.en.md) | Code quality overview | [#agent-rule](./code-quality/index.en.md#agent-rule) |
| [Code Style](./code-quality/code-style.en.md) | Shared Python / TypeScript implementation rules | [#agent-rule](./code-quality/code-style.en.md#agent-rule) |
| [Type Checking](./code-quality/type-checking.en.md) | BasedPyright + TypeScript strict rules | [#agent-rule](./code-quality/type-checking.en.md#agent-rule) |
| [Design Patterns](./code-quality/design-patterns.en.md) | Dependency and service-layer boundaries across API/UI/CLI | [#agent-rule](./code-quality/design-patterns.en.md#agent-rule) |
| [Script Authoring](./code-quality/script-authoring.en.md) | CLI command structure and responsibilities | [#agent-rule](./code-quality/script-authoring.en.md#agent-rule) |
| [Data Handling](./code-quality/data-handling.en.md) | metadata / trace-store split | [#agent-rule](./code-quality/data-handling.en.md#agent-rule) |
| [Logging](./code-quality/logging.en.md) | logging usage rules | [#agent-rule](./code-quality/logging.en.md#agent-rule) |

### UI/UX Quality

| Rule | Description | Agent Rule |
| --- | --- | --- |
| [UI/UX Quality](./ui-ux-quality/index.en.md) | UI/UX overview for the Next.js frontend | [#agent-rule](./ui-ux-quality/index.en.md#agent-rule) |
| [Theming](./ui-ux-quality/theming.en.md) | semantic tokens, dark mode, theme provider | [#agent-rule](./ui-ux-quality/theming.en.md#agent-rule) |
| [Component Guidelines](./ui-ux-quality/component-guidelines.en.md) | shadcn/ui, dialogs, forms, tables | [#agent-rule](./ui-ux-quality/component-guidelines.en.md#agent-rule) |
| [Layout Patterns](./ui-ux-quality/layout-patterns.en.md) | App Router layouts and master-detail rules | [#agent-rule](./ui-ux-quality/layout-patterns.en.md#agent-rule) |
| [State Management](./ui-ux-quality/state-management.en.md) | SWR / Context / RHF + Zod | [#agent-rule](./ui-ux-quality/state-management.en.md#agent-rule) |
| [Accessibility](./ui-ux-quality/accessibility.en.md) | a11y, keyboard, and ARIA rules | [#agent-rule](./ui-ux-quality/accessibility.en.md#agent-rule) |
| [Routing](./ui-ux-quality/routing.en.md) | Next.js App Router strategy | [#agent-rule](./ui-ux-quality/routing.en.md#agent-rule) |

### Execution & Verification

| Rule | Description | Agent Rule |
| --- | --- | --- |
| [Execution & Verification](./execution-verification/index.en.md) | build / lint / test / CI index | [#agent-rule](./execution-verification/index.en.md#agent-rule) |
| [Build Commands](./execution-verification/build-commands.en.md) | common frontend / backend / CLI / docs commands | [#agent-rule](./execution-verification/build-commands.en.md#agent-rule) |
| [Linting & Formatting](./execution-verification/linting.en.md) | Ruff / BasedPyright / frontend checks | [#agent-rule](./execution-verification/linting.en.md#agent-rule) |
| [Testing](./execution-verification/testing.en.md) | pytest / Vitest / Playwright / docs checks | [#agent-rule](./execution-verification/testing.en.md#agent-rule) |
| [CI Gates](./execution-verification/ci-gates.en.md) | merge quality gates for the rewrite branch | [#agent-rule](./execution-verification/ci-gates.en.md#agent-rule) |
| [Commit Standards](./execution-verification/commit-standards.en.md) | commit scope and message rules | [#agent-rule](./execution-verification/commit-standards.en.md#agent-rule) |

### Documentation Design

| Rule | Description | Agent Rule |
| --- | --- | --- |
| [Documentation Design](./documentation-design/documentation.en.md) | documentation-rule index | [#agent-rule](./documentation-design/documentation.en.md#agent-rule) |
| [Documentation Standards](./documentation-design/standards.en.md) | Diataxis and frontmatter rules | [#agent-rule](./documentation-design/standards.en.md#agent-rule) |
| [Documentation Maintenance](./documentation-design/maintenance.en.md) | bilingual sync and build flow | [#agent-rule](./documentation-design/maintenance.en.md#agent-rule) |

## Verification Commands

```bash
uv run ruff format .
uv run ruff check .
uv run basedpyright src
uv run pytest
./scripts/prepare_docs_locales.sh
./scripts/build_docs_sites.sh
```
