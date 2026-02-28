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
scope: "Documentation maintenance: bilingual sync, version/frontmatter updates, Zensical checks"
version: v0.5.0
last_updated: 2026-02-28
updated_by: docs-team
---

# Documentation Maintenance

This page defines maintenance rules (bilingual sync, update rules, verification checklist).

---

## Bilingual Sync (required)

This project uses a **single native config**:

- config file: `zensical.toml`
- source files: `.md` and `.en.md` side-by-side
- site-level navigation and build settings: single source of truth in `zensical.toml`

!!! info "Native Zensical standard"
    Documentation standards now align with native `zensical.toml`.  
    Legacy YAML dual-config files are no longer the documentation standard, and the docs no longer assume a dual-config workflow.

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

## Native Zensical Audit (documentation scope)

From a documentation-maintenance perspective, the migration to native `zensical.toml` requires four aligned updates:

1. All docs commands must assume a single `zensical.toml` workflow.
2. All maintenance guidance must describe one config file, not legacy mirrored dual-config navigation.
3. All navigation rules must point to `zensical.toml` as the only site-level source of truth.
4. README, CI guidance, and contributing docs must use the same command set to avoid mixed legacy instructions.

---

## Navigation and Link Hygiene

When adding/moving pages:

1. Update navigation and site-level settings in `zensical.toml`
2. Check all relative links (including `.en.md` counterparts)
3. If the page is SoT, ensure `tags` includes `sot/true`

---

## Native Single-Build Bilingual Pages

The formal name of this project's current architecture is:

- `Native Single-Build Bilingual Pages`

Its technical shape is:

- one native config: `zensical.toml`
- paired source files: `.md` and `.en.md`
- native language selector entries: `extra.alternate` as the site-level fallback

!!! info "Same-page switching"
    Under `Native Single-Build Bilingual Pages`, native Zensical `extra.alternate` only provides site-level links.  
    It does not directly model the current page's language counterpart.  
    To provide same-page switching without MkDocs plugins, this project loads `docs/javascripts/language-switcher.js` via native `extra_javascript` and rewrites the selector links in the browser based on real `.md` / `.en.md` file pairs.

!!! warning "Scope and limits"
    - If a page has no `.en.md` (or no `.md`) counterpart, the selector keeps the site-home fallback.
    - This only solves content-page routing. Site chrome (theme language, built-in labels, single nav labels) still has one canonical language in a single build.
    - If the project later needs a fully localized UI shell per language, the native direction is Separate Builds (one native config/build per language).
    - If `.md` / `.en.md` pages are added, removed, or moved, `docs/javascripts/language-switcher.js` must be updated to keep the route map in sync.

---

## Verification

### Local preview

```bash
uv run --group dev zensical serve
```

### Build

```bash
uv run --group dev zensical build
```

!!! tip "Common issues"
    - If `zensical serve/build` does not start, first confirm that `zensical.toml` exists at the repo root.
    - If bilingual navigation diverges, inspect the navigation and language configuration in `zensical.toml`.

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Single Config SoT**: all site-level config and navigation changes go through `zensical.toml`
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: keep navigation and relative links aligned with the single config model
- **Architecture Term**: this repo uses `Native Single-Build Bilingual Pages`, not Separate Builds
- **Language Switch**: `extra.alternate` is site-level fallback; same-page switching depends on `docs/javascripts/language-switcher.js`
- **Verify**: `uv run --group dev zensical build` must pass
```
