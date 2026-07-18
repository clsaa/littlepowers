# Changelog

All notable changes are recorded here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Add optional observable progress to the schema 2 recovery ledger without a version bump, preserving old-reader compatibility while adding bounded Hook/status rendering.
- Add regression scenarios for active-cache replacement, ADR/brainstorm separation, and long-wave progress across a status interruption.
- Add an explicit cross-workspace handoff that verifies an existing active target, cancels only the source, and records a bounded recovery pointer.
- Add an on-demand, content-free Git review snapshot for detecting drift in broad uncommitted candidates without creating a ledger.

### Changed

- Require execution checkpoints to use named milestones or acceptance-check counts instead of invented percentages, with continuity checkpoints before compaction, handoff, plugin replacement, or multi-subsystem batches.
- Keep approved plans stable while the ledger carries current execution progress.
- Partition reviews that exceed one reliable pass by trust, state ownership, or rollback boundary, with one acceptance owner aggregating shared-interface evidence once.
- Keep handoff and snapshot dormant on ordinary routes: no sibling scan, background service, automatic reviewer/model selection, or added test run.

### Fixed

- Require an explicit current declaration before using a non-default workflow artifact root, so historical or tool-branded directories such as `docs/superpowers` are not silently inherited by new Littlepowers work.
- Preserve recorded artifact paths during recovery and require authorized migrations to move files and update the ledger through the state CLI.
- Recover a replaced plugin path through the host's single enabled Littlepowers installation before rereading skills and state; never continue from remembered instructions alone.
- Require a full-route brainstorm artifact to remain distinct from an optional companion ADR while preserving legacy ledger references.
- Invalidate a broad uncommitted review verdict when its explicit candidate snapshot token changes.

## [0.4.0-alpha.1] - 2026-07-17

### Added

- A systematic debugging skill that preserves diagnosis-only authority, reproduces failures before repairs, tests one falsifiable hypothesis at a time, and escalates after three falsified fix hypotheses.
- A verification skill that gates completion on fresh claim-specific evidence and classifies checks as local, connected, or broad by impact and rollback scope.
- A read-only review skill with separate acceptance/spec and code-quality verdicts, actionable findings, and coordinator adjudication.
- Evaluation scenarios for diagnosis, stale evidence, bug reproducers, proportional test scope, delegated review, and tiny local self-review.

### Changed

- Execution conditionally invokes debugging on unexplained failures, review at material boundaries, and verification before success claims.
- Plans now name global constraints, affected interfaces, rollback units, and proportional validation rationale.
- Full-suite testing is reserved for broad shared boundaries or aggregate release verification instead of every small edit.

### Fixed

- Limit Codex `interface.defaultPrompt` to the runtime-supported maximum of three so the prompt set is loaded instead of ignored.

### Compatibility

- The three disciplines are shared by Codex and Claude Code and do not select models, effort levels, reviewers, or subagent counts.
- The skills require observable evidence and verdicts, not hidden reasoning or mandatory TDD.
- Existing hooks, state schema, and recovery behavior are unchanged.

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

[0.4.0-alpha.1]: https://github.com/clsaa/littlepowers/releases/tag/v0.4.0-alpha.1
[0.3.0-alpha.1]: https://github.com/clsaa/littlepowers/releases/tag/v0.3.0-alpha.1
[0.2.0]: https://github.com/clsaa/littlepowers/commits/main
[0.1.0]: https://github.com/clsaa/littlepowers/commits/main
