## Littlepowers workflow

- Use `littlepowers:using-littlepowers` for long-running, ambiguous, architectural, risky, or explicitly phased development work.
- Choose direct, lean-plan, compact, or full shaping by unresolved decisions and risk. Small bounded work with one real decision follows brainstorm → plan; full shaping follows brainstorm → spec → design → plan.
- At Lean/Compact/Full planning boundaries, persist one Review Lease policy from the latest request: `blocking` for discuss/wait/ambiguity, `implementation_mandate` for a fixed bounded Lean/Compact implementation request, `windowed` only with an explicit duration and fallback, or `unattended` only when explicitly told not to ask or stop. End-to-end delivery alone is not unattended authority.
- Never consume a Review Gate after a correction, hold, replacement, uncertainty, proposed scope delta, changed artifact, or Contract/Plan drift. Review continuation does not authorize external writes, destructive actions, secrets, or broader permissions. Arm the optional Claude sleeper only for an exact current session UUID and a valid future `windowed` gate; otherwise resume manually.
- Bind the latest request and approved parent PRD/spec/prototype/baseline as one complete outcome. Do not create product or technical slices or staged deliveries; use one continuous implementation stream with tasks, checkpoints, rollback units, and small commits for safe ordering. Highlight `Added / Changed / Deferred / Removed` for explicit approval, or state `No scope delta`.
- Treat implementation-generated visual snapshots as regression evidence only, and report work-unit compliance separately from approved-outcome fidelity.
- Resolve the exact project root before reading recovery context. Treat recovery state as a continuity hint; the latest user request has priority. Preserve unrelated ancestor or sibling workflows instead of silently overwriting them.
- Keep the root coordinator as the only ledger writer in multi-agent runs.
- Put new durable artifacts under `docs/littlepowers/...` unless the latest user request or a current repository instruction explicitly names another root for new workflow artifacts; do not infer one from legacy directories or backlinks.
- Keep tiny, fully specified edits lightweight and verify changes proportionally.
- On prompt, resume, clear, or compaction boundaries, reconcile restored ledger facts with the latest request.
