# SQUID JPA Analysis Pipeline

Automated analysis pipeline for SQUID JPA (Josephson Parametric Amplifier) simulation and measurement data.

## Documentation

Full documentation is available in the `docs/` directory:

- **[Getting Started](docs/tutorials/getting-started.md)**: First time setup and analysis.
- **[How-to Guides](docs/how-to/index.md)**: Step-by-step guides for common tasks.
- **[Explanation](docs/explanation/index.md)**: Physics background and pipeline design.
- **[Reference](docs/reference/index.md)**: CLI commands and data formats.

## Quick Start

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Validate environment**
   ```bash
   uv run python main.py
   ```

3. **Explore documentation**
   Start at **[docs/index.md](docs/index.md)**.

## Project Structure

- `src/`: Source code (extraction, models, fitting, visualization).
- `data/`: Data storage (structure defined in [Data Layout](docs/reference/data-formats/raw-data-layout.md)).
- `docs/`: Everything you need to know.

## Contribution

Please read the **[Guardrails](docs/reference/guardrails/index.md)** before contributing. It covers:
- Type Checking (BasedPyright)
- Code Style (Ruff)
- Data Handling Rules
