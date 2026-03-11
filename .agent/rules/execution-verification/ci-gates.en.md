## CI Gates
- Mandatory checks include:
    - Python format / lint / type-check
    - backend/core pytest
    - frontend lint / typecheck / tests / build when the frontend workspace exists
    - desktop lint / build when the desktop workspace exists
    - docs build when docs are touched
- `main` must not receive direct pushes.
- Guardrail source changes must keep `.agent/rules` in sync.
- Any failing required check blocks merge.
