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

const MAX_SESSIONS = 128;
const MAX_MESSAGES = 256;

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

const isRecoveryPart = (part) =>
  part?.type === 'text' && part.synthetic === true &&
  typeof part.text === 'string' && part.text.startsWith(`${INJECT_PREFIX}\n`);

const injectContext = (message, context) => {
  // Mark synthetic recovery parts so a lifecycle change can replace our block
  // without deleting a user's ordinary text that happens to quote the prefix.
  const text = `${INJECT_PREFIX}\n${context}`;
  const existing = message.parts.find(isRecoveryPart);
  if (existing) {
    existing.text = text;
    message.parts = message.parts.filter((part) => !isRecoveryPart(part) || part === existing);
  } else {
    message.parts.unshift({...message.parts[0], type: 'text', synthetic: true, text});
  }
};

export const LittlepowersPlugin = async ({ directory }) => {
  // A plugin instance belongs to one workspace. Never share ledger context or
  // child-session observations with another instance, even for identical IDs.
  const sessions = new Map();
  const anonymousMessages = new WeakMap();
  let nextAnonymousId = 0;
  const messageId = (message) => {
    if (typeof message.info.id === 'string' && message.info.id) return message.info.id;
    // Without a native ID, only the same object is safely identifiable. Do not
    // retain prompt text or guess that two identical prompts are one message.
    if (!anonymousMessages.has(message)) anonymousMessages.set(message, ++nextAnonymousId);
    return anonymousMessages.get(message);
  };
  const sessionFor = (id) => {
    const session = sessions.get(id) || { child: false, generation: 0, messages: new Map() };
    sessions.delete(id);
    sessions.set(id, session);
    if (sessions.size > MAX_SESSIONS) sessions.delete(sessions.keys().next().value);
    return session;
  };

  return {
    config: async (config) => {
      try {
        config.skills = config.skills || {};
        config.skills.paths = config.skills.paths || [];
        if (!config.skills.paths.includes(SKILLS_DIR)) config.skills.paths.push(SKILLS_DIR);
      } catch {
        // Fail open: skill discovery must not break session startup.
      }
    },

    event: async ({ event }) => {
      try {
        const info = event?.properties?.info;
        if (!info?.id) return;
        if (event.type === 'session.deleted') sessions.delete(info.id);
        if (event.type === 'session.created') {
          const session = sessionFor(info.id);
          const child = Boolean(info.parentID);
          if (session.child !== child) {
            session.messages.clear();
            session.generation += 1;
          }
          session.child = child;
        }
      } catch {
        // Fail open.
      }
    },

    'experimental.chat.messages.transform': async (_input, output) => {
      try {
        // Host transforms may reconstruct messages each step. Cache the hook
        // result, then reapply it to each representation instead of assuming a
        // prior in-memory insertion persists in the host's next input.
        const groups = new Map();
        for (const message of output.messages) {
          if (message?.info?.role !== 'user' || !message.parts?.length) continue;
          const id = message.info.sessionID || null;
          if (!groups.has(id)) groups.set(id, []);
          groups.get(id).push(message);
        }
        for (const [sessionId, messages] of groups) {
          const session = sessionFor(sessionId);
          const generation = session.generation;
          const first = messages[0];
          const last = messages[messages.length - 1];
          const boundary = messageId(last);
          const candidates = [{message: first, event: session.child ? 'SubagentStart' : 'SessionStart'}];
          if (last !== first) candidates.push({message: last, event: session.child ? 'SubagentStart' : 'UserPromptSubmit'});
          for (const {message, event} of candidates) {
            if (sessions.get(sessionId) !== session || session.generation !== generation) break;
            const id = messageId(message);
            let entry = session.messages.get(id);
            if (!entry || entry.event !== event || (!entry.context && !entry.pending && entry.boundary !== boundary)) {
              entry = {event, boundary, context: null, pending: null};
              // Store the pending attempt before awaiting it. Concurrent host
              // transforms share one subprocess per message/boundary.
              entry.pending = runRecoveryHook(event, directory);
              session.messages.set(id, entry);
              if (session.messages.size > MAX_MESSAGES) session.messages.delete(session.messages.keys().next().value);
            }
            if (entry.pending) {
              entry.context = await entry.pending;
              entry.pending = null;
            }
            // A lifecycle event may reset/delete this session while its hook
            // is pending. Do not inject a superseded coordinator/worker result.
            if (sessions.get(sessionId) !== session || session.generation !== generation) break;
            if (session.messages.get(id) !== entry) continue;
            if (entry.context) injectContext(message, entry.context);
          }
        }
      } catch {
        // Fail open: never break an agent step for recovery context.
      }
    },
  };
};
