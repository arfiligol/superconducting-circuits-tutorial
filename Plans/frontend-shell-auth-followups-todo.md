# Frontend Shell And Auth Follow-ups TODO

This file is a planning note for upcoming Frontend Agent prompts.
It is not a Source of Truth document and must not override `docs/reference/**`.

## Scope

- Track user-requested frontend fixes that should be bundled into future Frontend Agent prompts.
- Keep visible product issues grouped by feature outcome, not by implementation layer.
- Mark doc-dependent ideas clearly so they are not implemented silently against SoT.

## TODO

### P0 Authentication-first surfaces

- [ ] Add a visible `Login` surface instead of relying on placeholder session language.
- [ ] Add a visible `Logout` flow or dedicated logout route from the user menu.
- [ ] Make the header show clear auth-aware states:
  - anonymous session
  - authenticated user
  - degraded session
- [ ] Remove placeholder-only auth wording from the user menu once real auth/session adoption lands.

### P0 Error readability and message contrast

- [ ] Fix low-contrast error banners across shared/frontend workflow surfaces.
- [ ] Replace pale error text on pale rose backgrounds with accessible contrast.
- [ ] Apply the fix consistently to repeated error banner patterns, not just one page.
- [ ] Re-check shell-level status and workflow-level loading/error surfaces in light theme.

### P1 Sidebar shell cleanup

- [x] Trim sidebar to title-only navigation.
- [ ] Split duplicated shell identity between sidebar and header.
- [ ] Move one of these two labels out of the sidebar and into the header:
  - `SUPERCONDUCTING CIRCUITS`
  - `Research Workbench`
- [ ] Keep the sidebar focused on navigation instead of shell identity duplication.
- [ ] Preserve group labels and active-route clarity after the shell identity move.

### P1 Header and global context cleanup

- [ ] Reduce visual noise in the header/status area once auth/session authority is ready.
- [ ] Revisit how `Active Workspace`, `Active Dataset`, `Tasks Queue`, and worker summary are presented after backend auth/session work lands.
- [ ] Keep current header ownership unless docs are explicitly changed.

### P2 Pending docs decision

- [ ] Decide whether heavy global-context management should stay entirely in the header or move into a right-side drawer triggered from the header.
- [ ] If this direction changes, update docs first before implementation.

## Prompting Notes

Future Frontend Agent prompts should include these follow-ups when they touch shell/auth work:

- Authentication-first work takes precedence over cosmetic shell polish.
- Sidebar fixes should preserve the current header/global-context boundary unless docs change.
- Error readability fixes should be bundled with shell/auth UI work when possible.
- Do not silently implement the right-drawer idea until the docs decision is explicit.
