---
name: brainstorming
description: Explore a rough or consequential software idea before requirements or implementation. Use for the brainstorm phase of Littlepowers when intent, scope, constraints, success criteria, or viable approaches need clarification. Do not use once an approved, testable specification already exists.
---

# Brainstorming

Turn the request into a chosen direction without writing implementation code.

## Explore

1. Read active Littlepowers state and relevant repository context, docs, and recent changes.
2. State the intended outcome, known constraints, and assumptions in your own words.
3. Ask one high-leverage question at a time only when its answer changes the direction. Prefer a reasonable stated assumption when the risk is low.
4. Compare two or three genuinely viable approaches when a meaningful choice exists. Lead with the recommendation and explain tradeoffs. Do not invent fake alternatives.
5. Identify non-goals and a measurable definition of success.

If the request contains multiple independent products or subsystems, decompose them and shape the first independently deliverable slice.

## Decide

Request user approval when the choice changes product behavior, scope, cost, security, compatibility, or irreversible external state. If the user asked for end-to-end execution and the recommendation follows directly from supplied constraints, record it and continue.

## Save the artifact

Use the repository's existing convention or default to:

`docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`

Include:

- problem and intended outcome;
- constraints and non-goals;
- approaches and tradeoffs;
- chosen direction and reasoning;
- assumptions and unresolved questions.

Resolve `<plugin-root>` by going two directories up from this skill directory, then checkpoint:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py checkpoint \
  --phase spec \
  --artifact brainstorm=<artifact-path> \
  --completed brainstorm \
  --next-action "Write the product specification"
```

Use `writing-specs` next. Do not skip directly to implementation.

