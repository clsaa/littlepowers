# Repository guidance

- Keep Littlepowers Codex-first and dependency-free at runtime.
- Preserve the proportional workflow: do not force full ceremony on trivial, fully specified edits.
- Keep hooks read-only, silent when no active state exists, and free of network or transcript access.
- Do not add telemetry.
- Update the matching brainstorm, spec, design, and plan artifacts when behavior or scope changes.
- Run `python3 -m unittest discover -s tests -v` after code or manifest changes.
- Run the official skill validator for every directory under `skills/` and the official plugin validator before release.

