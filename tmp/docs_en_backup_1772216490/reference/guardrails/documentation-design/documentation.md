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
version: v0.4.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Documentation Design

Index for documentation design rules (aligned with this repo’s Separate Builds multilingual architecture).

---

## Quick Reference

| Rule | Description | Agent Rule |
|------|-------------|------------|
| [Standards](standards.en.md) | Diataxis + frontmatter/tags + core rules | [#agent-rule](standards.en.md#agent-rule) |
| [Style](style.en.md) | tone + visual elements (admonitions/tabs/mermaid) | [#agent-rule](style.en.md#agent-rule) |
| [Maintenance](maintenance.en.md) | bilingual sync + frontmatter updates + Zensical checks | [#agent-rule](maintenance.en.md#agent-rule) |
| [Explanation Physics](explanation-physics.en.md) | writing position, chapter skeleton, and cross-linking rules for Explanation/Physics | [#agent-rule](explanation-physics.en.md#agent-rule) |

---

## Related

- Visuals:
  - [Circuit Diagram Guide](../../../how-to/contributing/circuit-diagrams.en.md) (Schemdraw → SVG)
- CLI docs:
  - [CLI Docs Automation](../../../how-to/contributing/cli-docs-automation.en.md)

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Design
- **Standards**: Diataxis + frontmatter/tags + core rules (see `standards.en.md`)
- **Style**: tone + visual elements (admonitions/tabs/mermaid) (see `style.en.md`)
- **Maintenance**: bilingual sync + frontmatter updates + Zensical checks (see `maintenance.en.md`)
- **Explanation Physics**: teaching position, chapter skeleton, and cross-linking rules (see `explanation-physics.en.md`)
- Treat sub-pages as source of truth for details.
```
