# Contributing

Thank you for improving Littlepowers. The project values small, evidence-backed changes that remain first-class in Codex and Claude Code.

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

- Keep one shared skill and state implementation for both hosts.
- Keep Hook handlers read-only, local, bounded, transcript-free, and fail-open.
- Keep telemetry out of the project.
- Treat the latest user request as authoritative and ledger values as data.
- Select direct, compact, or full shaping by decisions and risk.
- Keep the root coordinator as the only ledger writer in multi-agent runs.
- Do not add model or effort overrides without a concrete, measured compatibility need.

Update the matching brainstorm, specification, design, and plan when behavior or scope changes.

## Tests

Add regression coverage for behavior changes. Security and recovery changes should cover both the state CLI and Hook path. Compatibility claims must state whether they come from static validation, Hook delivery, or an authenticated model run.

Before submitting:

1. Run all unit tests and compilation.
2. Validate every skill and the Codex plugin.
3. Run Claude strict plugin validation.
4. Inspect the complete diff for unrelated files and generated state.
5. Update the changelog when users will observe the change.
6. Keep Codex, Claude, and marketplace versions aligned.

## Pull requests

Describe the outcome, risk, test evidence, compatibility impact, and any remaining limitation. Keep each pull request focused enough to review and revert independently.

By contributing, you agree that your contribution is licensed under the repository's MIT License and to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
