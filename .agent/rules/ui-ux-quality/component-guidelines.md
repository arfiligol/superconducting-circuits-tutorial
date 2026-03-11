## Component Guidelines
- Prefer components from `@/components/ui/` for interactive primitives.
- Put feature-specific UI in `frontend/src/features/<feature>/components/`.
- Do not use `alert()`, `confirm()`, or `prompt()` for product interactions.
- Destructive actions require an explicit confirmation flow.
- Forms need labels, validation, and visible error states.
- Data-dense tables must support sorting, filtering, and pagination or a clear virtualization strategy.
- Load summary rows first; fetch heavy detail payload only on explicit detail interaction.
