# Backlog (pilot)

Every piece of outstanding work for this repo, one Markdown file per task, in [Backlog.md](https://github.com/MrLesk/Backlog.md)'s file format with a few extra keys. A small tool, [`scripts/tasks.py`](../scripts/tasks.py), lints the files, works out what is ready, and ranks it separately for the developer and for agents. This is a pilot: the design it tries, and what it found, are in [docs/task-tracking-pilot.md](../docs/task-tracking-pilot.md).

Start with [BOARD.md](BOARD.md), the generated view.

## Commands

| Command | What it does |
|---|---|
| `mise run tasks -- board` | Regenerates `BOARD.md`: both ready queues, bottlenecks, blocked tasks, drafts for other repos, everything by milestone |
| `mise run tasks -- next --for human` | The developer's ready tasks, ranked, with the terms behind each score (`--for agent` for agents; `-n 0` for all; `--repo <name>` for an outbox) |
| `mise run tasks -- why AD-12` | One task's score, what it waits on and what waits on it |
| `mise run tasks -- check` | Lints every task; also runs in `mise run check` |
| `mise run tasks -- brief` | The short summary meant for a session-start hook |
| `backlog board`, `backlog browser` | Backlog.md's own terminal and web boards over the same files (pinned in `mise.toml`; `mise install` installs it) |

In an interactive shell where mise is activated, `tasks` is an alias for `mise run tasks`, so `tasks board` and `tasks next --for human` work inside this repo, and `tasks help` lists the commands. Scripts, CI and agents' shells don't load the alias and use the full form.

Two options go before the command. `--offline` skips GitHub lookups, so blockers on GitHub count as open. `--private` also loads the drafts under `private/`, and `board` then writes `private/BOARD.md` and leaves the public board alone.

## What's where

| Path | Holds | Who writes it |
|---|---|---|
| `tasks/` | This repo's tasks, `ad-<n> - <Title>.md` | Agents and the developer |
| `focus.yml` | The developer's pins and ranking weights | The developer only |
| `outbox/<repo>/` | Task drafts for other repos, named by a slug; the receiving repo assigns the ID and priority | Agents draft; the developer delivers |
| `private/outbox/<repo>/` | The same, for anything that can't be public (gitignored), including work for this repo that came from a private source | Agents draft; the developer delivers |
| `milestones/` | The themes tasks are grouped under | The developer |
| `BOARD.md` | The generated view | The tool |
| `config.yml` | Backlog.md's settings: no remote operations, no auto-commit, no status callbacks | The developer |

## How Backlog.md is set up here

Backlog.md is pinned in `mise.toml`, and `config.yml` is written by hand rather than by `backlog init`. Three choices keep it from doing more than read and write task files:

- **`remote_operations: false`.** Otherwise, creating a task runs `git fetch origin --prune`, which needs the network and deletes stale remote-tracking branches.
- **`auto_commit: false`** (its default). Agents don't commit in this repo.
- **No `backlog init`.** By default it adds a block to `AGENTS.md` telling agents to run `backlog instructions overview` at the start of every conversation, and its MCP mode writes user-level config for several agents. To initialize another repo with it, pass `--agent-instructions none` and choose the CLI mode.

`tests/test_backlog_md.py` runs the pinned CLI to check that an edit keeps the custom keys below, so an upgrade that drops them fails `mise run check`.

## A task's keys

Backlog.md's own keys keep their meaning: `id`, `title`, `status` (`To Do`, `In Progress`, `Done`), `priority` (`high`, `medium`, `low`), `type`, `milestone`, `dependencies` (IDs in this backlog), `parent_task_id`, `due_date`, `references`, `labels`. Backlog.md keeps keys it doesn't know when it rewrites a file, which is what lets the rest live beside them:

| Key | Values | Meaning |
|---|---|---|
| `performer` | `human`, `agent` | Who does it. A task needing both is split in two, linked by `dependencies` |
| `agent_tier` | `fast`, `moderate`, `strong` | For agent tasks: the weakest model class suited to it |
| `effort` | `S`, `M`, `L` | Well under an hour, about a session, several sessions |
| `external_blockers` | `gh:owner/repo#N`, `repo#AD-12`, `repo/slug` | Blockers outside this backlog: a GitHub issue or pull request, a task in another repo, or an outbox draft. One that can't be read counts as open, and isn't a lint finding: today that includes every task in another repo, since only this backlog is read |
| `deadline_kind` | `hard`, `soft`, `target` | How firm `due_date` is |
| `defer_until` | a date | Not ready before this date |
| `waiting` | free text | Who is waiting for it |
| `priority_set_by` | `agent`, `human` | Who last set `priority`; every task starts as `agent` |

`type` is one of `decision`, `feature`, `bug`, `chore`, `docs`, `spike`, `eval`, `upstream`, `review`. A `decision` is always the developer's.

## Ready and ranked

A task is **ready** when it is open, every dependency is `Done`, every external blocker is closed, its `defer_until` has passed and it has no open subtask.

Ready tasks are ordered in three tiers: the developer's pins in `focus.yml`, in their order; then hard deadlines within a week; then by score. The score adds a term for priority, for how many open tasks wait on this one (directly or through others), for a nearing deadline, for work in progress, for small effort, for someone waiting and for age. Every listing prints the terms, and the weights can be changed in `focus.yml`.

## Rules for agents

- When asked to pick up work, take it from `next --for agent`. Set `status: In Progress` when starting and `Done` when finished, and say in the task what was done.
- Record new work for this repo with `backlog task create "<title>" -d "<description>" --priority <p> --type <t> -m <milestone id>`, which assigns the ID and names the file. Then add `performer`, `effort`, `priority_set_by: agent` and, for an agent task, `agent_tier` to its frontmatter. Work for another repo is a file under `outbox/<repo>/` named by a short slug, with the same keys and no `id` or `dependencies`. Run `check` afterwards.
- Never edit `focus.yml`, and never change a `priority` whose `priority_set_by` is `human`. Propose the change in the conversation instead.
- A task file never carries `onStatusChange`: Backlog.md runs that key as a shell command.
- Split a task rather than leave agent-doable work inside one that waits on the developer.
