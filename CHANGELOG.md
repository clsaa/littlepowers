# Changelog

All notable changes are recorded here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.0-alpha.1] - 2026-07-26

### Added

- Add a lean planning route for bounded changes: brainstorm → plan → execute, with no separate specification or design artifact.
- Add parent-contract inheritance, a highlighted `Added / Changed / Deferred / Removed` Scope Delta Gate, and approved-baseline provenance.
- Add separate work-unit compliance and approved-outcome fidelity verdicts so a narrower technical work unit cannot be reported as complete product consistency.
- Include the canonical workspace root in recovery snapshots and require explicit project-root context, preventing an unrelated ancestor ledger from silently driving a nested project.
- Add regression/evaluation scenarios for small-change routing, implicit scope slicing, self-generated visual baselines, and nested-project ledger isolation.

### Changed

- Treat tasks and dependency-safe waves as implementation order only. Agents may not split an approved outcome into independently accepted product, technical, platform, MVP, or phase slices without an explicitly approved scope delta.
- Require plans, execution, reviews, and completion evidence to retain inherited parent acceptance criteria under one definition of done.
- Keep the new protections model-neutral and lightweight: no schema migration, extra model call, reviewer, background scan, or automatic test run.

## [1.0.0] - 2026-07-21

The first stable release. Multi-host support (Codex, Claude Code, Qoder, OpenCode), full-route phase review gates, and host plan-surface mirroring land as the stable contract, with the expert-review fixes below.

### Fixed

- Close the review-gate loopholes found in expert review: define explicit approval, treat corrections as revise-and-re-present instead of phase advancement, keep the agent parked at a gate across status questions and compaction, and harmonize the gate wording across the router and every phase skill.
- Align hook plugin-root resolution order between `hooks.json` and `session-start.py` so a Qoder install can no longer mix roots when both variables are set.
- Fix the OpenCode plugin to spawn the fallback Python interpreter at most once and only when `python3` is missing, wrap every hook body so host API drift fails open, give task-created child sessions the worker read-only context, and retry empty ledger lookups only after a newer message arrives.
- Fix the Codex post-replacement recovery to resolve git-sourced marketplace entries through `source.url` instead of the never-present `source.path`.
- Update the supported-versions policy, issue templates, contributor guidance, and bilingual READMEs for all four supported hosts; cover the OpenCode plugin in the security model; mark `package.json` private with aligned keywords.

## [0.5.0-alpha.1] - 2026-07-21

### Added

- Add optional observable progress to the schema 2 recovery ledger without a version bump, preserving old-reader compatibility while adding bounded Hook/status rendering.
- Add first-class Qoder CLI and Qoder IDE support through `.qoder-plugin/plugin.json`, a shared hooks manifest that resolves `${QODER_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}`, and `QODER_PLUGIN_ROOT` handling in the recovery hook. The Qoder IDE currently fires only a subset of hook events, so SessionStart and SubagentStart stay silent there.
- Add first-class OpenCode support through `.opencode/plugins/littlepowers.js`, which registers the skills directory with OpenCode's native skill tool and injects the same read-only ledger snapshot and prompt reminder produced by `hooks/session-start.py`. Install rides OpenCode's `opencode.json` plugin entry from the repository root `package.json`.
- Mirror the tracked task checklist through the host's native plan surface so plans render in the host interface: Codex `update_plan` after the plan artifact and at each execution checkpoint, OpenCode's todo tool likewise, with re-issue from the ledger after resume or compaction. The Markdown plan file remains the durable source of truth.
- Add regression scenarios for active-cache replacement, ADR/brainstorm separation, and long-wave progress across a status interruption.
- Add an explicit cross-workspace handoff that verifies an existing active target, cancels only the source, and records a bounded recovery pointer.
- Add an on-demand, content-free Git review snapshot for detecting drift in broad uncommitted candidates without creating a ledger.

### Changed

- Full-route phase artifacts are now review gates: after checkpointing, the agent presents the brainstorm, specification, design, plan, or compact shape for approval and stops, chaining into the next phase only after user approval or an explicit unattended end-to-end authorization. Requesting end-to-end delivery is no longer treated as unattended authorization by itself.
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

[Unreleased]: https://github.com/clsaa/littlepowers/compare/v1.1.0-alpha.1...HEAD
[1.1.0-alpha.1]: https://github.com/clsaa/littlepowers/compare/v1.0.0...v1.1.0-alpha.1
[1.0.0]: https://github.com/clsaa/littlepowers/releases/tag/v1.0.0
[0.5.0-alpha.1]: https://github.com/clsaa/littlepowers/compare/v0.4.0-alpha.1...v1.0.0
[0.4.0-alpha.1]: https://github.com/clsaa/littlepowers/releases/tag/v0.4.0-alpha.1
[0.3.0-alpha.1]: https://github.com/clsaa/littlepowers/releases/tag/v0.3.0-alpha.1
[0.2.0]: https://github.com/clsaa/littlepowers/commits/main
[0.1.0]: https://github.com/clsaa/littlepowers/commits/main
