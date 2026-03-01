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
version: v0.6.0
last_updated: 2026-03-01
updated_by: docs-team
---

# Documentation Maintenance

This page defines maintenance rules (bilingual sync, update rules, verification checklist).

---

## Bilingual Sync (required)

This project uses **native Separate Builds**:

- config files: `zensical.toml` (zh-TW) and `zensical.en.toml` (en)
- primary editable source tree: `docs/docs_zhtw/`
- English counterpart tree: `docs/docs_en/`
- site output: `docs/site/` (zh-TW) and `docs/site/en/` (en)

!!! info "Native Zensical standard"
    Documentation standards now align with native Zensical TOML configs.
    The old YAML setup is no longer valid, and MkDocs i18n plugins are not part of this architecture.

!!! warning "Sync rules"
    - Daily edits start in `docs/docs_zhtw/`
    - Content changes must be mirrored into the matching page in `docs/docs_en/`
    - Delete/move: update both versions and fix all incoming links
    - If the repo still contains legacy mirrored files under `docs/`, treat them as reference copies only, not the active build source

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

From a documentation-maintenance perspective, the move to native Separate Builds requires four aligned updates:

1. All maintenance guidance must clearly distinguish `zensical.toml` (zh-TW) and `zensical.en.toml` (en).
2. All navigation rules must require synchronized `nav` updates in both native TOML configs.
3. Documentation edits start in `docs/docs_zhtw/` and are then mirrored into `docs/docs_en/`.
4. README, CI guidance, and contributing docs must use the same workflow so contributors do not fall back to an obsolete staging-tree model.

---

## Navigation and Link Hygiene

When adding/moving pages:

1. Update navigation and site-level settings in both `zensical.toml` and `zensical.en.toml`
2. Check all relative links (including `.en.md` counterparts)
3. If the page is SoT, ensure `tags` includes `sot/true`

---

## Native Separate Builds

The formal name of this project's current architecture is:

- `Native Separate Builds`

Its technical shape is:

- two native configs: `zensical.toml` (zh-TW) and `zensical.en.toml` (en)
- two maintained source trees: `docs/docs_zhtw/` and `docs/docs_en/`
- two builds that emit `docs/site/` and `docs/site/en/`

!!! info "Same-page switching"
    Under `Native Separate Builds`, native Zensical `extra.alternate` still defines site-level locale roots.
    To keep the same relative path when switching languages, this project loads `docs/javascripts/language-switcher.js` via native `extra_javascript` and rewrites the selector between `/` and `/en/`.

!!! warning "Scope and limits"
    - Do not assume automatic fallback for untranslated pages; add the matching page in `docs/docs_en/` when route symmetry matters.
    - If the locale roots ever change (for example, not using `/en/` anymore), update both `extra.alternate` and `docs/javascripts/language-switcher.js`.
    - If navigation changes, both TOML configs must be updated together or the two sidebars will drift.

---

## Verification

### Local preview

```bash
uv run --group dev zensical serve -f zensical.toml
uv run --group dev zensical serve -f zensical.en.toml -a localhost:8001
```

### Build

```bash
uv run --group dev zensical build -f zensical.toml
uv run --group dev zensical build -f zensical.en.toml

# Or use the canonical static-build wrapper (if still kept in the repo)
./scripts/build_docs_sites.sh
```

!!! tip "Common issues"
    - If `zensical serve/build` does not start, confirm that both `zensical.toml` and `zensical.en.toml` exist at the repo root.
    - If build fails because a page is missing, confirm the change was made in `docs/docs_zhtw/` / `docs/docs_en/` and not only under the legacy `docs/` root.
    - If bilingual navigation diverges, first confirm that both TOML `nav` blocks still match.

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Docs Source**: edit `docs/docs_zhtw/` first, then mirror the same change into `docs/docs_en/`
- **No Staging Assumption**: `docs/docs_zhtw/` and `docs/docs_en/` are maintained source trees for the docs site
- **Config SoT**: site-level config is split across `zensical.toml` and `zensical.en.toml`
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: keep navigation and relative links aligned across both native configs
- **Architecture Term**: this repo uses `Native Separate Builds`
- **Language Switch**: `extra.alternate` defines locale roots; same-page switching depends on `docs/javascripts/language-switcher.js`
- **Verify**: `uv run --group dev zensical build -f zensical.toml` and `uv run --group dev zensical build -f zensical.en.toml` must pass
```
