---
name: writing-specs
description: Convert an agreed product direction into precise, testable requirements before solution design. Use in the Littlepowers spec phase when behavior, boundaries, edge cases, constraints, and acceptance criteria need a durable document. Do not use to choose implementation architecture.
---

# Writing Specs

Describe what must be true without prematurely choosing how to implement it.

## Preconditions

Read the active state and brainstorm artifact. If no direction has been chosen and the missing choice is material, return to `brainstorming`. Treat supplied requirements as the brainstorm input when they are already complete.

Inspect existing user-visible behavior and repository conventions that constrain the specification.

## Write the specification

Use the repository's convention or default to:

`docs/littlepowers/specs/YYYY-MM-DD-<slug>.md`

Include only relevant sections:

- purpose and problem;
- goals and non-goals;
- users or callers;
- functional requirements with stable IDs;
- observable behavior and data rules;
- errors, edge cases, and recovery expectations;
- compatibility, performance, privacy, and security constraints;
- acceptance criteria;
- assumptions and open questions.

Make every requirement falsifiable. Replace vague words such as "fast", "robust", or "appropriate" with an observable threshold or behavior. Keep architecture out unless it is an externally imposed constraint.

Resolve every question that would change behavior or scope before proceeding. Record low-risk assumptions explicitly.

## Review and checkpoint

Check for contradictions, placeholders, uncovered edge cases, and acceptance criteria that cannot be tested. Fix issues in the document.

Resolve `<plugin-root>` by going two directories up from this skill directory, then run:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py checkpoint \
  --phase design \
  --artifact spec=<artifact-path> \
  --completed spec \
  --next-action "Design a solution for the approved specification"
```

Use `designing-solutions` next.

