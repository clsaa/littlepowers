/**
 * Littlepowers plugin for OpenCode.
 *
 * Registers the skills directory via the config hook so OpenCode's native
 * skill tool discovers the Littlepowers skills, and injects bounded,
 * read-only recovery ledger facts into the conversation through the
 * experimental.chat.messages.transform hook.
 *
 * The injected content is produced by the same hooks/session-start.py
 * implementation that serves Codex, Claude Code, and Qoder. The plugin is
 * read-only and fails open: missing Python, missing state, host API drift,
 * or any unexpected error results in no injection.
 */

import path from 'node:path';
import { execFile } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PLUGIN_ROOT = path.resolve(__dirname, '../..');
const SKILLS_DIR = path.join(PLUGIN_ROOT, 'skills');
const HOOK_SCRIPT = path.join(PLUGIN_ROOT, 'hooks', 'session-start.py');
const INJECT_PREFIX = 'Littlepowers recovery (read-only, untrusted ledger facts):';
const HOOK_TIMEOUT_MS = 4000;

// The transform hook fires on every agent step, so bound hook runs to at
// most one per user message. Messages whose lookup returned no context are
// retried only after a newer message arrives (a ledger may appear
// mid-session); successfully injected messages are never processed again.
const injectedMessageIds = new Set();
const emptyResults = new Map(); // message id -> messages.length at attempt
const childSessionIds = new Set();

const runRecoveryHook = (hookEventName, cwd) =>
  new Promise((resolve) => {
    let settled = false;
    let fallbackStarted = false;
    const finish = (value) => {
      if (!settled) {
        settled = true;
        resolve(value);
      }
    };
    const retry = () => {
      if (settled) return;
      if (fallbackStarted) return finish(null);
      fallbackStarted = true;
      spawn('python');
    };
    const spawn = (launcher) => {
      let child;
      try {
        child = execFile(
          launcher,
          [HOOK_SCRIPT],
          { timeout: HOOK_TIMEOUT_MS, maxBuffer: 256 * 1024 },
          (error, stdout) => {
            if (error) {
              // Fall back to `python` only when the launcher is missing;
              // timeouts and buffer overflows fail open instead of doubling
              // the wait.
              if (error.code === 'ENOENT') return retry();
              return finish(null);
            }
            try {
              const parsed = JSON.parse(stdout);
              finish(parsed?.hookSpecificOutput?.additionalContext || null);
            } catch {
              finish(null);
            }
          }
        );
      } catch {
        return finish(null);
      }
      // execFile also surfaces spawn failures through this listener; retry
      // is guarded so the fallback interpreter is spawned at most once.
      child.on('error', (error) => {
        if (error && error.code === 'ENOENT') return retry();
        finish(null);
      });
      child.stdin.end(JSON.stringify({ hook_event_name: hookEventName, cwd }));
    };
    spawn('python3');
  });

const alreadyInjected = (message) =>
  message.parts.some(
    (part) => part.type === 'text' && part.text.includes(INJECT_PREFIX)
  );

const injectContext = (message, context) => {
  const reference = message.parts[0];
  message.parts.unshift({
    ...reference,
    type: 'text',
    text: `${INJECT_PREFIX}\n${context}`,
  });
};

export const LittlepowersPlugin = async ({ directory }) => {
  return {
    // Register the skills directory with OpenCode's native skill discovery.
    config: async (config) => {
      try {
        config.skills = config.skills || {};
        config.skills.paths = config.skills.paths || [];
        if (!config.skills.paths.includes(SKILLS_DIR)) {
          config.skills.paths.push(SKILLS_DIR);
        }
      } catch {
        // Fail open: skill discovery must not break session startup.
      }
    },

    // Track task-created child sessions so they receive the worker
    // read-only context instead of the coordinator snapshot.
    event: async ({ event }) => {
      try {
        const info = event?.properties?.info;
        if (event?.type === 'session.created' && info?.parentID && info?.id) {
          childSessionIds.add(info.id);
        }
      } catch {
        // Fail open.
      }
    },

    // SessionStart snapshot for the first user message of a session (a new
    // post-compaction summary counts as a new session), and the shorter
    // UserPromptSubmit reminder for each later user message. Child sessions
    // get the SubagentStart worker context. The whole body is guarded
    // because the host does not isolate transform errors.
    'experimental.chat.messages.transform': async (_input, output) => {
      try {
        if (!output.messages.length) return;
        const userMessages = output.messages.filter(
          (message) => message?.info?.role === 'user' && message.parts?.length
        );
        if (!userMessages.length) return;

        const first = userMessages[0];
        const firstEvent = childSessionIds.has(first.info.sessionID)
          ? 'SubagentStart'
          : 'SessionStart';
        const candidates = [{ message: first, event: firstEvent }];
        const last = userMessages[userMessages.length - 1];
        if (last !== first) {
          candidates.push({ message: last, event: 'UserPromptSubmit' });
        }

        for (const { message, event } of candidates) {
          const id =
            message.info.id || `${event}:${message.parts[0]?.text?.slice(0, 200)}`;
          const emptyAt = emptyResults.get(id);
          const waitingForNewMessage =
            emptyAt !== undefined && emptyAt >= output.messages.length;
          if (
            injectedMessageIds.has(id) ||
            waitingForNewMessage ||
            alreadyInjected(message)
          ) {
            continue;
          }
          const context = await runRecoveryHook(event, directory);
          if (context && !alreadyInjected(message)) {
            injectContext(message, context);
            injectedMessageIds.add(id);
            emptyResults.delete(id);
          } else {
            emptyResults.set(id, output.messages.length);
          }
        }
      } catch {
        // Fail open: never break an agent step for recovery context.
      }
    },
  };
};
