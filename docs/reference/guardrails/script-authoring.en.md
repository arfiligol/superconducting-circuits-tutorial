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
1. Add a corresponding page in [[../cli/index.md|CLI Reference]]
2. Add a user guide in the corresponding [[../../how-to/index.md|How-to]] section
3. Update README.md (if necessary)

## Related

- [[./data-handling.md|Data Handling]] - Output path rules
- [[../cli/index.md|CLI Reference]] - command reference
