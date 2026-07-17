# Littlepowers Product Specification

## Purpose

Littlepowers is a lightweight Codex plugin for keeping non-trivial development work on a reviewable path and recovering unfinished work after a session resume, context compaction, or newly opened task in the same workspace.

## Goals

- Provide an explicit brainstorm → spec → design → plan → execute → verify workflow.
- Scale the workflow to the task instead of forcing ceremony onto trivial edits.
- Persist the active objective, phase, artifacts, current task, and next action outside conversation history.
- Restore unfinished state through a Codex plugin SessionStart hook.
- Fit GPT-5.6/Codex conventions: concise skills, native plan tracking, minimal questions, proportional verification, and no mandatory subagents.
- Be installable from a GitHub-hosted Codex marketplace repository.

## Non-goals

- Supporting Claude Code, Cursor, OpenCode, Pi, or other agent harnesses.
- Recreating Superpowers' complete TDD, worktree, review-agent, or branch-finishing methodology.
- Preventing the user from intentionally steering, pausing, replacing, or cancelling work.
- Changing Codex app settings on the user's behalf.
- Reading unstable transcript formats or storing conversation content.
- Sending telemetry or making network calls at runtime.

## Functional requirements

### FR1 — Workflow routing

Classify work before editing:

- **Direct:** local, reversible, fully specified, low-risk work may proceed with a short mental plan and verification.
- **Shaped:** ambiguous, architectural, risky, or multi-file work follows all workflow phases.
- User instructions can explicitly choose or skip phases.

### FR2 — Separate phases

The shaped workflow has these ordered phases:

1. Brainstorm: clarify outcome and constraints; compare viable approaches.
2. Spec: record required behavior, boundaries, and acceptance criteria.
3. Design: record architecture, interfaces, data flow, errors, and verification strategy.
4. Plan: produce ordered, checkable implementation tasks with exact paths and commands.
5. Execute: work task by task and checkpoint state.
6. Verify: run relevant checks and compare the result with the spec.

### FR3 — Reviewable artifacts

Default artifact paths are:

- `docs/littlepowers/brainstorms/YYYY-MM-DD-<slug>.md`
- `docs/littlepowers/specs/YYYY-MM-DD-<slug>.md`
- `docs/littlepowers/designs/YYYY-MM-DD-<slug>.md`
- `docs/littlepowers/plans/YYYY-MM-DD-<slug>.md`

Existing repository conventions and explicit user paths override these defaults.

### FR4 — Durable active state

Store active state at `<workspace-root>/.littlepowers/state.json`. Create `.littlepowers/.gitignore` so scratch state does not appear in commits. State must include:

- schema version
- status
- objective
- phase
- artifact paths
- current task
- next action
- completed checkpoints
- last update time

State commands must support start, checkpoint, pause, complete, cancel, show, and context rendering.

### FR5 — Recovery hook

On Codex `SessionStart` for `startup`, `resume`, `clear`, or `compact`:

- locate active state from the session working directory;
- emit no output when no active state exists;
- inject concise additional developer context when state is active or paused;
- reject a state file tracked by Git and treat all state values as untrusted data;
- never modify project files, inspect transcripts, or access the network.

### FR6 — Skills

Ship concise skills for:

- routing and continuity (`using-littlepowers`)
- brainstorming
- writing specs
- designing solutions
- writing plans
- executing and verifying plans

Each skill must have OpenAI UI metadata and pass the Codex skill validator.

### FR7 — Interruption semantics

When an active state exists, a new message is interpreted as one of:

- additive context or correction: update the current objective and continue;
- status/question: answer briefly, then continue;
- pause: checkpoint and stop safely;
- explicit replace/cancel: close the old state before starting new work.

An unrelated message must not silently erase active state.

### FR8 — Distribution and documentation

The repository must contain a valid plugin manifest, GitHub marketplace entry, install instructions, an optional `AGENTS.md` guidance snippet, license, and automated tests.

## Acceptance criteria

- All bundled skills validate.
- The plugin scaffold validates under the bundled plugin validator, with current Codex hook discovery covered separately.
- State CLI tests cover lifecycle transitions, root discovery, invalid transitions, and context output.
- Hook tests prove silence without state, rejection of tracked state, and valid recovery context with local state.
- Codex can discover the repository marketplace and install the plugin locally.
- A fresh `codex debug prompt-input` inspection shows all six installed skills.
- A read-only, ephemeral `codex exec` probe receives the recovery context when unfinished state exists.
- README clearly explains Queue, `/goal`, `/side`/`/btw`, explicit skill invocation, hook trust, and uninstall behavior.
