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
version: v0.2.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Script Authoring

CLI script authoring standards.

## Location

Place tool scripts in `src/scripts/`, organized by function:

```
src/scripts/
├── analysis/              # Analysis scripts
│   ├── admittance_fit.py
│   └── flux_dependence_plot.py
└── simulation/            # Simulation scripts
    └── run_lc.py
```

## Entry Points

Register entry points in `pyproject.toml`:

```toml
[project.scripts]
# Analysis
sc-fit-squid = "scripts.analysis.admittance_fit:run_no_ls"
flux-dependence-plot = "scripts.analysis.flux_dependence_plot:run"

# Simulation
sc-simulate-lc = "scripts.simulation.run_lc:main"
```

## Execution

Scripts must be executable as modules:

```bash
uv run python -m scripts.analysis.admittance_fit
uv run python -m scripts.simulation.run_lc
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
- [Folder Structure](folder-structure.md) - Directory structure

---

## Agent Rule { #agent-rule }

```markdown
## Script Authoring
- **Location**:
    - Analysis scripts: `src/scripts/analysis/`
    - Simulation scripts: `src/scripts/simulation/`
- **Naming**: `kebab-case` (e.g. `sc-simulate-lc`, `sc-fit-squid`).
- **Structure**:
    - MUST have `def main():`.
    - MUST use `argparse` for arguments.
    - MUST use `if __name__ == "__main__": main()`.
- **Logic**:
    - Analysis CLI: minimal wrappers around `core/analysis` logic.
    - Simulation CLI: minimal wrappers around `core/simulation` logic.
- **I/O**: Print to stdout is allowed here (and only here).
```
