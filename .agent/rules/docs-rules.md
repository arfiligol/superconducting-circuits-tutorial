---
trigger: model_decision
description: When we are discussing or handling about docs.
---

## Docs Rules
- **Architecture (Diataxis)**:
    - `tutorials/`: Learning-oriented (Step-by-step).
    - `how-to/`: Problem-oriented (Recipes).
    - `reference/`: Information-oriented (Specs).
    - `explanation/`: Understanding-oriented (Concepts).
- **Style**:
    - Language: Traditional Chinese (zh-TW).
    - **Bilingual**: Ensure all docs have both zh and en versions.
    - Keep technical terms in English (e.g., SQUID, Admittance).
- **Maintenance**:
    - **Sync**: Update Human Readable Doc -> MUST Update `.agent/rules/`.
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
