# Backlog.md

Feedback for [Backlog.md](https://github.com/MrLesk/Backlog.md), the leading task store in [the task-management prior-art note](../prior-art/2026-11-12-task-management-for-humans-and-agents.md). Read in source at 52b4ea3 (v1.55.3). None of these has been raised upstream.

## A task file can run a shell command

- **Where:** `src/core/backlog.ts:3347-3372`, `src/utils/status-callback.ts:26-60`.
- **What:** a task's frontmatter key `onStatusChange` is run as `sh -c <command>` when the task's status changes. A task file that arrives in a pull request, for example a task filed by another repo's agent, can carry a command that runs on the next status change, by a person or an agent.
- **Suggested fix:** take the callback only from the project config (or an allowlist there), never from a task file; or require an explicit config flag before per-task callbacks run.

## Dependency cycles are accepted on write

- **Where:** `src/utils/readiness.ts:1-121`; cycles are reported only by `backlog doctor` (`src/cli.ts:5920-5921`).
- **What:** a task edit that creates a dependency cycle is saved, and the cycle surfaces only when someone runs `doctor`.
- **Suggested fix:** reject the edit with the cycle's path, reusing `findCycleThroughRoot` (`src/utils/dependency-graph.ts:219`).

## Claiming a task isn't atomic

- **Where:** claims are status plus assignee by convention (`src/guidelines/agent-guidelines.md:95,386-387`); the per-task lock lasts only for one edit (`src/file-system/operations.ts:735-760`).
- **What:** two agents in parallel worktrees can both set a task to In Progress with themselves as assignee.
- **Suggested fix:** a `task claim` command that checks status and assignee and writes them under the existing lock in the git common directory, so the claim is shared across worktrees.

## ID generation fetches and prunes by default

- **Where:** `src/git/operations.ts:605-634`, `src/utils/id-generators.ts:45-60`.
- **What:** with the default `remoteOperations: true`, creating a task runs `git fetch origin --prune`, which deletes stale remote-tracking refs and needs the network.
- **Suggested fix:** document the side effect beside the setting, or make pruning a separate opt-in.
