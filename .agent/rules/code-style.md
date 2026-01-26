---
trigger: always_on
---

## Code Style
- **Standard**: PEP 8 (enforced by Ruff).
- **Naming Conventions**:
    - **Physics**: `frequency_hz`, `inductance_ph`, `admittance_s` (Include units).
    - **Variables**: Noun (e.g., `component_record`).
    - **Functions**: Verb-Noun (e.g., `calculate_impedance`).
- **Clean Architecture**: `domain` <- `application` <- `infrastructure`.
- **Refactoring**: Prefer small, atomic changes.
- **Complexity**: Keep functions under 20 lines where possible.
