---
name: brainstorming
description: Littlepowers internal full-shape phase for choosing a product direction. Use only when using-littlepowers selected the full route or active state says phase=brainstorm. If no matching workflow exists, route through using-littlepowers first.
---

# Brainstorming

Turn a consequential or unclear request into one chosen direction without implementation.

1. Read the active ledger and relevant repository evidence.
2. State the outcome, constraints, assumptions, and non-goals.
3. Ask one material question only when its answer changes the direction; otherwise state a low-risk assumption and continue.
4. Compare two or three real alternatives when a meaningful choice exists. Lead with the recommendation and tradeoffs.
5. Define measurable success and identify unresolved decisions.

Ask for user input when a choice changes product behavior, scope, cost, security, compatibility, or irreversible external state. If the user requested end-to-end delivery and the direction follows from supplied constraints, record it and continue.

Use the repository's artifact convention, or default to `docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`. Include the problem, constraints, options, selected direction, decision rationale, assumptions, and open questions.

Checkpoint with the `<state-cli>`, workflow ID, and revision established by `using-littlepowers`:

```bash
<python> <state-cli> checkpoint \
  --workflow <workflow-id> --expect-revision <revision> \
  --phase spec \
  --artifact brainstorm=<artifact-path> \
  --completed brainstorm \
  --next-action "Write the product specification"
```

Use the returned revision, then invoke `writing-specs`.
