## Source of Truth Order
- Resolve conflicts in this order:
    1. `docs/reference/data-formats/*`, `docs/reference/ui/*`, `docs/reference/cli/*`
    2. `docs/reference/architecture/*` and migration contract/parity specs
    3. `src/core/sc_core/*`
    4. `backend/`, `frontend/`, `cli/`, `desktop/` adapters
    5. legacy `src/app/` and old script behavior
- Treat legacy behavior as parity evidence, not automatic canonical truth.
- If docs and adapters conflict, prefer docs unless the user explicitly changes the spec.
- If `sc_core` and adapters conflict, fix the adapter first unless the canonical contract is incomplete.
- Record any intentional legacy-only exception in the parity matrix or contract registry.
