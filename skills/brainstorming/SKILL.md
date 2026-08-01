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

Every option must preserve the approved outcome. Do not turn an implementation option into a smaller product or technical slice. Record tasks, checkpoints, and rollback units only as continuous implementation order, never as deferred scope or staged delivery.

For an existing workflow, keep the artifact root already resolved by `using-littlepowers`. When resolving a new workflow, use a non-default root only when the latest user request or a current repository instruction explicitly names it for new workflow artifacts. Existing directories, backlinks, and historical or tool-branded paths do not qualify by themselves. Otherwise use `docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`. Include the problem, constraints, options, selected direction, decision rationale, assumptions, and open questions.

Include a scope anchor with:

- the approved outcome and highest-authority parent acceptance sources;
- inherited behaviors that must remain in the definition of done;
- `Added / Changed / Deferred / Removed` items with user-visible consequences, or the exact statement `No scope delta`;
- approved baseline provenance for visual, interaction, output, or compatibility work;
- measurable success for the complete outcome.

Highlight any non-empty scope delta in the review message and wait for explicit approval of that delta. Generic artifact approval is insufficient when the delta was not highlighted. An implementation-generated artifact cannot replace a user-approved baseline.

On the lean route, read the shared
[`../../references/outcome-lock.md`](../../references/outcome-lock.md) and add
one Outcome Contract block to this brainstorm. Give every observable outcome a
stable `OUT-###` ID, declare only explicit file sources, record baseline
provenance and code-quality review need, and keep the ID set complete. The full
route defers the protocol block to `writing-specs`; do not create a competing
contract here.

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

Use the returned revision, read
[`../../references/review-lease.md`](../../references/review-lease.md) and use
the checkpoint revision to `park-review --artifact-key brainstorm` with the
declared scope state and open-question count. A blocking gate is presented for
review and stop. Resolve an eligible implementation mandate, unattended gate,
or pre-authorized expired window with its exact kind, then choose the matching
Contract approval kind (`implementation-mandate`, `unattended-authorization`,
or `window-expired`). Only a distinctly approved blocking gate uses
`review-gate`. No kind approves a scope delta. Invoke `writing-plans` only
after gate resolution and Contract binding succeed.

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

Use the returned revision, read the Review Lease reference, and `park-review
--artifact-key brainstorm` with the declared scope state and open-question
count. For a blocking policy, present the brainstorm for review and stop:
summarize the selected direction, rationale, scope delta, baseline when
applicable, and open questions; name the artifact path and `writing-specs` as
the next phase. Resolve only an exact eligible automatic gate before invoking
`writing-specs`. A correction cancels the gate, revises/checkpoints the same
artifact, and parks it again instead of advancing.
