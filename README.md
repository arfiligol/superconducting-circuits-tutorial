# JPA Circuit Model Simulations

This repository collects reusable experiments for studying Josephson qubits, readout resonators, and supporting microwave structures with [`JosephsonCircuits.jl`](https://github.com/QICKLab/JosephsonCircuits.jl).  The `circuit_model_analysis` directory contains the circuits you previously explored (floating qubits, resonator coupling, LC tanks, transmission lines, symbolic derivations, etc.), while the `JPACircuitModelSim` module (`src/`) centralizes the small set of helpers you need while running simulations (consistent PlotlyJS plotting plus utilities to persist DataFrames back into `data/`).  The goal of the repo is to make each study reproducible, to expose helpers that future scripts (or AIs) can call, and to eventually expose a CLI entry point so simulations can be launched with a single command similar to `uv run <model>`.

## Repository layout

- `Project.toml` / `Manifest.toml` — Julia environment that pins `JosephsonCircuits.jl`, PlotlyJS, CSV/DataFrames, Symbolics, etc.  Every command in this README assumes `--project=.` is active.
- `src/` — home of the `JPACircuitModelSim` module.  It exposes `ili_plot`, the model registry API (`register_model!`, `run_model`), project paths (`src/utils/Paths.jl`), and lightweight utilities (`src/utils/DataExport.jl`) for saving simulation DataFrames back under `data/`.
- `data/` — raw and processed artifacts (ignored by git): `data/raw/admittance` for HFSS exports, `data/raw/phase` reserved for future work, `data/processed/reports` for fit summaries.  `Paths.ensure_data_dirs!()` (called on module load) guarantees the folders exist.
- `circuit_model_analysis/` — individual experiments.  Each file sets up components with `@variables`, sweeps frequencies via `hbsolve`, and post-processes the linearized impedance/admittance matrices.
  - `floating_1Q_coupled_XY*.jl` — floating qubit examples with XY lines; one variant extracts admittance matrices and another plots S-parameters.
  - `floating_1Q_coupled_Readout.jl` — extends the qubit to include a readout resonator and provides a `solve_circuit` helper for scripted sweeps.
  - `port_on_LC_oscillator.jl` — demonstrates a parameter sweep over SQUID inductance, writes CSV summaries, and uses `ili_plot` to batch traces.
  - `transmission_line*.jl`, `grounding_1Q*.jl`, `hang_a_LC_*` — additional harmonic-balance studies for coupling networks, grounding strategies, and component extraction.
  - `symbolics_model_analysis/single_floating_qubit_coupled_via_xy_line.jl` — Symbolics.jl derivation of the capacitance matrix and mode transform used in the floating-qubit scripts.
  - `*.csv` — HFSS/Q3D exports (capacitance matrices, port admittances) that seed the numerical definitions inside the simulations.
- `models/` — the new home for production-ready circuit definitions.  Each file should define a `run_*` function and call `register_model!` (see `models/README.md` for a template).
- `utils.jl` — superseded by the code that now lives in `src/Plotting.jl`.  Continue extending the helper inside the module so every consumer can `using JPACircuitModelSim: ili_plot`.  Legacy scripts can still `include("../utils.jl")`.
- `build/log` — scratch artifacts (safe to ignore unless you are debugging).

## Getting started

### 1. Activate / install the Julia environment

```bash
cd /Users/arfiligol/Codes/DataAnalysis/Simulation/JPA-CircuitModel-Sim
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

`instantiate` will download all packages into the global `~/.julia` cache, so every project can have its own `Project.toml` without duplicating package storage (similar to `uv`’s shared cache).

### 2. Run an existing model

*Direct script run (closest to `uv run <model>` for now):*

```bash
julia --project=. circuit_model_analysis/port_on_LC_oscillator.jl
```

*REPL-driven when you want to reuse functions interactively:*

```julia
julia --project=.
julia> using JPACircuitModelSim
julia> include("circuit_model_analysis/floating_1Q_coupled_XY.jl")
```

*Extract-only, useful for headless exports:*

```bash
julia --project=. -e 'include("circuit_model_analysis/floating_1Q_coupled_Readout.jl");
                      sol = solve_circuit(circuit, circuitdefs, 4.0, 5.5, 0.01);
                      println(sol.linearized.w)'
```

Each script currently configures its data source explicitly.  Before running a model, confirm the CSV paths inside the file use `joinpath(@__DIR__, ...)` or update them to point to your data directory; this avoids hard-coded `/Users/...` paths when sharing with collaborators.

### 3. Toward a `uv run`-style workflow

The repository is ready for a thin launcher script, e.g. `scripts/run_model.jl --model floating_1Q_coupled_XY --qubit q5`.  To get there:

1. Ensure every `circuit_model_analysis/*.jl` exposes its configuration as a function (similar to `solve_circuit` in `floating_1Q_coupled_Readout.jl`).
2. Move hard-coded constants into keyword arguments or small configuration structs.
3. Have the launcher `include` the chosen file and call the exported function.

Following the programming principles below will make this upgrade straightforward.

### 4. Register and call models programmatically

The `models/` directory is intended to house reusable builders.  Each builder calls `register_model!` so that the function can later be invoked through the shared registry:

```julia
julia --project=.
julia> using JPACircuitModelSim
julia> include("models/floating_1Q_coupled_XY.jl")  # registers itself
julia> run_model(:floating_1Q_coupled_XY; qubit="q5", fspan=(4.0, 5.0))
```

This layer will become the backend for a CLI launcher; keeping logic in `models/` avoids copy/paste across scripts and notebooks.

### 5. Run a built-in LC model & export simulation data

Julia 端現在只負責產生/快速檢查 JosephsonCircuits.jl 或 HFSS 模擬結果；深入分析與報告交給 Python 專案。可以直接呼叫 `simulate_model` 取得 S/Z/Y 並寫到 `data/processed`：

```julia
julia --project=.
julia> using JPACircuitModelSim
julia> simulate_model(:single_lc_resonator;
                      L_ind = 25e-9,
                      C_cap = 58e-15,
                      f_start_GHz = 4.5,
                      f_stop_GHz = 7.5,
                      exports = [:S, :Z])
```

- 會自動在 `data/processed/` 下產生 `single_lc_resonator_S.csv`, `single_lc_resonator_Z.csv`（附時間戳），欄位包含實部/虛部/幅度/相位。
- 想做參數掃描可使用 `sweep_parameter(:single_lc_resonator, :C_cap, [55e-15, 58e-15, 61e-15])`，每個點都會呼叫一次 `simulate_model` 並輸出對應 CSV。
- 如果要匯出自訂 DataFrame，仍然可以呼叫 `export_dataframe_csv(df, "my_results.csv"; subdir="processed", timestamp=true)`；函式會自動建立資料夾並回傳檔案路徑。
- 資料夾結構可透過 `Paths.DATA_DIR`, `Paths.RAW_DIR`, `Paths.PROCESSED_DIR` 等常數取得；模擬腳本（例如 `circuit_model_analysis/port_on_LC_oscillator.jl`）可以直接 `using JPACircuitModelSim` 後呼叫 `ili_plot` 與 `export_dataframe_csv` 來快速檢查/輸出。

運行完成的 CSV 再交由 Python 專案進一步 fitting、可視化或報告即可。

## Built-in helpers and conventions

- **`ili_plot` (from `JPACircuitModelSim`)** — wraps PlotlyJS traces so all figures share titles, axis labels, font sizes, and downloadable PNG exports.  Accepts keyword arguments for ranges, tick formats, and canvas size.  Reuse it whenever you convert harmonic-balance arrays into scatter traces.
- **Paths / DataExport** — `Paths` exposes canonical directories (`DATA_DIR`, `RAW_DIR`, etc.) while `export_dataframe_csv` provides a one-liner to persist simulation sweeps for downstream Python analysis.
- **Harmonic-balance workflow** — scripts share the same pattern: define symbolic components with `@variables`, store topology as a vector of `(element, node₊, node₋, value)`, evaluate with `hbsolve`, then analyze `sol.linearized` (`w`, `Z`, `S`).  When writing new studies, start from `floating_1Q_coupled_XY.jl` or `port_on_LC_oscillator.jl`.
- **Admittance/Z-matrix tool snippets** — `floating_1Q_coupled_XY.jl` shows how to invert `Z` into `Y`, perform Kron reductions, and compute mode weights (`alpha`, `beta`).  Copy those routines when you need similar reductions.
- **Symbolic derivations** — `symbolics_model_analysis/...` illustrates how to build Hessians with `Symbolics.hessian` to confirm capacitance matrices.  Use it to validate hand-written reductions before running numeric sweeps.

## Programming principles

1. **Environment-first.** Always run with `julia --project=.` and keep dependencies declared in `Project.toml`.  Install any new package via `Pkg.add` so manifests stay reproducible.
2. **Relative resources.** Load CSV/Q3D exports with `joinpath(@__DIR__, "..", "circuit_model_analysis", "PF6FQ_Q3D_C_Matrix.csv")` or, for new data, use `JPACircuitModelSim.Paths` (`joinpath(Paths.RAW_ADMITTANCE_DIR, "file.csv")`) so paths stay portable.  Declare units (e.g., `const GHz = 1e9`) at the top of each file.
3. **Functional entry points.** Wrap simulations inside functions that accept explicit keyword arguments (`f_start`, `f_stop`, `Npumpharmonics`, etc.).  This makes it easy to script sweeps, add command-line interfaces, or reuse logic in notebooks.
4. **Consistent circuits.** Represent topologies as `Vector{Tuple{String,String,String,Num}}` and keep component symbols (`@variables R50 C_01 ...`) grouped near the top.  Document any non-obvious connections (mutual inductors, differential ports) with short comments.
5. **Numerical hygiene.** Work in SI units internally, keep arrays typed (`Array{ComplexF64}`), and guard expensive operations (matrix inversions) with preallocation as shown in `floating_1Q_coupled_XY.jl`.  Use helper functions (like `unwrap_phase`) whenever there is reusable math.
6. **Plotting standard.** Use `ili_plot` for all PlotlyJS visualizations; add new helper kwargs rather than duplicating layout code in scripts.  Include axis labels, legends with physical meaning, and persist raw data via CSV whenever possible.
7. **Documentation & comments.** Add docstrings to new helpers (`solve_circuit`, data loaders) and short comments that explain the intent (e.g., “Neumann–Kron reduction to eliminate XY line”).  Describe expected inputs/outputs so AI-generated code can stay consistent.
8. **Extensibility mindset.** New features should live in their own files under `circuit_model_analysis/` or dedicated subdirs.  Keep symbolic derivations separate from numeric solvers.  When multiple scripts share logic, move it into `src/` (e.g., extend `JPACircuitModelSim`) before copy/pasting.
9. **Single responsibility.** Each module/file should own exactly one concern (e.g., `Paths` only manages directories, `Plotting` only wraps PlotlyJS, `utils/DataExport.jl` only persists DataFrames).  When adding code, decide which layer it belongs to and keep helper functions scoped there rather than mixing concerns.

## Extending / maintaining the project

- **Add a new simulation:** create `circuit_model_analysis/<name>.jl`, start with the constants+`@variables` pattern, `using JPACircuitModelSim` (or `include("../utils.jl")` for legacy scripts), load any CSV using a relative path, and expose a `run_<name>` function.  Provide example usage in the file header (or append a section to this README once it stabilizes).
- **Share data and outputs:** keep experimental CSVs alongside the script or under a future `data/` directory; document the origin (HFSS, ADS, measurement) and units.  Scripts like `port_on_LC_oscillator.jl` show how to append sweep results to a `DataFrame` and export via `CSV.write`.
- **Refactor helpers:** whenever two scripts need the same chunk of code (parameter sweeps, impedance inversion, Kron reduction, data export helpers), centralize it inside `src/` (extend `JPACircuitModelSim`) so every caller shares the same implementation and style.
- **Plan for the CLI launcher:** once each simulation exposes a function, add `scripts/run_model.jl` with `using ArgParse` or `Base.ArgTools` to parse `--model`, `--qubit`, etc., then call the matching function.  This script will be the Julia analogue of `uv run`.

Following the structure above will make it easier for human collaborators and AI copilots to understand what each file does, keep syntax/style consistent, and evolve the project toward a maintainable toolbox of circuit models.
