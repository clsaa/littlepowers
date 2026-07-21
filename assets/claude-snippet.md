## Littlepowers workflow

- Use `littlepowers:using-littlepowers` for long-running, ambiguous, architectural, risky, or explicitly phased development work.
- Choose direct, compact, or full shaping by unresolved decisions and risk. Full shaping follows brainstorm → spec → design → plan.
- Full-shape phases pause for your review at each boundary (including shape → execute); chain automatically only when you explicitly authorize unattended end-to-end execution — requesting end-to-end delivery alone does not qualify.
- Treat recovery state as a continuity hint; the latest user request has priority. Preserve unrelated workflows instead of silently overwriting them.
- Keep the root coordinator as the only ledger writer in multi-agent runs.
- Put new durable artifacts under `docs/littlepowers/...` unless the latest user request or a current repository instruction explicitly names another root for new workflow artifacts; do not infer one from legacy directories or backlinks.
- Keep tiny, fully specified edits lightweight and verify changes proportionally.
- On prompt, resume, clear, or compaction boundaries, reconcile restored ledger facts with the latest request.
