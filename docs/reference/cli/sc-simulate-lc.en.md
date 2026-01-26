---
aliases:
  - "sc-simulate-lc"
tags:
  - diataxis/reference
  - status/draft
  - topic/cli
---

---
aliases:
  - "sc-simulate-lc CLI"
tags:
  - topic/cli
  - topic/simulation
status: stable
owner: docs-team
audience: user
scope: "CLI reference for sc-simulate-lc"
version: v0.1.0
last_updated: 2026-01-24
updated_by: docs-team
---

# sc-simulate-lc

LC resonator simulation command line tool.

## Synopsis

```bash
sc-simulate-lc -L <inductance> -C <capacitance> [options]
```

## Description

Simulates a simple LC resonator circuit and calculates S11 parameters. Uses **JosephsonCircuits.jl** for Harmonic Balance analysis.

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-L`, `--inductance` | float | **Required** | Inductance (nH) |
| `-C`, `--capacitance` | float | **Required** | Capacitance (pF) |
| `--start` | float | 0.1 | Start frequency (GHz) |
| `--stop` | float | 10.0 | Stop frequency (GHz) |
| `--points` | int | 100 | Number of frequency points |
| `-o`, `--output` | path | None | Output JSON file path |
| `-v`, `--verbose` | flag | False | Detailed output |
| `-h`, `--help` | flag | - | Show help |

## Examples

### Basic Usage

```bash
# L=10nH, C=1pF, default frequency range
uv run sc-simulate-lc -L 10 -C 1
```

### Custom Frequency Range

```bash
# Narrower frequency range, more points
uv run sc-simulate-lc -L 10 -C 1 --start 1.0 --stop 3.0 --points 200
```

### Save Results to File

```bash
uv run sc-simulate-lc -L 10 -C 1 --output results/lc_sim.json
```

### Verbose Output

```bash
uv run sc-simulate-lc -L 10 -C 1 -v
```

## Output Format

### Standard Output

```
Simulating LC resonator: L=10.0 nH, C=1.0 pF
Frequency range: 0.1 - 10.0 GHz (100 points)

Expected resonance: 1.592 GHz
Simulation complete: 100 points
Resonance found at: 1.590 GHz
```

### JSON Output (--output option)

```json
{
  "metadata": {
    "inductance_nh": 10.0,
    "capacitance_pf": 1.0,
    "expected_resonance_ghz": 1.5915,
    "timestamp": "2026-01-24T12:00:00Z"
  },
  "results": {
    "frequencies_ghz": [0.1, 0.2, ...],
    "s11_real": [0.99, 0.98, ...],
    "s11_imag": [0.01, 0.02, ...]
  }
}
```

## Theory

The LC resonator's resonance frequency is:

$$
f_0 = \frac{1}{2\pi\sqrt{LC}}
$$

At resonance, S11 magnitude reaches its minimum value.

## Related Commands

- [Python API Guide](../../how-to/simulation/python-api.md) - API usage
- [LC Resonator Simulation](../../how-to/simulation/lc-resonator.md) - Tutorial
</Parameter>
<parameter name="Complexity">3
