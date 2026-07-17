# Littlepowers Brainstorm

## Problem

Two failures need separate controls:

1. A follow-up message can steer an in-flight Codex turn, and the agent may treat it as a replacement instead of returning to the active objective.
2. Implicit skill matching is advisory. A coding request can skip the desired brainstorm → spec → design → plan sequence, especially when a large bootstrap prompt competes with the model's native instructions.

The upstream `superpowers` repository was reviewed at v6.1.1 (`d884ae0`, 2026-07-02). Its Codex package intentionally disables plugin hooks and relies on native skill discovery. That keeps startup light, but it does not provide a durable, project-local recovery record for unfinished work.

## Options considered

### A. Prompt-only workflow

Put a global rule in `AGENTS.md` and ship a few skills.

- Advantages: smallest implementation; no executable hooks; no trust prompt.
- Weaknesses: state is still conversational; a compacted, resumed, or newly opened task can lose its place.

### B. Fork Superpowers

Rename the project and retain its strict bootstrap, hard gates, worktree flow, TDD rules, and subagent orchestration.

- Advantages: broad methodology already exists.
- Weaknesses: preserves the GPT-5.6 conflict the user wants to avoid; large context cost; much more cross-platform code than this problem needs.

### C. Native-first workflow plus a recovery ledger

Use concise Codex-native skills for the workflow, a self-ignored state file for the current objective, and a narrow SessionStart hook that emits context only when unfinished work exists.

- Advantages: durable recovery without a permanent bootstrap; works with Codex's built-in planning and goal features; small enough to audit.
- Weaknesses: the hook must be trusted after installation; same-turn steering is still best prevented with the app's Queue setting.

## Decision

Choose option C.

Littlepowers will be Codex-first rather than a multi-harness fork. It will use proportional process: direct execution for trivial, fully specified edits; brainstorm → spec → design → plan for ambiguous, multi-file, risky, or architectural work. It will not require subagents, create worktrees, commit automatically, use telemetry, or make network requests.

The product-level companion practices are:

- Start long work with `/goal` and measurable completion criteria.
- Set **Settings → General → Follow-up behavior** to **Queue**.
- Use `/side` or `/btw` for questions that should not alter the main task.
- Invoke the workflow explicitly when the automatic match matters: `$littlepowers:using-littlepowers`.

