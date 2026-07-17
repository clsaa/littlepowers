# Changelog

All notable changes are recorded here. The project follows [Semantic Versioning](https://semver.org/).

## [0.3.0-alpha.1] - 2026-07-17

### Added

- UserPromptSubmit reminders for ordinary prompt boundaries.
- SubagentStart ownership context for coordinator-only ledger writes.
- Schema 2 workflow IDs, revisions, timestamps, explicit resume, and replacement archives.
- Cross-process locking and stale-revision conflict detection.
- Shared validation for tracked, linked, non-regular, oversized, and path-escaping state.
- Direct tracking, one-file compact shaping, and a ledger management skill.
- Capability, security, model compatibility, expert review, and provenance documentation.
- Contribution, security, conduct, issue, and pull-request guidance.
- Linux, macOS, and Windows test coverage.

### Changed

- Planning depth now follows decisions and risk rather than file count or model effort.
- Hook output contains bounded factual data instead of imperative workflow policy.
- The latest user request is authoritative; recovery state is a continuity hint.
- Codex `/goal` is no longer recommended beside the ledger.
- Multi-agent plans may use dependency-safe waves while the root coordinator retains ledger ownership.

### Security

- Reject state-directory and state-file symlink or reparse-point redirection.
- Pin POSIX workspace and state-directory components to descriptors to prevent intermediate or final pathname-swap redirection.
- Reject unsafe artifact paths and read referenced Markdown through a snapshot-bound, bounded safe reader.
- Limit state input and serialized output to 64 KiB and Hook context to 10,000 characters.
- Reject hard-linked or unexpectedly writable store files and timestamps too far in the future.
- Reject Git-tracked state in both Hook and CLI paths.

### Compatibility

- Existing schema 1 ledgers migrate deterministically on their next successful mutation.
- This prerelease does not yet claim an authenticated end-to-end Fable 5 or Opus 4.8 run.

## [0.2.0] - 2026-07-17

- Added one shared Codex and Claude Code implementation with a worktree-local recovery ledger.
- Added six planning and execution skills, SessionStart recovery, native manifests, tests, and CI.

## [0.1.0] - 2026-07-17

- Created the initial Codex plugin and planning workflow.

[0.3.0-alpha.1]: https://github.com/clsaa/littlepowers/releases/tag/v0.3.0-alpha.1
[0.2.0]: https://github.com/clsaa/littlepowers/commits/main
[0.1.0]: https://github.com/clsaa/littlepowers/commits/main
