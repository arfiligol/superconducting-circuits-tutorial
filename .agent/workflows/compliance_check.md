---
description: Mandatory compliance check to run before and after every coding task
---

# Agent Compliance Protocol

This workflow codifies the "Lawyer Protocol" and "Core Engineering Principles" from Global Rules. You **MUST** follow this for every significant coding task.

## 1. PRE-FLIGHT CHECK (Before writing code)

1. **Scan Guardrails**:
   - Run `ls docs/reference/guardrails/` to see available laws.
   - **READ** the specific guardrail file relevant to your task (e.g., `documentation.md`, `python-scripts.md`, `tech-stack.md`).
   - *DO NOT assume you know the rules. Read them.*

2. **Check Context**:
   - Verify `task.md` exists and is up to date.
   - If modifying an existing system, READ the relevant `sot` (Source of Truth) document first.

## 2. EXECUTION STANDARDS

1. **Single Source of Truth**:
   - If you hit a conflict between Code and Docs, **STOP**.
   - Ask the user: "Update Code to match Docs?" or "Amend Docs to match Code?".
   - *NEVER* silently modify the SoT to fit a violation.

2. **Atomic Changes**:
   - Do not mix refactoring with feature work.
   - Do not mix formatting fixes with logic changes.

## 3. LANDING CHECK (Before commit)

1. **Self-Correction**:
   - Did you violate any constraints read in Step 1?

2. **Automated Verification**:
   - **MUST RUN**: `uv run pre-commit run --all-files`
   - Fix *all* linter errors found. Do not bypass.

3. **Documentation Sync**:
   - If you modified `.md` files, did you update the bilingual counterpart (`.en.md`)?
   - If you modified code, did you update the docstrings/docs?

4. **Commit**:
   - Use standard format: `type: description`.
   - Ensure the commit message is truthful.
