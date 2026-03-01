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
version: v0.2.0
last_updated: 2026-02-27
updated_by: docs-team
---

# Documentation Maintenance

This page defines maintenance rules (bilingual sync, update rules, verification checklist).

---

## Bilingual Sync (required)

This project uses **Separate Builds**:

- zh: `path/to/page.md`
- en: `path/to/page.en.md`

Build configs:

- zh site: `zensical.yml`
- en site: `zensical.en.yml`

Language switching:

- use Zensical-native `extra.alternate` links between the two sites.

!!! info "Source layout vs build input"
    Source files stay as `.md` + `.en.md` side-by-side for authoring parity.
    For EN builds, CI prepares `docs_en/` and renames `.en.md` to `.md` before running `zensical.en.yml`.

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

1. Update BOTH `zensical.yml` and `zensical.en.yml` `nav:` to keep structures symmetric
2. Check all relative links (inside `.en.md`, target `.md` paths to stay valid after `docs_en` renaming)
3. If the page is SoT, ensure `tags` includes `sot/true`

---

## Verification

### Local preview

```bash
# zh preview
uv run --group dev zensical serve -f zensical.yml

# prepare EN build input
cp -a docs docs_en
find docs_en -depth -name "*.en.md" -exec sh -c 'mv "$1" "${1%.en.md}.md"' _ {} \;

# en preview (optional)
uv run --group dev zensical serve -f zensical.en.yml
```

### Build

```bash
# zh build
uv run --group dev zensical build -f zensical.yml

# en build (requires prepared docs_en)
cp -a docs docs_en
find docs_en -depth -name "*.en.md" -exec sh -c 'mv "$1" "${1%.en.md}.md"' _ {} \;
uv run --group dev zensical build -f zensical.en.yml
```

!!! tip "Common issues"
    - If EN links look wrong, regenerate `docs_en` from the latest `docs/`.
    - If bilingual navigation diverges, diff `nav` blocks in `zensical.yml` and `zensical.en.yml`.

---

## Agent Rule { #agent-rule }

```markdown
## Documentation Maintenance
- **Bilingual sync**: `.md` changes require matching `.en.md` changes (and vice versa)
- **Separate Configs**: Nav/site-config changes MUST be applied to BOTH `zensical.yml` and `zensical.en.yml`
- **Frontmatter**: update `last_updated` and `updated_by` on content changes
- **Versioning**: patch/minor/major bumps for doc changes
- **Nav/links**: keep both nav trees symmetric and fix relative links
- **EN link target**: links inside `.en.md` should target `.md` paths for `docs_en` compatibility
- **Verify**: both `zensical.yml` and `zensical.en.yml` builds must pass
```
