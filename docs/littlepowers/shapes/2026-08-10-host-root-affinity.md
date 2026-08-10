# Littlepowers 1.3.1 host and root-affinity shape

## Outcome

Ship a lightweight patch that prevents an unrelated manager-directory ledger
from steering nested-project tasks, restores every Codex starter prompt on the
current host limit, clarifies immutable Contract-source selection, validates
the current Codex, Claude Code, and Qoder releases, and publishes/install the
same exact release on all three local hosts.

## Evidence that shaped the patch

- Recent project tasks commonly start with the host working directory at the
  parent workspace rather than the named repository.
- That parent directory currently has an unfinished legacy ledger. The 1.3.0
  prompt hook deterministically injects that unrelated objective for any task
  whose `cwd` is the parent directory, even when the request names another
  nested repository.
- One recent workflow accidentally treated a test file that implementation
  would change as an immutable Contract source. The drift gate failed safely,
  but only after implementation, adding avoidable reconciliation work.
- A live Codex 0.147.0 probe loaded the Littlepowers recovery hook and returned
  the exact temporary workflow ID, while also warning that two of three
  `interface.defaultPrompt` values exceeded the current 128-character limit and
  were ignored.
- Local current versions are Codex 0.147.0, Claude Code 2.1.226, and Qoder CLI
  1.1.18. Claude and Qoder validators accept the 1.3.0 package; local installed
  Littlepowers copies are inconsistent: Codex is 1.3.0-alpha.1, Claude has no
  Littlepowers installation, and Qoder is 1.0.0.

## Selected approach

1. Keep explicit state CLI roots unchanged. Add a Hook-only root-affinity
   predicate that permits automatic injection only when the discovered ledger
   root contains a `.git` directory or worktree marker file. A non-Git manager
   directory remains usable through explicit `--root`, but its ledger is not
   guessed into every task launched from that container directory.
2. Keep the predicate local and constant-cost: inspect one already-discovered
   root marker; do not scan children, inspect prompt text/transcripts, run Git,
   access the network, or mutate state.
3. Shorten every Codex default prompt to at most 128 characters and add a
   manifest regression for the host limit.
4. Clarify that Contract sources are stable acceptance inputs for the whole
   workflow. A planned write target, generated evidence, test, or fixture that
   implementation will update stays out of `sources`; when no stable parent
   file exists, the reviewed OUT records carry the latest user request.
5. Retain schema 4 and protocol 1.3. This is a compatibility/safety patch, not
   a new authority model.
6. Validate focused Hook/manifest/routing behavior, then run the aggregate
   suite and all current host validators once after integration. Publish an
   exact `v1.3.1` commit/tag only after CI passes, then replace local plugin
   installs from that exact tag at the safe task boundary.

## Non-goals

- No transcript parsing, sibling-repository discovery, telemetry, daemon, or
  automatic project registration.
- No automatic cancellation or deletion of an existing parent-directory
  ledger.
- No new planning phase, schema field, source semantic inference, model choice,
  reviewer, or broad-test loop.
- No claim that a plugin can repair a host where it is not installed or that an
  already-open task hot-loads a replacement.

## Constraints and assumptions

- Git repositories and worktrees use a `.git` directory or marker file at the
  repository root. Non-Git workspaces retain explicit state CLI support but no
  automatic Hook recovery.
- Hook failure remains fail-open and silent when no eligible active state is
  present.
- The release continues to require only Python 3 at runtime.
- The user explicitly requested implementation, host updates, publication, and
  local installation. No scope delta is present.

## Execution and rollback units

### Task 1 — Root-affine recovery Hook

- Add the single-root eligibility predicate and focused tests for eligible Git
  roots, ineligible manager directories, native plugin-root variables, and
  unchanged active/terminal behavior.
- Rollback: revert Hook and Hook tests together.

### Task 2 — Host metadata and source-authority guidance

- Shorten Codex starter prompts and enforce the 128-character limit.
- Update router/protocol guidance and regression scenarios for stable Contract
  sources without changing the grammar or schema.
- Rollback: revert manifests, skills/references, and their focused assertions.

### Task 3 — Compatibility evidence and patch release

- Refresh compatibility/capability/security/release documentation and aligned
  `1.3.1` package metadata.
- Run the aggregate suite, all skill validators, Codex plugin validation,
  Claude strict validation, Qoder validation, OpenCode syntax, and exact-package
  smoke.
- Commit and push one release candidate, require exact-commit CI, tag/release
  the same commit, then update the three local host installations from the tag.
- Rollback: reinstall `v1.3.0`; schema/protocol rollback is unnecessary.

## Acceptance checks

- A Hook invocation from a non-Git parent workspace with an active ledger is
  silent.
- The same Hook from a Git repository/worktree with an active ledger injects
  the exact workflow, revision, root, and bounded status as before.
- Explicit CLI operations against a non-Git `--root` still work.
- All three Codex default prompts are present and no longer produce the
  128-character warning on a current runtime probe.
- Skills explicitly reject planned write targets/generated regression evidence
  as Contract sources without adding runtime ceremony.
- Codex 0.147.0, Claude Code 2.1.226, and Qoder CLI 1.1.18 package validation
  passes; available live probes are reported at their actual validation level.
- Unit/compile/skill/Codex/Claude/Qoder/OpenCode and exact-tag release gates pass.
- `v1.3.1` is published from the CI-green commit and each local host reports the
  same enabled Littlepowers version after replacement.

## Scope delta

No scope delta.

<!-- littlepowers:contract:v1 -->
```json
{
  "route": "compact",
  "sources": [],
  "scope_delta": {
    "status": "none",
    "consequences": []
  },
  "baseline": {
    "requirement": "not_applicable",
    "source_ids": []
  },
  "review": {
    "code_quality_required": true
  },
  "outcomes": [
    {
      "id": "OUT-001",
      "title": "Automatic recovery context is injected only from the exact Git repository or worktree ledger root, never an unrelated non-Git manager directory",
      "disposition": "active"
    },
    {
      "id": "OUT-002",
      "title": "Contract-source guidance excludes planned write targets and generated regression evidence without adding a new runtime gate or planning phase",
      "disposition": "active"
    },
    {
      "id": "OUT-003",
      "title": "Every Littlepowers starter prompt is accepted by Codex 0.147.0 and current plugin metadata remains valid",
      "disposition": "active"
    },
    {
      "id": "OUT-004",
      "title": "The release is validated honestly against current Codex, Claude Code, and Qoder host boundaries with no model or effort override in Littlepowers",
      "disposition": "active"
    },
    {
      "id": "OUT-005",
      "title": "Littlepowers v1.3.1 is published from an exact CI-green commit and installed consistently on the three local hosts",
      "disposition": "active"
    },
    {
      "id": "OUT-006",
      "title": "The patch adds no repository scan, prompt or transcript read, network access, background loop, schema migration, or ordinary model-call overhead",
      "disposition": "active"
    }
  ],
  "fidelity": []
}
```
<!-- /littlepowers:contract -->

<!-- littlepowers:plan-map:v1 -->
```json
{
  "mappings": [
    {
      "outcome": "OUT-001",
      "tasks": ["Task 1"],
      "evidence": ["test:hook-root-affinity", "inspection:constant-root-check"]
    },
    {
      "outcome": "OUT-002",
      "tasks": ["Task 2"],
      "evidence": ["test:contract-source-guidance", "inspection:source-authority-scenario"]
    },
    {
      "outcome": "OUT-003",
      "tasks": ["Task 2"],
      "evidence": ["test:codex-default-prompt-limit", "host:codex-plugin-validation"]
    },
    {
      "outcome": "OUT-004",
      "tasks": ["Task 3"],
      "evidence": ["host:current-host-matrix", "inspection:validation-levels"]
    },
    {
      "outcome": "OUT-005",
      "tasks": ["Task 3"],
      "evidence": ["build:exact-release-commit", "host:three-host-installation"]
    },
    {
      "outcome": "OUT-006",
      "tasks": ["Task 1", "Task 2"],
      "evidence": ["inspection:hook-runtime-boundary", "test:aggregate-regression"]
    }
  ]
}
```
<!-- /littlepowers:plan-map -->
