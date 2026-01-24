---
aliases:
  - "Script Authoring Rules"
tags:
  - boundary/system
  - audience/team
  - sot
status: stable
owner: docs-team
audience: team
scope: "CLI Script Authoring Rules: Location, Entry Points, Documentation"
version: v0.1.0
last_updated: 2026-01-12
updated_by: docs-team
---

# Script Authoring

CLI script authoring standards.

## Location

Place tool scripts in `src/scripts/`:

```
src/scripts/
├── admittance_fit.py
├── flux_dependence_plot.py
└── ...
```

## Entry Points

Register entry points in `pyproject.toml`:

```toml
[project.scripts]
squid-model-fit = "src.scripts.admittance_fit:run_no_ls"
flux-dependence-plot = "src.scripts.flux_dependence_plot:run"
```

## Execution

Scripts must be executable as modules:

```bash
uv run python -m src.scripts.admittance_fit
```

## Help Message

Implement `--help` description:

```python
parser = argparse.ArgumentParser(
    description="Fit SQUID LC model to admittance data",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
```

## Documentation

When adding a new script:
1. Add a page in [CLI Reference](../cli/index.md)
2. Add a guide in [How-to](../../how-to/index.md) section
3. Update README.md (if necessary)

## Related

- [Data Handling](data-handling.md) - Output path rules
- [CLI Reference](../cli/index.md) - Command reference

---

## Agent Rule { #agent-rule }

```markdown
## Script Authoring
- **Location**: `src/scripts/`
- **Naming**: `kebab-case` (e.g. `sc-convert-hfss`).
- **Structure**:
    - MUST have `def main():`.
    - MUST use `argparse` for arguments.
    - MUST use `if __name__ == "__main__": main()`.
- **Logic**: CLI scripts should be minimal wrappers around `sc_analysis` logic.
- **I/O**: Print to stdout is allowed here (and only here).
```
