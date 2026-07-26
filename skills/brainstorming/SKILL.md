---
name: brainstorming
description: Choose a Littlepowers lean/full direction. Use only when routed by using-littlepowers or active state phase=brainstorm.
---

# Brainstorming

Turn a consequential or unclear request into one chosen direction without implementation while preserving the approved outcome.

1. Read the active ledger and relevant repository evidence.
2. Identify the highest-authority parent acceptance sources and state the approved outcome, constraints, assumptions, and non-goals.
3. Ask one material question only when its answer changes the direction; otherwise state a low-risk assumption and continue.
4. Compare two or three real alternatives when a meaningful choice exists. Lead with the recommendation and tradeoffs.
5. Define measurable success and identify unresolved decisions.

Ask for user input when a choice changes product behavior, scope, cost, security, compatibility, or irreversible external state. If the user requested end-to-end delivery and the direction follows from supplied constraints, record it and finish the brainstorm without more questions; the phase-boundary review gate still applies before the next phase.

Every option must preserve the approved outcome. Do not turn an implementation option into a smaller product or technical slice. Record tasks or waves only as implementation order, never as deferred scope.

For an existing workflow, keep the artifact root already resolved by `using-littlepowers`. When resolving a new workflow, use a non-default root only when the latest user request or a current repository instruction explicitly names it for new workflow artifacts. Existing directories, backlinks, and historical or tool-branded paths do not qualify by themselves. Otherwise use `docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`. Include the problem, constraints, options, selected direction, decision rationale, assumptions, and open questions.

Include a scope anchor with:

- the approved outcome and highest-authority parent acceptance sources;
- inherited behaviors that must remain in the definition of done;
- `Added / Changed / Deferred / Removed` items with user-visible consequences, or the exact statement `No scope delta`;
- approved baseline provenance for visual, interaction, output, or compatibility work;
- measurable success for the complete outcome.

Highlight any non-empty scope delta in the review message and wait for explicit approval of that delta. Generic artifact approval is insufficient when the delta was not highlighted. An implementation-generated artifact cannot replace a user-approved baseline.

The checkpointed `brainstorm` artifact must be this shaping record in the resolved brainstorm area. An ADR may be created or updated as a companion record of the selected decision, but an ADR is not a substitute for the brainstorm artifact. Preserve a legacy ADR-backed artifact reference during recovery; apply this rule to new or deliberately reshaped workflows instead of silently rewriting active ledger paths.

## Lean route

When `using-littlepowers` selected the lean route, checkpoint directly to plan:

```bash
<python> <state-cli> checkpoint \
  --workflow <workflow-id> --expect-revision <revision> \
  --phase plan \
  --artifact brainstorm=<artifact-path> \
  --completed brainstorm \
  --progress "Lean route: brainstorm complete; plan is next" \
  --next-action "Write the implementation plan from the approved brainstorm"
```

Use the returned revision, then present the brainstorm for review and stop. Name `writing-plans` as the next phase. Invoke `writing-plans` only after explicit approval of the brainstorm and any highlighted scope delta, or immediately when the latest user request explicitly authorized unattended end-to-end execution and there is no unapproved scope delta.

## Full route

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

Use the returned revision, then present the brainstorm for review and stop: summarize the selected direction, rationale, scope delta, baseline when applicable, and open questions; name the artifact path and name `writing-specs` as the next phase. Invoke `writing-specs` only after explicit approval of this artifact and any highlighted scope delta, or immediately when the latest user request explicitly authorized unattended end-to-end execution and there is no unapproved scope delta. On either route, when the user asks for corrections, revise this artifact, checkpoint again, and present it again instead of advancing.
