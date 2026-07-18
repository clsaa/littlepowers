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

For an existing workflow, keep the artifact root already resolved by `using-littlepowers`. When resolving a new workflow, use a non-default root only when the latest user request or a current repository instruction explicitly names it for new workflow artifacts. Existing directories, backlinks, and historical or tool-branded paths do not qualify by themselves. Otherwise use `docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`. Include the problem, constraints, options, selected direction, decision rationale, assumptions, and open questions.

The checkpointed `brainstorm` artifact must be this shaping record in the resolved brainstorm area. An ADR may be created or updated as a companion record of the selected decision, but an ADR is not a substitute for the brainstorm artifact. Preserve a legacy ADR-backed artifact reference during recovery; apply this rule to new or deliberately reshaped workflows instead of silently rewriting active ledger paths.

Checkpoint with the `<state-cli>`, workflow ID, and revision established by `using-littlepowers`:

```bash
<python> <state-cli> checkpoint \
  --workflow <workflow-id> --expect-revision <revision> \
  --phase spec \
  --artifact brainstorm=<artifact-path> \
  --completed brainstorm \
  --progress "Full shape: brainstorm complete; spec is next" \
  --next-action "Write the product specification"
```

Use the returned revision, then invoke `writing-specs`.
