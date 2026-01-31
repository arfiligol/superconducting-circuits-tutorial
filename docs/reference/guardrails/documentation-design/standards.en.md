---
aliases:
  - "Documentation Standards"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
status: stable
owner: docs-team
audience: team
scope: "Diataxis boundaries, frontmatter/tags schema, and core documentation rules"
version: v0.1.0
last_updated: 2026-01-30
updated_by: docs-team
---

# Documentation Standards

This page defines the project-wide documentation standards (Diataxis + metadata + core constraints).

---

## Diataxis Framework

| Type | Directory | Goal | Orientation |
|------|-----------|------|------------|
| Tutorials | `docs/tutorials/` | Learning | Guided |
| How-to | `docs/how-to/` | Problem-solving | Task-oriented |
| Reference | `docs/reference/` | Information | Technical |
| Explanation | `docs/explanation/` | Understanding | Conceptual |

### Boundaries

=== "Tutorials"

    !!! tip "When to use"
        Help newcomers succeed by following steps.

    - ✅ prerequisites, step-by-step, verifiable outcome
    - ❌ complete specs, design debates, decision rationale

=== "How-to"

    !!! tip "When to use"
        Solve one specific problem / complete one task.

    - ✅ shortest path, clear steps
    - ❌ tutorial-style narrative, exhaustive option lists, rationale

=== "Reference"

    !!! note "When to use"
        Provide citeable specs and facts.

    - ✅ complete, precise, easy to scan
    - ❌ background motivation, teaching steps, stories

=== "Explanation"

    !!! info "When to use"
        Explain why the design is the way it is.

    - ✅ concepts, trade-offs, rationale
    - ❌ operational steps, exhaustive specs, imperative commands

---

## Frontmatter Schema

We follow the YAML frontmatter pattern already used across `docs/`:

| Property | Required | Format |
|----------|----------|--------|
| `aliases` | ✅ | list of strings |
| `tags` | ✅ | list of strings (must follow Tag Taxonomy) |
| `status` | ✅ | `draft` / `incubating` / `stable` / `deprecated` |
| `owner` | ✅ | `team` or `team/person` |
| `audience` | ✅ | `team` / `contributor` / `user` |
| `scope` | ✅ | short scope summary |
| `version` | ✅ | `vX.Y.Z` |
| `last_updated` | ✅ | `YYYY-MM-DD` |
| `updated_by` | ✅ | `team` or `team/person` |

!!! warning "Name validation"
    Any **person name** referenced in `owner` or `updated_by` must exist in the [Contributors Registry](../../contributors.en.md). Add new contributors before referencing them.

---

## Tag Taxonomy

Tags use `namespace/value`.

| Prefix | Purpose | Example |
|--------|---------|---------|
| `diataxis/*` | Diataxis type | `diataxis/reference` |
| `audience/*` | Target audience | `audience/team` |
| `sot/*` | Source of truth | `sot/true` |
| `topic/*` | Topic label | `topic/documentation` |

---

## Core Rules

!!! warning "Violations reduce consistency (and can make CI/MkDocs checks harder to maintain)"

| Rule | Description |
|------|-------------|
| Diataxis | Do not mix doc types |
| Links | Use standard Markdown internal links (relative paths) |
| Bilingual | Keep `.md` and `.en.md` in sync |
| Terms | Keep technical terms in English or bilingual |
| SoT | Mark authoritative docs with `sot/true` |
| No vague time | Avoid “soon/later/future”; use concrete dates (e.g. `2026-01-30`) |

---

## References

- [Documentation Style](./style.en.md)
- [Documentation Maintenance](./maintenance.en.md)

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Standards
- **Diataxis**: Tutorials / How-to / Reference / Explanation; do not mix types
- **Frontmatter**: aliases, tags, status, owner, audience, scope, version, last_updated, updated_by
- **owner/updated_by**: `team` or `team/person`; person names must be in contributors registry
- **Tags**: `diataxis/*`, `audience/*`, `sot/*`, `topic/*`
- **SoT**: mark authoritative docs with `sot/true`
- **No vague time**: avoid “soon/later/future”; use concrete dates
```

