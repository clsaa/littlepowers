## Littlepowers workflow

- Use `littlepowers:using-littlepowers` for long-running, ambiguous, architectural, risky, or explicitly phased development work.
- Choose direct, compact, or full shaping by unresolved decisions and risk. Full shaping follows brainstorm → spec → design → plan.
- Treat recovery state as a continuity hint; the latest user request has priority. Preserve unrelated workflows instead of silently overwriting them.
- Keep the root coordinator as the only ledger writer in multi-agent runs.
- Keep tiny, fully specified edits lightweight and verify changes proportionally.
- In Codex, prefer Queue for follow-up behavior and use `/side` or `/btw` for unrelated questions when appropriate.
