# Littlepowers Product Specification

> Historical v0.2 artifact. Superseded by [the v0.3 specification](2026-07-17-v0.3-expert-review.md).

## Purpose

Littlepowers is a lightweight Codex and Claude Code workflow for keeping non-trivial development work on a reviewable path and recovering unfinished work after interruption or session boundaries.

## Goals

- Provide an explicit brainstorm → spec → design → plan → execute → verify workflow.
- Scale process to the task instead of forcing ceremony onto trivial edits.
- Persist the active objective, phase, artifacts, current task, and next action outside conversation history.
- Restore unfinished state on startup, resume, clear, and compaction in Codex and Claude Code.
- Share one behavior implementation across both harnesses while using native installation metadata for each.
- Remain dependency-free at runtime beyond Python 3.
- Be installable from the GitHub repository through both native plugin marketplaces.

## Non-goals

- Recreating Superpowers' complete TDD, worktree, review-agent, or branch-finishing methodology.
- Supporting Cursor, OpenCode, Pi, or other agent harnesses in this release.
- Preventing the user from intentionally steering, pausing, replacing, or cancelling work.
- Changing Codex or Claude Code settings on the user's behalf.
- Reading unstable transcript formats or storing conversation content.
- Sending telemetry or making network calls at runtime.

## Functional requirements

### FR1: Workflow routing

Classify work before editing:

- **Direct:** local, reversible, fully specified, low-risk work may proceed with a short plan and verification.
- **Shaped:** ambiguous, architectural, risky, or multi-file work follows all workflow phases.
- Explicit user instructions can choose, skip, or revisit phases.

### FR2: Separate phases

The shaped workflow has these ordered phases:

1. Brainstorm: clarify outcome and constraints; compare viable approaches.
2. Spec: record required behavior, boundaries, and acceptance criteria.
3. Design: record architecture, interfaces, data flow, errors, and verification strategy.
4. Plan: produce ordered, checkable implementation tasks with exact paths and commands.
5. Execute: work task by task and checkpoint state.
6. Verify: run relevant checks and compare the result with the spec.

### FR3: Reviewable artifacts

Default artifact paths are:

- `docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`
- `docs/littlepowers/specs/YYYY-MM-DD-<slug>.md`
- `docs/littlepowers/designs/YYYY-MM-DD-<slug>.md`
- `docs/littlepowers/plans/YYYY-MM-DD-<slug>.md`

Existing repository conventions and explicit user paths override these defaults.

### FR4: Durable active state

Store active state at `<workspace-root>/.littlepowers/state.json`. Create `.littlepowers/.gitignore` so scratch state does not appear in commits. State includes:

- schema version
- status
- objective
- phase
- artifact paths
- current task
- next action
- completed checkpoints
- last update time

State commands support start, checkpoint, pause, complete, cancel, show, and context rendering. One worktree has at most one active objective.

### FR5: Cross-harness recovery hook

On `SessionStart` for `startup`, `resume`, `clear`, or `compact`:

- locate active state from the session working directory;
- emit no output when no unfinished state exists;
- inject concise additional context when state is active or paused;
- reject a state file tracked by Git and treat state values as untrusted data;
- never modify project files, inspect transcripts, or access the network;
- complete within five seconds and fail open on malformed input or state;
- resolve its installed plugin root under both Codex and Claude Code.

### FR6: Shared skills

Ship one shared copy of six skills:

- routing and continuity (`using-littlepowers`)
- brainstorming
- writing specs
- designing solutions
- writing plans
- executing and verifying plans

Every skill has portable Agent Skills frontmatter. Codex UI metadata remains available under `agents/openai.yaml`. Harness-specific interaction advice is conditional and never presented as portable behavior.

### FR7: Interruption semantics

When active state exists, a new message is interpreted as one of:

- additive context or correction: update artifacts/state and continue;
- status or question: answer briefly, then continue;
- pause: checkpoint and stop safely;
- explicit replace or cancel: close old state before starting new work.

An unrelated message must not silently erase active state.

### FR8: Native packaging and documentation

The repository contains:

- a Codex plugin manifest and marketplace catalog;
- a Claude Code plugin manifest and marketplace catalog;
- matching plugin versions and metadata;
- install, update, uninstall, and explicit invocation instructions for both;
- optional `AGENTS.md` and `CLAUDE.md` guidance snippets;
- license and automated tests.

### FR9: Versioning

The Codex manifest, Claude Code manifest, and Claude marketplace entry use the same semantic version. Every published behavior change bumps that version.

## Acceptance criteria

- All six skills pass the bundled skill validator.
- The Codex plugin and marketplace pass their validator and install from the repository.
- `claude plugin validate --strict .` passes.
- Claude Code can add the repository marketplace, install `littlepowers@littlepowers`, and discover all six skills.
- Codex and Claude Code each receive recovery context from an active ledger in a real CLI probe.
- Unit tests exercise both plugin-root environment conventions and all recovery edge cases.
- README distinguishes shared behavior from harness-specific controls and documents both installation paths.
- GitHub Actions passes on the published commit.
