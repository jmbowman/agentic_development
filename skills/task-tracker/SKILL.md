---
name: task-tracker
description: Record, pick up and finish work in a repo's task backlog, one Markdown file per task in Backlog.md's format under backlog/, ranked by a read-only task tool. Use when choosing what to work on next, when work is left outstanding beyond the current request (a loose end, a follow-up, a deferred spec, a decision the developer must make), when starting, finishing, editing, re-prioritising, pinning or holding back a task, when asked to change the backlog's focus file, when writing work for another repo, or when the task tool's check reports a problem. Not for work done now in the session that found it.
license: Apache-2.0
---

# Task tracker

A repo's outstanding work lives in its backlog directory (`backlog/` unless the repo says otherwise), one file per task. The file format, every key and the reference forms are in [references/task-format.md](references/task-format.md): read it before writing or editing a task by hand.

The task tool lints the files and ranks the ready work. It reads task files and never writes one. Run it as `mise run tasks -- <command>` where the repo has that task, otherwise as `uv run --script <this skill's directory>/scripts/tasks.py <command>`:

| Command | What it shows |
|---|---|
| `check` | Every problem in the backlog, one per line; exits 1 when there is any |
| `next --for agent` | The ready agent tasks, ranked, each with the terms behind its score (`--for human` for the developer's; `-n 0` for all; `--repo <outbox folder>` for an outbox's drafts) |
| `why <ID>` | One task: its rank, what it waits on and what waits on it |
| `board` | The whole backlog as one Markdown page on standard output |
| `brief` | A short summary for the start of a session |

Two options go before the command: `--offline` skips GitHub lookups, so GitHub blockers count as open, and `--private` also loads the private drafts in `backlog/private/outbox/`.

Tasks are created and edited with Backlog.md's `backlog` CLI, or by editing the file. Where a rule below differs from Backlog.md's own agent instructions (the block `backlog init` writes, or `backlog instructions`), this skill's rule applies.

## A repo with no backlog

If the repo has no backlog directory, don't create one, and don't run `backlog init`: setting up a backlog is the developer's decision. Tell the developer the repo has no backlog, and leave the outstanding work in your reply.

## When to create a task

Create a task for work left outstanding beyond the current request: a loose end, a follow-up, a deferred spec, a decision the developer must make. Record it without asking first, unless the workflow you are in asks the developer before it writes (a session wrap-up does): then that workflow's approval steps apply to the tasks it creates. Work done now, in the session that found it, needs no task.

## Recording work

1. **Search first.** Before creating a task, search the backlog for one that covers the same work: `backlog search "<query>"`, narrowed if needed with `--status`, `--task-type` or `--priority`, or a text search of the task files (`grep -ril "<words>" backlog/tasks`), which can also match labels and milestones. Don't list everything. If one covers the work, extend it or link to it instead of creating a duplicate.
2. **Size it.** One task is what one focused pull request would finish, for one performer. Use subtasks (`--parent <ID>`, which sets `parent_task_id`) for parts of one goal in one area, and `dependencies` for work across components. Split agent-doable work out of a task that waits on the developer, and link the two with `dependencies`; a task may depend on one created after it.
3. **Write it.** The description gives the why: the problem or trigger, and the context a reader can't recover from the code. Acceptance criteria (`--ac`) state testable behaviour, not implementation steps, and don't repeat the description. Leave the plan to whoever starts the task. `type` says what kind of work it is (a ruling only the developer can make is `decision`); `labels` say where it came from and never restate the type.
4. **Create it** with `backlog task create "<title>" -d "<description>" --priority <p> --type <t> -m <milestone ID>`, which assigns the ID and names the file. Never choose an ID yourself.
5. **Add the custom keys** to its frontmatter by editing the file, since the CLI has no option for them: `performer`, `effort`, `priority_set_by: agent`, and for an agent task `agent_tier`. Add a `sessions` record with role `created` (below).
6. **Run `check`** (`mise run tasks -- check`) and fix any problem it reports about the task.

Put the task in the milestone whose description covers it, naming the milestone by its ID.

## When the backlog CLI won't run

If `backlog task create` fails to run (the command is missing, or crashes), don't write the task file yourself and don't choose an ID: an ID picked by hand skips Backlog.md's check of other worktrees and branches, and can collide with one there. Tell the developer the CLI failed, with its error, and leave the outstanding work in your reply.

## Session records

When you create a task, start it and finish it, add a record for the current session to its `sessions` list, with role `created`, `worked` or `finished`. Take the session ID from the harness: in Claude Code, the `CLAUDE_CODE_SESSION_ID` environment variable, with `agent: claude-code`. Where the harness exposes no session ID, add no record. Never edit or remove an existing record.

## Doing the work

- Take the top of `next --for agent` unless the developer names a task.
- Read the task before changing it, including its `## Comments`, where the developer or a reviewer may have left guidance for whoever picks it up. Set `status: In Progress` when starting (`backlog task edit <n> -s "In Progress"`).
- Comments (`--comment "<text>" --comment-author <session>`) carry guidance, review remarks and questions that don't stop the work. A question that blocks the work becomes a `decision` task, with `performer: human`, that the work depends on. Progress goes in notes, not comments.
- Record the plan with `--plan` (which replaces it) or `--append-plan`, and progress with `--append-notes`, briefly and in time order.
- Don't widen the task silently: record extra work you find as a new task, or ask.
- Work through subtasks one at a time, and finish a parent only when all of its subtasks are `Done`.

## Finishing

- Tick an acceptance criterion (`--check-ac <n>`) only on evidence that the behaviour works, such as a passing test or an observed result. The presence of code, or a search hit, isn't evidence.
- Write a final summary (`--final-summary`) of what changed, why, how it was verified, and any risks, then set `status: Done`.
- A `decision` task's ruling is recorded in the document it governs (a design doc, a note, a config file), and the final summary links to it. Only when no document governs the choice does the final summary hold the ruling itself.
- Commits follow the repo's own policy; a commit message may cite the task.

## Milestones

Never change a milestone's `## Importance`, which is the developer's. You may draft or update its other sections for the developer's review, saying only what no single task says. Adding, renaming, archiving and removing milestones are the developer's.

## Work for another repo

Write work for another repo as a draft in `outbox/<outbox folder>/<slug>.md` in this repo's backlog directory, with the same keys as a task except `id` and `dependencies`, plus `target`: the receiving repo's forge path, `<host>/<owner>/<repo>`. Name this repo's files by URL and its tasks and specs by its forge path, in `references` and in the body alike. A task here that waits on the work names the draft in `external_blockers` as `<outbox folder>/<slug>`. The draft is the record; a message to a session in that repo, or an issue on it, is a way of delivering it.

Work that can't be public, for any repo, goes in a draft in a private outbox:
1. in the private coordination repo's backlog, as `outbox/<outbox folder>/<slug>.md`, when the per-machine task-tracker settings (`$XDG_CONFIG_HOME/task-tracker/config.yml`, or `~/.config/task-tracker/config.yml` when that variable is unset) set `private_root` to its checkout and it has a backlog directory;
2. otherwise, if the repo's main checkout has a `backlog/private/` folder, in its `backlog/private/outbox/<outbox folder>/`, in the main checkout, not a worktree;
3. otherwise write no draft, and tell the developer.

Never name a private repo, or reference a private draft, in a public repo's tasks, drafts or references.

**Delivering a draft** is done by whoever delivers it, the developer or a session in the receiving repo:
1. The receiving repo creates the task with its own ID and lists the sending task in its `references` by forge path, unless the sending repo is private and the receiving one public.
2. In the sending repo, replace every `<outbox folder>/<slug>` reference to the draft with the new task's `<host>/<owner>/<repo>#<ID>`, delete the draft, and run `check`.

## Authority

- Never edit `focus.yml`, even when the developer asks you to: show the developer the exact edit to make instead.
- Never change a `priority` whose `priority_set_by` is `human`: propose the change to the developer instead.
- Leave `assignee` empty, and don't assign yourself: `performer` says who does a task.
- Deleting a task (`task delete`) is the developer's call.

## Editing

- Edit tasks through `backlog task edit` or directly in the file, never by moving cards in `backlog board`, which rewrites neighbouring cards. Never add `onStatusChange`.
- Several `task edit` options replace a whole list rather than add to it: `--acceptance-criteria`, `--dep`, `--ref`, `-l`, `--notes` and `-a`. Add with `--add-ref`, `--add-label` and `--append-notes`. To add a dependency, pass the full list to `--dep`. Tick criteria with repeated `--check-ac <n>`.
- In shell commands, put text containing backticks in single quotes. Build multi-line text by repeating an `--append-*` option, not with heredocs or `$'…'`.
- Never set a task's status to `Draft` or run `backlog task demote`: Backlog.md then moves the task to its drafts, gives it a new ID, and removes the old ID from every other task's `dependencies` and `references`.
- Task file names contain spaces (`ad-12 - Title.md`): quote them, and match one by ID with an escaped glob, `backlog/tasks/ad-12\ -\ *.md`.

## Duplicate IDs

When `check` reports an ID that two files use, as can happen when branches made on different machines merge, the task whose file reached the repo later takes a new ID. Find out which with `git log --diff-filter=A --format=%ci -- <file>` on each file; a `created_date` can't tell, since tasks made on the same day share one. If the history doesn't settle it, ask the developer which to renumber. Then:
1. Rename its file and change its `id` to the next free ID.
2. Update every reference to the old ID that its own branch added, in tasks, docs, notes and specs alike.
3. Run `check`.

## What not to use

These parts of Backlog.md stay unused, whatever its own instructions say:
- reading `backlog instructions overview` at every session start;
- `task list` to choose work (use `next`);
- the `documentation` key or `--doc` (links go in `references`);
- Definition of Done checklists (`--dod`, the `definition_of_done` config key): the finishing rules above cover them;
- its drafts (`task create --draft`, `draft …`), `backlog doc`, `backlog decision`, its MCP tools, `board export` (which writes a board into a tracked file) and `agents --update-instructions` (which edits agent instruction files);
- `doctor --fix`, which renumbers duplicate IDs without updating references. Plain `backlog doctor`, which only reports, is fine.
