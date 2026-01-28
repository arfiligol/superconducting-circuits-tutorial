---
aliases:
  - "Documentation Standards"
tags:
  - diataxis/reference
  - status/draft
  - topic/governance
---

# Documentation Standards

This document is the single source of truth for writing and maintaining project documentation. We follow the **Diataxis** framework with strict formatting and style guidelines.

## 1. Architecture (Diataxis)

We use the [Diataxis](https://diataxis.fr/) framework to categorize all documentation:

| Category | Directory | Goal | Orientation | Content |
|----------|-----------|------|-------------|---------|
| **Tutorials** | `docs/tutorials/` | Learning | Guided | Step-by-step teaching with achievable outcomes |
| **How-to** | `docs/how-to/` | Problem-solving | Practical | Recipes for specific problems. Steps only, no theory. |
| **Reference** | `docs/reference/` | Information | Technical | API specs, parameters, formats. Precise and concise. |
| **Explanation** | `docs/explanation/` | Understanding | Theoretical | Background, design decisions, physics. Explains "Why". |

## 2. Style Guide

- **Language (Bilingual Policy)**:
    - **All docs must have both zh and en versions** (via i18n plugin).
    - Core content is written in **Traditional Chinese (zh-TW)**, with synchronized `.en.md` files.
    - Keep technical terms in English (e.g., `SQUID`, `Admittance`).
- **Tone**:
    - **Tutorials**: Encouraging, guiding ("Now let's try...")
    - **Reference**: Objective, neutral ("This parameter controls...")
    - **How-to**: Direct, imperative ("Run the following command...")

## 3. Maintenance

- **Guardrails as Single Source of Truth**: Files in `docs/reference/guardrails/` are the **only source of truth** for both human developers and AI agents. No separate `.agent/rules/` directory maintenance required.
- **Bilingual Sync**: When modifying any `.md` file, **you MUST also update the corresponding `.en.md` file** to keep both versions consistent.
- **Commit**: Use `docs:` type for documentation updates.

## 4. Formatting

### Frontmatter Schema

All `.md` files must include YAML frontmatter that conforms to this specification.

#### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `aliases` | `list[str]` | Alternative names for search and redirects. At least one descriptive name required. | `["LC Resonator Tutorial", "LC 諧振器教學"]` |
| `tags` | `list[str]` | Classification tags for management and filtering. Must follow the **Tags Taxonomy** below. | `["diataxis/tutorial", "status/stable"]` |

#### Optional Fields (Automation)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `owner` | `str` | Document owner or team. Defaults to Git History author. | `"docs-team"` |
| `last_updated_by` | `str` | Last modifier (recommended: CI auto-update). | `"arfiligol"` |
| `last_updated` | `str` | Last update date `YYYY-MM-DD` (recommended: CI auto-update). | `"2026-01-27"` |

!!! warning "Name Validation Rule"
    **All names** in `owner` and `last_updated_by` **MUST exist in the [Contributors Registry](../contributors.en.md)**. Add new contributors to the registry before referencing them.

#### Tags Taxonomy

All tags use `namespace/value` format for consistency and manageability.

| Namespace | Description | Valid Values |
|-----------|-------------|--------------|
| `diataxis` | Document type (per Diataxis framework) | `tutorial`, `how-to`, `reference`, `explanation` |
| `status` | Document maturity status | `draft`, `incubating`, `stable`, `deprecated` |
| `audience` | Target reader | `user`, `contributor`, `maintainer` |
| `sot` | Source of Truth marker | `true` (This doc is the authoritative source for this topic) |
| `topic` | Topic area (customizable, but keep consistent) | `simulation`, `analysis`, `physics`, `cli`, `data-format`, ... |

**Example Frontmatter**:

```yaml
---
aliases:
  - "LC Resonator Simulation Tutorial"
  - "LC 共振器模擬教學"
tags:
  - diataxis/tutorial
  - status/stable
  - audience/user
  - topic/simulation
---
```

!!! tip "Tag Usage Principles"
    - Every document needs at least `diataxis/*` and `status/*` tags.
    - `topic/*` can be freely added based on content, but prefer existing topic values for consistency.

### Links

- **Internal**: Use standard Markdown `[Display Text](path/to/file.md)`.
- **External**: Use standard Markdown `[Display Text](url)`.
- **Images**: Use `![Alt](../assets/image.png)` (store images in `docs/assets/`).

### Admonitions

Use MkDocs Material syntax:

!!! warning "Syntax Note"
    **Do NOT use** GitHub style `> [!NOTE]`. MkDocs cannot render it.

**Correct syntax**:

```markdown
!!! note "Title (optional)"
    Content must be indented 4 spaces.
    Can have multiple lines.
```

**Collapsible version** (use `???`):

```markdown
??? tip "Click to expand"
    Hidden content.
```

**Supported types**: `note`, `tip`, `warning`, `danger`, `info`, `example`

### Math

- Inline: `$E = mc^2$`
- Block: `$$ \Phi_0 = \frac{h}{2e} $$`

### Code

Always specify the language:

```python
def hello():
    print("Hello")
```

## 5. Special Sections

Some topics have dedicated rules or maintenance workflows. Always consult the relevant page first.

### Visuals

- **Circuit Diagrams**: Must use **Schemdraw** (Python) to generate SVG.
    - See: [Circuit Diagram Guide](../../../how-to/contributing/circuit-diagrams.md)
- **Flowcharts**: Use Mermaid.
    ```mermaid
    graph TD;
        A-->B;
    ```

### CLI Options

CLI Reference pages follow a **hybrid model**:

- **Hand-written**: purpose, examples, and notes (readability first).
- **Auto-generated**: help block generated by `sc-docs-cli`, synced by `sc-docs-cli-sync`.
- **Consistency check**: use `sc-docs-cli-sync --check`.

See: [CLI Docs Automation](cli-docs-automation.en.md)

---

## Agent Rule { #agent-rule }

```markdown
## Docs Rules
- **Architecture (Diataxis)**:
    - `tutorials/`: Learning-oriented (Step-by-step).
    - `how-to/`: Problem-oriented (Recipes).
    - `reference/`: Information-oriented (Specs).
    - `explanation/`: Understanding-oriented (Concepts).
- **Style**:
    - Language: Traditional Chinese (zh-TW).
    - **Bilingual**: Ensure all docs have both zh and en versions. When updating one, MUST update the other.
    - Keep technical terms in English (e.g., SQUID, Admittance).
- **Maintenance**:
    - **Single Source of Truth**: `docs/reference/guardrails/` is the only source for both human devs and AI agents. No separate `.agent/rules/` sync needed.
    - **Bilingual Sync**: When modifying `.md`, MUST update corresponding `.en.md` (and vice versa).
- **Formatting**:
    - Frontmatter: Required (aliases, tags, owner).
    - Links: Use Standard Markdown `[Label](path)`.
    - Math: Use `$$ ... $$` for blocks.
    - Code: Always specify language (e.g., `python`, `julia`).
    - **Admonitions**: Use MkDocs Material syntax only.
        - Correct: `!!! note "Title"` with 4-space indented content.
        - WRONG: `> [!NOTE]` (GitHub style, not supported).
        - Types: `note`, `tip`, `warning`, `danger`, `info`, `example`.
- **Visuals**:
    - Circuits: Use Schemdraw (Python) SVG only.
    - Flows: Use Mermaid.
```
