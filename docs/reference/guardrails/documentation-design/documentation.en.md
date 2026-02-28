---
aliases:
  - "Documentation Design"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
status: stable
owner: docs-team
audience: team
scope: "Documentation design index: standards / style / maintenance"
version: v0.6.0
last_updated: 2026-02-28
updated_by: docs-team
---

# Documentation Design

Index for documentation design rules (aligned with this repo’s `Native Single-Build Bilingual Pages` architecture).

---

## Quick Reference

| Rule | Description | Agent Rule |
|------|-------------|------------|
| [Standards](standards.md) | Diataxis + frontmatter/tags + core rules | [#agent-rule](standards.md#agent-rule) |
| [Style](style.md) | tone + visual elements (admonitions/tabs/mermaid) | [#agent-rule](style.md#agent-rule) |
| [Maintenance](maintenance.md) | bilingual sync + frontmatter updates + Zensical checks | [#agent-rule](maintenance.md#agent-rule) |
| [Explanation Physics](explanation-physics.md) | writing position, chapter skeleton, and cross-linking rules for Explanation/Physics | [#agent-rule](explanation-physics.md#agent-rule) |

---

## Canonical Term

The formal name for this project's bilingual documentation-site architecture is:

- `Native Single-Build Bilingual Pages`

This means:

- one native `zensical.toml`
- one native build
- paired `.md` / `.en.md` content pages
- same-page language switching, but not a full Separate Builds setup

---

## Related

- Visuals:
  - [Circuit Diagram Guide](../../../how-to/contributing/circuit-diagrams.md) (Schemdraw → SVG)
- CLI docs:
  - [CLI Docs Automation](../../../how-to/contributing/cli-docs-automation.md)

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Design
- **Standards**: Diataxis + frontmatter/tags + core rules (see `standards.md`)
- **Style**: tone + visual elements (admonitions/tabs/mermaid) (see `style.md`)
- **Maintenance**: bilingual sync + frontmatter updates + Zensical checks (see `maintenance.md`)
- **Explanation Physics**: teaching position, chapter skeleton, and cross-linking rules (see `explanation-physics.md`)
- **Architecture Term**: the formal name of this bilingual docs architecture is `Native Single-Build Bilingual Pages`
- Treat sub-pages as source of truth for details.
```
