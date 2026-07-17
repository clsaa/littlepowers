---
name: designing-solutions
description: Turn an approved specification into an implementation-ready technical design. Use in the Littlepowers design phase for component boundaries, interfaces, data flow, failure handling, compatibility, migration, security, and verification strategy. Do not use before required behavior is settled.
---

# Designing Solutions

Choose the smallest architecture that satisfies the specification and fits the existing system.

## Ground the design

Read active state, the specification, relevant code, tests, configuration, and local instructions. Follow established patterns unless they prevent a requirement. Keep unrelated refactors out of scope.

Compare alternatives only where the choice has meaningful tradeoffs. Make the recommendation explicit and request user input only when the decision materially changes behavior, cost, risk, or future constraints.

## Write the design

Use the repository's convention or default to:

`docs/littlepowers/designs/YYYY-MM-DD-<slug>.md`

Cover the parts that apply:

- architecture overview;
- components and single responsibilities;
- public interfaces, schemas, and invariants;
- control and data flow;
- state ownership and persistence;
- failure modes, retries, rollback, and observability;
- security and privacy boundaries;
- compatibility, migration, and deployment;
- testing and verification strategy;
- mapping from specification requirement IDs to design elements.

Keep interfaces concrete enough to plan against. Prefer focused units that can be understood and tested independently. Do not add extensibility without a current requirement.

## Review and checkpoint

Check that every requirement has a design path, names and types are consistent, failure behavior is defined, and the proposal can be delivered as one coherent plan.

Resolve `<plugin-root>` by going two directories up from this skill directory, then run:

```bash
python3 <plugin-root>/scripts/littlepowers_state.py checkpoint \
  --phase plan \
  --artifact design=<artifact-path> \
  --completed design \
  --next-action "Write the implementation plan"
```

Use `writing-plans` next.
