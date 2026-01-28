---
aliases:
  - "Extend Julia Functions"
tags:
  - diataxis/how-to
  - status/draft
  - topic/extension
---

---
aliases:
  - "Extend Julia Functions"
tags:
  - topic/extend
  - topic/contributing
  - topic/julia
status: stable
owner: docs-team
audience: contributor
scope: "Contributor guide: Extend Julia simulation functions"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# Extend Julia Functions

This guide explains how to add new Julia simulation functions and wrap them for Python usage.

## Architecture Overview

```
Python                    JuliaCall                Julia
┌─────────────────┐       ┌─────────────┐         ┌─────────────────────┐
│ CLI Script      │       │             │         │ hbsolve.jl          │
│ (run_lc.py)     │──────▶│  juliacall  │────────▶│ run_lc_simulation() │
├─────────────────┤       │             │         └─────────────────────┘
│ JuliaSimulator  │       │             │                   │
│ (julia_adapter) │◀──────│  Main       │◀──────────────────┘
├─────────────────┤       └─────────────┘         ┌─────────────────────┐
│ Domain Models   │                               │ JosephsonCircuits.jl│
│ (circuit.py)    │                               └─────────────────────┘
└─────────────────┘
```

## Step 1: Add Julia Function

Edit `src/core/simulation/infrastructure/hbsolve.jl`:

```julia
"""
    run_my_simulation(param1, param2, ...)

Description of the new function.

# Arguments
- `param1`: Description of parameter 1
- `param2`: Description of parameter 2

# Returns
Dict with keys: :frequencies_ghz, :s11_real, :s11_imag
"""
function run_my_simulation(param1::Float64, param2::Float64)
    # Unit conversion (if needed)
    nH = 1e-9
    pF = 1e-12
    GHz = 1e9

    # Define circuit
    @variables L C R50
    circuit = [
        ("P1", "1", "0", 1),
        # ... circuit definition
    ]

    circuitdefs = Dict(
        L => param1 * nH,
        C => param2 * pF,
        R50 => 50.0,
    )

    # Frequency setup
    frequencies = range(0.1, 10, length=100) .* GHz
    ws = 2π .* frequencies

    # Pump setup
    wp = (2π * 5GHz,)
    sources = [(mode=(1,), port=1, current=0.0)]

    # Run simulation
    sol = hbsolve(ws, wp, sources, (10,), (20,), circuit, circuitdefs)

    # Extract S11
    S11 = sol.linearized.S(
        outputmode=(0,), outputport=1,
        inputmode=(0,), inputport=1,
        freqindex=:
    )

    # Return Dict (will be converted to Python dict)
    return Dict(
        :frequencies_ghz => collect(frequencies ./ GHz),
        :s11_real => real.(S11),
        :s11_imag => imag.(S11)
    )
end
```

!!! important
    - Functions must return `Dict` with Symbol keys
    - Use `collect()` to convert arrays to Julia Array
    - Do not use `const` inside functions (Julia doesn't allow const in function blocks)

## Step 2: Add Pydantic Domain Model (If Needed)

If the new function needs new input/output structures, edit `src/core/simulation/domain/circuit.py`:

```python
from pydantic import BaseModel

class MySimulationConfig(BaseModel):
    """New simulation configuration."""

    param1: float
    param2: float
    # ... other parameters

class MySimulationResult(BaseModel):
    """New simulation result."""

    frequencies_ghz: list[float]
    s11_real: list[float]
    s11_imag: list[float]
    # ... other outputs
```

## Step 3: Update Python Adapter

Edit `src/core/simulation/infrastructure/julia_adapter.py`:

```python
from core.simulation.domain.circuit import (
    FrequencyRange,
    SimulationResult,
    MySimulationConfig,  # New
)

class JuliaSimulator:
    # ... existing methods ...

    def run_my_simulation(
        self,
        config: MySimulationConfig,
        freq_range: FrequencyRange,
    ) -> SimulationResult:
        """
        Run custom simulation.

        Args:
            config: Simulation configuration.
            freq_range: Frequency range.

        Returns:
            SimulationResult with S11 data.
        """
        self._ensure_initialized()
        assert self._jl is not None

        # Call Julia function
        result = self._jl.run_my_simulation(
            float(config.param1),
            float(config.param2),
        )

        # Convert result
        return SimulationResult(
            frequencies_ghz=list(result["frequencies_ghz"]),
            s11_real=list(result["s11_real"]),
            s11_imag=list(result["s11_imag"]),
        )
```

!!! tip
    - Use `assert self._jl is not None` to satisfy the type checker
    - Julia returns Dict with Symbol keys, but JuliaCall automatically converts them to Python str

## Step 4: Add CLI Entry Point

Create `src/scripts/simulation/run_my_simulation.py`:

```python
"""CLI for my custom simulation."""

import argparse
import sys

from core.simulation.infrastructure.julia_adapter import JuliaSimulator
from core.simulation.domain.circuit import FrequencyRange


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run my custom simulation",
    )
    parser.add_argument("--param1", type=float, required=True)
    parser.add_argument("--param2", type=float, required=True)
    parser.add_argument("--start", type=float, default=0.1)
    parser.add_argument("--stop", type=float, default=10.0)
    parser.add_argument("--points", type=int, default=100)

    args = parser.parse_args()

    print(f"Running simulation: param1={args.param1}, param2={args.param2}")

    simulator = JuliaSimulator()
    freq_range = FrequencyRange(
        start_ghz=args.start,
        stop_ghz=args.stop,
        points=args.points,
    )

    # Use new function
    result = simulator.run_my_simulation(
        config=MySimulationConfig(
            param1=args.param1,
            param2=args.param2,
        ),
        freq_range=freq_range,
    )

    print(f"Simulation complete: {len(result.frequencies_ghz)} points")


if __name__ == "__main__":
    main()
```

## Step 5: Register CLI Entry Point

Update `pyproject.toml`:

```toml
[project.scripts]
# ... existing scripts ...
sc-my-simulation = "scripts.simulation.run_my_simulation:main"
```

## Step 6: Test

```bash
# Type checking
uv run basedpyright src/core/simulation/

# Run test
uv run sc-my-simulation --param1 10.0 --param2 1.0
```

## Step 7: Update Documentation

1. Add CLI reference page in `docs/reference/cli/`
2. Update relevant tutorials in `docs/how-to/simulation/`
3. Update README.md (if needed)

## Common Issues

### Julia Syntax Error

**Problem**: `syntax: unsupported 'const' declaration on local variable`

**Solution**: Julia doesn't allow `const` inside functions. Use regular variable assignment instead.

### Type Conversion

| Python Type | Julia Type |
|-------------|------------|
| `float` | `Float64` |
| `int` | `Int` |
| `list` | `Vector` |
| `dict` | `Dict` |

### Performance Considerations

For computationally intensive operations (like parameter sweeps), implement the complete logic in Julia rather than repeatedly calling from Python.

## Related Resources

- [Script Authoring](../../reference/guardrails/code-quality/script-authoring.en.md) - CLI standards
- [Folder Structure](../../reference/guardrails/project-basics/folder-structure.en.md) - Directory structure
- [Python API Guide](../simulation/python-api.md) - API usage
