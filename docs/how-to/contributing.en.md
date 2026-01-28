---
aliases:
  - "How to Contribute"
tags:
  - diataxis/how-to
  - status/draft
---

# How to Contribute

Thank you for your interest in contributing to the Superconducting Circuits Tutorial!

This guide will help you set up your development environment and understand our workflow.

## 1. Environment Setup

We use `uv` for dependency management.

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### Installation

1.  **Fork the repository**:
    Go to the project page and click "Fork" to copy the repository to your own account.

2.  **Clone your fork**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/superconducting-circuits-tutorial.git
    cd superconducting-circuits-tutorial
    ```

3.  **Sync dependencies**:
    This will create a virtual environment and install all dependencies (including dev).
    ```bash
    uv sync
    ```

3.  **Activate virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

## 2. Development Workflow

### Running Tests
We use `pytest`.
```bash
uv run pytest
```

### Building Documentation
We use `mkdocs` with `material` theme.
```bash
uv run mkdocs serve
```
Access the site at `http://localhost:8000`.

> Need more customization? See the [MkDocs Official Documentation](https://www.mkdocs.org/).

### Submitting Changes (Pull Request)

1.  **Create a Branch**:
    ```bash
    git checkout -b feature/my-new-feature
    ```
2.  **Commit Changes**:
    ```bash
    git commit -m "feat: description of changes"
    ```
3.  **Push to Fork**:
    ```bash
    git push origin feature/my-new-feature
    ```
4.  **Open Pull Request**:
    Go to the original repository and click "Compare & pull request".

### Pre-commit Checks
Before submitting a Pull Request, please ensure:
1.  **Typing**: Code passes type checks (we use Python 3.12+ syntax).
2.  **Formatting**: Code is formatted (following PEP 8, checked via Ruff).
3.  **Tests**: All tests pass.

> For detailed code quality standards, see [Code Style Guardrails](../reference/guardrails/code-quality/code-style.md).

## 3. Coding Standards

Please refer to our **Reference** section for detailed standards:

- 👉 [Code Style & Principles](../reference/guardrails/code-quality/code-style.md) (Clean Code, Clean Arch)
- 👉 [Documentation Standards](../reference/guardrails/documentation-design/documentation.en.md) (Schemdraw, SVG)
- 👉 [Type Checking](../reference/guardrails/code-quality/type-checking.en.md)
- 👉 [Circuit Diagram Guide](./contributing/circuit-diagrams.md)
