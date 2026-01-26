---
trigger: model_decision
description: When doing task with CLI scripts.
---

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
