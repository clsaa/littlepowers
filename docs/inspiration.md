# Inspiration and provenance

Littlepowers was designed after reviewing [Superpowers](https://github.com/obra/superpowers) v6.1.1 at commit `d884ae04edebef577e82ff7c4e143debd0bbec99`, released under the MIT License.

## Concepts that informed the design

- explicit skills for brainstorming and planning;
- native packaging for Codex and Claude Code;
- a SessionStart recovery hook;
- implementation plans with verification evidence;
- root-cause-first debugging and completion evidence gates;
- read-only change review with acceptance and quality assessment;
- isolated delegated work when the host supports it.

## Independent implementation

Littlepowers is not a fork and does not depend on the Superpowers package. Its Python ledger, schemas, Hook behavior, skill text, tests, manifests, and documentation were implemented independently for this repository.

Littlepowers differs deliberately:

- direct and compact routes avoid mandatory full ceremony;
- a revisioned worktree-local ledger carries recovery state;
- UserPromptSubmit refreshes state at prompt boundaries;
- the host, not the plugin, owns subagent orchestration;
- debugging, verification, and review are proportional skills rather than mandatory ceremony for every edit;
- no telemetry, transcript parsing, automatic commits, or branch workflow is included;
- Codex and Claude Code share one state and skill core.

Littlepowers is not affiliated with, sponsored by, or endorsed by obra or the Superpowers project. The name indicates historical inspiration, not an official relationship.

If future contributions copy upstream code or prose, preserve the applicable copyright and license notices and identify the source in the pull request.
