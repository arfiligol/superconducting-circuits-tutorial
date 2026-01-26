---
trigger: always_on
---

superconducting-circuits-tutorial/
├── src/
│   ├── core/                 # Domain & Application Logic
│   │   ├── analysis/         # 數據分析 (Clean Architecture)
│   │   ├── simulation/       # 電路模擬 (JuliaCall ↔ Julia)
│   │   └── shared/           # 共用工具 (visualization, utils)
│   ├── app/                  # [Planned] NiceGUI App
│   └── scripts/              # CLI Entry Points
│       ├── analysis/         # 分析腳本 (admittance_fit.py 等)
│       └── simulation/       # 模擬腳本 (run_lc.py 等)
├── data/                     # Data Lifecycle
│   ├── raw/                  # Read-Only Input (HFSS/VNA)
│   ├── preprocessed/         # Intermediate JSON
│   └── processed/            # Analysis Results & Reports
├── docs/                     # Documentation (MkDocs)
├── examples/                 # Usage Examples
├── tests/                    # Tests
├── sandbox/                  # Experimental / Legacy Code
├── pyproject.toml            # Python Dependencies (uv)
├── uv.lock                   # Python Lock File
├── juliapkg.json             # Julia Dependencies (JosephsonCircuits.jl)
├── Project.toml              # Julia Project Settings
├── Manifest.toml             # Julia Lock File
└── .gitignore                # Git Ignore Rules
