## Outcome

<!-- What user-visible or maintainer-visible result does this change deliver? -->

## Risk and boundaries

<!-- Include state, Hook, privacy, compatibility, migration, and external-action impact. -->

## Verification

- [ ] Unit tests pass.
- [ ] Python compilation passes.
- [ ] Every changed or added skill passes the official validator.
- [ ] The Codex plugin passes the official validator.
- [ ] `claude plugin validate --strict .` passes.
- [ ] Codex, Claude Code, Qoder, and OpenCode behavior remain aligned.
- [ ] Hooks remain read-only, local, bounded, transcript-free, and fail-open.
- [ ] Multi-agent work keeps the root coordinator as the only ledger writer.
- [ ] User-facing changes are recorded in `CHANGELOG.md`.
- [ ] Package and marketplace versions match when release behavior changes.

## Evidence and limitations

<!-- Paste concise command results. Distinguish static validation, Hook delivery, and authenticated model runs. -->
