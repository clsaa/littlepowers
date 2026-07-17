# Littlepowers Brainstorm

## Problem

Two failures need one small workflow:

1. A follow-up message can steer an in-flight coding task, after which the agent may not return to the original objective.
2. Non-trivial work can jump straight into implementation instead of moving through brainstorm → spec → design → plan.

The workflow must work in both Codex and Claude Code. Installing the full Superpowers package is intentionally out of scope because the user wants a smaller workflow and has observed conflicts with current GPT-5.6 usage.

## What the upstream review showed

Superpowers v6.1.1 was reviewed as a design reference. Its strongest reusable ideas are explicit phase skills, native harness packaging, and a SessionStart hook on Claude Code. Littlepowers needs a different center of gravity: a project-local recovery ledger that records the active objective independently of chat history.

## Options considered

### A. Separate Codex and Claude Code implementations

- Advantage: each implementation can use only native concepts.
- Cost: skills, state rules, and recovery semantics will drift.
- Decision: reject.

### B. One shared core with thin native packaging

- Shared: skills, state CLI, recovery context, artifacts, tests.
- Codex-specific: `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, optional `AGENTS.md` guidance, and Codex interaction tips.
- Claude-specific: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, optional `CLAUDE.md` guidance, and Claude interaction tips.
- Advantage: one behavior contract with native installation on both harnesses.
- Decision: choose.

### C. Depend on or fork Superpowers

- Advantage: broad existing workflow coverage.
- Cost: restores the installation/conflict concern, adds unrelated process, and ties maintenance to a much larger project.
- Decision: reject.

## Direction

Littlepowers will use six concise skills and a dependency-free state CLI. A fast, read-only SessionStart hook will restore unfinished state on startup, resume, clear, and compaction. The hook will never parse transcripts, modify the project, send telemetry, or access the network.

The process remains proportional:

- Direct, reversible, fully specified work can proceed with a short plan and verification.
- Ambiguous, architectural, risky, or multi-file work uses all phases.
- Explicit user instructions can add, skip, pause, replace, or cancel phases.

Follow-up messages are classified as additional context, a question, a pause, or an explicit replacement. Only the last category closes the existing objective.

## Naming note

`littlepowers` clearly communicates its relationship to Superpowers, but can sound like a reduced version and remains dependent on the upstream name. `planthread` better expresses the distinctive value: keeping a plan connected across interruptions. GitHub name search on 2026-07-17 found no exact `planthread` repository, while `threadline`, `taskrelay`, and `continuum` were substantially more crowded.

The working name remains Littlepowers until the user explicitly chooses a rename. Packaging keeps naming localized so a later rename is mechanical rather than architectural.

## Harness-specific controls

- Codex can additionally use Queue, `/goal`, and `/side` or `/btw`.
- Claude Code can use its native resume and compaction flow; the SessionStart hook refreshes the ledger context.
- Skills must not recommend commands from the other harness.
