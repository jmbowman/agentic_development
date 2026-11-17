# Backlog.md

Feedback for [Backlog.md](https://github.com/MrLesk/Backlog.md), the leading task store in [the task-management prior-art note](../prior-art/2026-11-12-task-management-for-humans-and-agents.md). Read in source at 52b4ea3 (v1.55.3), and checked by running 1.55.3 in a sandbox on 2026-11-14 (the note's "Verified by running"). None of these has been raised upstream.

## A task file can run a shell command

- **Where:** `src/core/backlog.ts:3347-3372`, `src/utils/status-callback.ts:26-60`.
- **What:** a task's frontmatter key `onStatusChange` is run as `sh -c <command>` when the task's status changes. A task file that arrives in a pull request, for example a task filed by another repo's agent, can carry a command that runs on the next status change, by a person or an agent.
- **Evidence:** read in source; confirmed by running: `onStatusChange: "touch CALLBACK_RAN"` in a task file ran when `backlog task edit 1 -s Done` changed its status.
- **Suggested fix:** take the callback only from the project config (or an allowlist there), never from a task file; or require an explicit config flag before per-task callbacks run.

## Claiming a task isn't atomic

- **Where:** claims are status plus assignee by convention (`src/guidelines/agent-guidelines.md:95,386-387`); the per-task lock lasts only for one edit (`src/file-system/operations.ts:735-760`).
- **What:** two agents in parallel worktrees can both set a task to In Progress with themselves as assignee.
- **Suggested fix:** a `task claim` command that checks status and assignee and writes them under the existing lock in the git common directory, so the claim is shared across worktrees.

## ID generation fetches and prunes by default

- **Where:** `src/git/operations.ts:605-634`, `src/utils/id-generators.ts:45-60`.
- **What:** with the default `remoteOperations: true`, creating a task runs `git fetch origin --prune`, which deletes stale remote-tracking refs and needs the network.
- **Evidence:** read in source; confirmed by running: creating one task deleted a stale `origin/stale` ref, and with `remote_operations: false` the next create left another in place.
- **Suggested fix:** document the side effect beside the setting, or make pruning a separate opt-in.

## `init --defaults` writes an always-run instruction into `AGENTS.md`

- **Where:** `src/core/init.ts:276-300`, `src/agent-instructions.ts:126-210`.
- **What:** a non-interactive `init --defaults` creates (or appends to) `AGENTS.md` with a block marked `<CRITICAL_INSTRUCTION>` telling agents to run `backlog instructions overview` at the start of every conversation. Repos that keep `AGENTS.md` hand-written, or deliver live state through a SessionStart hook instead, have to pass `--agent-instructions none`.
- **Evidence:** confirmed by running `init Test --defaults` in an empty repo: it created a 24-line `AGENTS.md` and `backlog/config.yml`, and nothing else.
- **Suggested fix:** default to no agent instructions in non-interactive mode, or say in the init summary which files it changed.

## The terminal viewer pulls backticked paths out of their sentences

- **Where:** `src/ui/code-path.ts:45-97` (`transformCodePaths`), applied to the description, checklist items, plan, notes, comments and summary in `src/ui/task-viewer-with-search.ts:1703-1807`.
- **What:** in the terminal task view, any backticked string with a slash or a file extension is removed from its line and listed on a line of its own after that line's text, unless it is the line's only path and fewer than ten other characters remain. A sentence that names several paths loses them: "the extra files in `backlog/` (`focus.yml`, `BOARD.md`, `README.md`, `outbox/`) don't confuse it" shows as "the extra files in ( , , , ) don't confuse it", with the paths listed below the paragraph. Backticked strings without a slash or extension (`performer`) stay in place. The `--plain` output keeps paths in place (`transformCodePathsPlain`), so agents aren't affected. In the same view, `**bold**` markers showed as typed (seen, not traced in source).
- **Evidence:** seen by the developer in the terminal board on 2026-11-17 (task AD-1), then read in source at v1.55.3.
- **Suggested fix:** style a path where it stands, as the isolated-path branch already does, and never move it.

## Dependency cycles: check MCP edits

- **What:** the CLI refuses an edit that would create a cycle ("These dependencies would create a cycle: TASK-2 -> TASK-1 -> TASK-2"), confirmed by running. An earlier source reading found only `backlog doctor` reporting cycles (`src/utils/readiness.ts:1-121`, `src/cli.ts:5920-5921`), so the MCP `task_edit` path may not refuse them; this hasn't been checked.
- **Suggested fix, if MCP doesn't refuse them:** the same check there, reusing `findCycleThroughRoot` (`src/utils/dependency-graph.ts:219`).
