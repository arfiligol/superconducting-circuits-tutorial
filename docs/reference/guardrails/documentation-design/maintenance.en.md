---
aliases:
  - "Documentation Maintenance"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
status: stable
owner: docs-team
audience: team
scope: "Documentation maintenance: bilingual sync, version/frontmatter updates, MkDocs checks"
version: v0.1.0
last_updated: 2026-01-30
updated_by: docs-team
---

# Documentation Maintenance

This page defines maintenance rules (bilingual sync, update rules, verification checklist).

---

## Bilingual Sync (required)

We use `mkdocs-static-i18n` with suffix structure:

- zh: `path/to/page.md`
- en: `path/to/page.en.md`

!!! warning "Sync rules"
    - New page: create the `.en.md` counterpart
    - Content changes: update both language versions
    - Delete/move: update both versions and fix all incoming links

---

## Frontmatter Updates

On any content change, at minimum update:

- `last_updated`: `YYYY-MM-DD`
- `updated_by`: `team` or `team/person`

Suggested versioning:

- `v0.0.X`: small edits (typos/format)
- `v0.X.0`: new sections / rule changes
- `vX.0.0`: major restructure (move/merge pages)

---

## Navigation and Link Hygiene

When adding/moving pages:

1. Update `mkdocs.yml` `nav:` to avoid orphan pages
2. Check all relative links (including `.en.md`)
3. If the page is SoT, ensure `tags` includes `sot/true`

---

## Verification

### Local preview

```bash
uv run mkdocs serve
```

### Build

```bash
uv run mkdocs build
```

!!! tip "Common issues"
    - For i18n/nav issues, check `nav:` and the `.en.md` suffix naming.

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: update `mkdocs.yml` nav and fix all relative links
- **Verify**: `uv run mkdocs build` must pass
```

