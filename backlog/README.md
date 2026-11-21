# Backlog

Every piece of outstanding work for this repo, one Markdown file per task, in [Backlog.md](https://github.com/MrLesk/Backlog.md)'s file format with a few extra keys. The [task-tracker skill](../skills/task-tracker/SKILL.md) holds the tool that lints and ranks these files and the rules agents follow; [its format reference](../skills/task-tracker/references/task-format.md) describes every file, key and reference form.

## Commands

| Command | What it does |
|---|---|
| `mise run tasks -- next --for human` | The developer's ready tasks, ranked, with the terms behind each score (`--for agent` for agents; `-n 0` for all; `--repo <name>` for an outbox) |
| `mise run tasks -- why AD-12` | One task's score, what it waits on and what waits on it |
| `mise run tasks -- board` | The whole backlog as one Markdown page on standard output, with links relative to the directory it ran in |
| `mise run tasks -- check` | Lints every task; `mise run check` runs it through the test suite |
| `mise run tasks -- brief` | The short summary meant for a session-start hook |
| `backlog board`, `backlog browser` | Backlog.md's own terminal and web boards over the same files (pinned in `mise.toml`; `mise install` installs it) |

In an interactive shell where mise is activated, `tasks` is an alias for `mise run tasks`, so `tasks next --for human` works inside this repo, and `tasks help` lists the commands. Scripts, CI and agents' shells don't load the alias and use the full form.

Two options go before the command. `--offline` skips GitHub lookups, so blockers on GitHub count as open. `--private` also loads the drafts under `private/outbox/`.

## What's particular to this repo

- **Task IDs** start with `AD-` (`task_prefix: ad` in `config.yml`).
- **GitHub issues** are the public way in: each task made from an issue lists it in `references`, and the issue is closed when those tasks are done.
- **Private drafts** live in the gitignored `private/outbox/<repo>/`, in the main checkout, until the private coordination repo has a backlog.
- **Backlog.md's settings.** `config.yml` is written by hand rather than by `backlog init`. `remote_operations: false` keeps creating a task from running `git fetch origin --prune`, `auto_commit: false` leaves commits to the developer, and there is no status callback. `backlog init` isn't run, because by default it adds instructions to `AGENTS.md` and registers MCP config for several agents.
- **The contract test.** `tests/test_backlog_md.py` runs the pinned Backlog.md CLI to check that an edit keeps every custom key, so an upgrade that drops one fails `mise run check`.
- **The pilot.** The tracker started as a pilot; [docs/task-tracking-pilot.md](../docs/task-tracking-pilot.md) records what it found. The design is now [the task-tracker LLD](../docs/intent/task-tracker/task-tracker-design.md).
