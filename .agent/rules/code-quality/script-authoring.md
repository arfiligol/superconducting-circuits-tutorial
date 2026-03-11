## Script Authoring
- CLI is a first-class interface, not a leftover utility layer.
- New CLI work should go to `cli/`; avoid growing new workflows inside legacy `src/scripts/`.
- Use Typer for commands.
- Commands handle argument parsing, user I/O, and error presentation only.
- Real workflow logic must live in shared services or `src/core/`.
- Command names use `kebab-case`, and every command must have usable `--help`.
