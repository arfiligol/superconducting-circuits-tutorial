# Guardrails: Code Style & Quality

This document outlines the coding standards and best practices for the project.

## General Principles

We follow **[PEP 8](https://peps.python.org/pep-0008/)** for Python code style.

> **PEP 8** is Python's official style guide (the **standard**), while **Ruff** is the **tool** we use to automatically check and enforce these rules. See the [Toolchain section](#toolchain) for details.

## Clean Code Principles

We adopt principles from Robert C. Martin's *Clean Code*.

### 1. Naming
- **Functions**: Use **verbs** or **verb phrases** that clearly describe what the function does (e.g., `calculate_frequency`, `build_record`, `process_data`).
    - *Bad*: `squid_lc_frequency`, `y11_imaginary`, `process`
    - *Good*: `calculate_squid_lc_frequency`, `calculate_y11_imaginary`, `process_hfss_file`
- **Variables**: Use meaningful **nouns**.
- **Classes**: Use **nouns** or **noun phrases**.

### 2. Functions
- **Single Responsibility Principle (SRP)**: A function should do one thing, do it well, and do it only.
- **Small**: Functions should be small and focused.
- **Arguments**: Limit the number of arguments (aim for 3 or fewer). Use data classes/objects for larger groups of parameters.

## Clean Architecture Principles

We adopt **Clean Architecture** to ensure separation of concerns and maintainability.

### 1. Separation of Layers
- **Domain Layer** (`domain/`): Contains enterprise logic and entities (e.g., Pydantic schemas). No dependencies on outer layers.
- **Application Layer** (`application/`): Contains application specific business rules and use cases. Depends only on Domain.
- **Infrastructure Layer** (`infrastructure/`): Contains frameworks, drivers, and external interfaces (e.g., Visualization, File I/O). Depends on Application/Domain.

### 2. The Dependency Rule
Source code dependencies must point only **inward**, toward higher-level policies.
- Nothing in an inner circle (e.g., Domain) can know anything at all about something in an outer circle (e.g., Infrastructure).

## Type Hinting
- Use **Python 3.10+** syntax.
- Use `|` for Unions (e.g., `int | None` instead of `Optional[int]`).
- Use standard collections (`list`, `dict`, `tuple`) instead of `typing` module equivalents.

## Toolchain

The project uses automated tools to ensure code consistency and quality. For detailed information, see:

👉 **[Linting & Formatting Guardrails](./linting.md)**

### Quick Reference
- **Ruff**: Unified Linting & Formatting
- **Pre-commit**: Auto-check before Git commits
- **BasedPyright**: Type checking (Basic mode)

### Daily Usage
```bash
# Run all checks
uv run pre-commit run --all-files

# Manual Ruff execution
uv run ruff check .
uv run ruff format .
```

---

## Agent Rule { #agent-rule }

```markdown
## Code Style
- **Standard**: PEP 8 (enforced by Ruff).
- **Naming Conventions**:
    - **Physics**: `frequency_hz`, `inductance_ph`, `admittance_s` (Include units).
    - **Variables**: Noun (e.g., `component_record`).
    - **Functions**: Verb-Noun (e.g., `calculate_impedance`).
- **Clean Architecture**: `domain` <- `application` <- `infrastructure`.
- **Refactoring**: Prefer small, atomic changes.
- **Complexity**: Keep functions under 20 lines where possible.
```
