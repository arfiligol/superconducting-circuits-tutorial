# Guardrails: Documentation Standards

This document outlines the standards for writing and maintaining project documentation.

## Circuit Diagrams

We use **Schemdraw** (Python) to generate all circuit diagrams, ensuring consistent style and maintainability.

### Requirements
- **Format**: SVG (vector graphics, scalable)
- **Source Code**: Must include Schemdraw code for future modifications

### Detailed Tutorial
For a complete guide on creating circuit diagrams, see:

👉 **[Circuit Diagram Contributing Guide](../../how-to/contributing/circuit-diagrams.md)**

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
    - Keep technical terms in English (e.g., SQUID, Admittance).
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

