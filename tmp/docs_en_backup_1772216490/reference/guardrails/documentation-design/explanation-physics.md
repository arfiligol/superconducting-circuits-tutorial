---
aliases:
  - "Explanation Physics Guardrail"
tags:
  - diataxis/reference
  - audience/team
  - sot/true
  - topic/documentation
  - topic/physics
status: stable
owner: docs-team
audience: team
scope: "Writing position, chapter skeleton, and cross-linking rules for Explanation/Physics"
version: v0.2.0
last_updated: 2026-02-16
updated_by: docs-team
---

# Explanation Physics

This file defines the writing framework for `docs/explanation/physics/`, so it works as both a full start-to-end learning path and a set of reusable conceptual nodes.

---

## Teaching Position (Both Required)

1. **Backbone course**
   - Build from core physics to superconducting quantum-circuit engineering context.
   - Target readers: physics students who completed the four core physics courses and need bridge/review support.
2. **Reusable nodes**
   - Each page can be referenced independently by Tutorial / How-to / Reference pages.
   - Readers can enter from the middle without reading the whole sequence first.

!!! warning "Diataxis Boundary"
    Explanation answers "why/how to understand," not command-style procedures (those belong to How-to/Tutorials).

## Physics Q&A First

- Every Physics page must open with a **physics question** as the title or leading framing.
- The core question must be causal and conceptual, not operational ("how to run tool X").
- Engineering content should be used as mapping context, not as the main narrative axis.

!!! tip "History/Application Prompt"
    Each page should include at least one admonition that states what historical community problem this concept helped solve, or where it is classically applied.

---

## Start Point and Depth Boundary

### Fixed Start Point

- Start superconductivity sections from: **a single superconductor can be described by one macroscopic wavefunction**.
- Order-parameter notation is allowed, but phase/amplitude meanings must be explicit.

### Boundary (Avoid Over-expansion)

- Do not require full BCS or condensed-matter field-theory derivations.
- Include the minimum physics chain needed for engineering models:
  1. Macroscopic wavefunction/phase
  2. Josephson relations
  3. Circuit equivalent (L/C/nonlinear term)
  4. Measurable engineering quantities (frequency, impedance, noise, gain, sensitivity, etc.)

---

## Chapter Contract (Physics Sub-pages)

Each `docs/explanation/physics/*.md` page should follow this skeleton:

1. **Question this page answers**: define one core question in 1–2 sentences.
2. **Prerequisite mapping**: map required ideas back to the four core physics subjects.
3. **Physics core**: present minimum equations and assumptions; define all symbols; keep units consistent.
4. **Engineering mapping**: map physical quantities to circuit/system design quantities.
5. **Limits and approximations**: state validity range and failure conditions.
6. **Cross-document navigation**: provide 1-3 follow-up links by relevance (Tutorial, How-to, Reference, or Design Decisions; no mandatory combination).

---

## Global Narrative Path (Consistency Requirement)

Maintain a shallow-to-deep path in `Explanation/Physics`:

1. Macroscopic superconducting description (single-superconductor wavefunction)
2. Josephson element and source of nonlinearity
3. Circuit model, resonance, and parametric coupling
4. Measurement models (S/Z/Y, resonance extraction, noise/gain)
5. Interfaces to real engineering workflows (calibration, design tradeoffs, operating point)

When adding a page, state where it sits in this path and provide prev/next conceptual links.

---

## Mid-stream Entry Rules

Each Physics Explanation page should include:

- **You can start here if...**: a short prerequisite checklist
- **If you need background first...**: 1-3 backfill links
- **If you just need to do the task...**: links to corresponding Tutorial/How-to pages

---

## Relationship to Other Diataxis Types

- `Explanation`: builds conceptual understanding (why/how it works)
- `Tutorials`: guided practice across the learning path
- `How-to`: single-task execution
- `Reference`: verifiable specs, formulas, CLI, data formats

Physics Explanation must remain:

- Standalone readable (conceptually complete)
- Externally referencable (clear node boundaries)

---

## Agent Rule { #agent-rule }

```markdown
## Explanation Physics
- **Positioning**: `docs/explanation/physics/` must be both a full learning backbone and reusable concept nodes
- **Audience**: physics students with four-core-physics background; support bridging + review
- **Start point**: begin superconductivity from a single-superconductor macroscopic wavefunction
- **Depth boundary**: no full BCS derivation; include minimum chain: wavefunction/phase -> Josephson relations -> circuit equivalent -> measurable engineering quantities
- **Per-page contract**: question, prerequisites mapping, physics core equations/assumptions, engineering mapping, limits/approximations, cross-links
- **Cross-links**: provide 1-3 relevant links chosen by concept fit (Tutorial/How-to/Reference/Design Decisions); no mandatory pair
- **Narrative consistency**: place each page in the global path and maintain prev/next conceptual links
- **Diataxis boundary**: Explanation explains reasoning, not command-style procedures
- **Question-driven**: each page starts from a physics question, not an engineering operation question
- **Admonition usage**: include at least one history/application admonition per page
```
