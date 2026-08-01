# Contributing

Thank you for improving Littlepowers. The project values small, evidence-backed changes that remain first-class in Codex, Claude Code, Qoder, and OpenCode.

## Before opening a change

Use an issue for behavior, compatibility, security-boundary, or architecture changes. A typo or focused test fix can go directly to a pull request.

Do not report a vulnerability in a public issue. Follow [SECURITY.md](SECURITY.md).

## Set up

Requirements:

- Python 3.9 or later;
- Node.js 22 for the pinned Claude Code validator;
- the current Codex CLI or app bundle for Codex validators;
- Git Bash when testing Windows hooks.

Clone the repository and run:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
claude plugin validate --strict .
```

## Design rules

- Keep one shared skill and state implementation for all supported hosts.
- Keep Hook handlers read-only, local, bounded, transcript-free, and fail-open.
- Keep telemetry out of the project.
- Treat the latest user request as authoritative and ledger values as data.
- Select direct, lean-plan, compact, or full shaping by decisions and risk; bounded small changes may go brainstorm → plan without separate spec/design artifacts.
- Preserve approved parent requirements as one definition of done and one continuous implementation stream. Do not create product or technical slices or staged deliveries; use tasks, checkpoints, rollback units, and small commits for safe ordering, and require explicit approval for `Added / Changed / Deferred / Removed` scope.
- For tracked protocol-1.3 work, bind explicit parent sources, preserve stable Outcome IDs, map every active Outcome to tasks and evidence, resolve each planning Review Gate under its persisted policy, and record all three verification verdicts before completion.
- Debug unexpected behavior from reproduction and one falsifiable hypothesis at a time.
- Require fresh evidence before completion and choose local, connected, or broad checks by impact and rollback scope.
- Keep change review read-only and proportional; do not require a separate reviewer for every tiny edit.
- Keep the root coordinator as the only ledger writer in multi-agent runs.
- Do not add model or effort overrides without a concrete, measured compatibility need.

Update only the route artifacts that exist: lean work uses brainstorm and plan;
compact work uses its shape; full work uses brainstorm, specification, design,
and plan. Rebind an approved Outcome Contract when its semantics or explicit
sources change; do not edit `.littlepowers/state.json` by hand.

## Tests

Add regression coverage for behavior changes. Security and recovery changes should cover both the state CLI and Hook path. Compatibility claims must state whether they come from static validation, Hook delivery, or an authenticated model run.

Before submitting:

1. During implementation, run focused tests for each independently reversible change.
2. At the aggregate pull-request or release boundary, run all unit tests and compilation when shared surfaces are affected.
3. Validate every changed skill and the Codex plugin; validate all skills for a release.
4. Run Claude strict plugin validation when packaging or shared skill discovery is affected.
5. Inspect the complete diff for unrelated files and generated state.
6. Update the changelog when users will observe the change.
7. Keep the Codex, Claude, and Qoder manifests, the marketplaces, and `package.json` versions aligned.
8. For a schema change, verify migration and restore on an isolated copy. Do
   not migrate an active development ledger merely to test the candidate.

## Pull requests

Describe the outcome, risk, test evidence, compatibility impact, and any remaining limitation. Keep each pull request focused enough to review and revert independently.

By contributing, you agree that your contribution is licensed under the repository's MIT License and to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
