# Repository guidance

- Keep Littlepowers first-class on Codex, Claude Code, Qoder, and OpenCode, and dependency-free at runtime beyond Python 3.
- Preserve the proportional workflow: do not force full ceremony on trivial, fully specified edits.
- Keep hooks read-only, silent when no active state exists, and free of network or transcript access.
- Keep the root coordinator as the only ledger writer; delegated workers are read-only.
- Do not add telemetry.
- Update the matching brainstorm, spec, design, and plan artifacts when behavior or scope changes.
- Run `python3 -m unittest discover -s tests -v` after code or manifest changes.
- Run the official skill validator for every directory under `skills/`, the official Codex plugin validator, and `claude plugin validate --strict .` before release.
