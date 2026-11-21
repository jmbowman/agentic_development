# Tasks and outbox drafts

How the wrap-up records loose ends and inferences as tasks in the repo's backlog, and work for another repo as outbox drafts. The backlog is one Markdown file per task in [Backlog.md](https://github.com/MrLesk/Backlog.md)'s format. Where the `task-tracker` skill is installed, follow its rules for creating a task, and its format reference for the keys; this file summarizes what a task item needs where it isn't. Either way, the wrap-up's own rules win: nothing is written without approval, a non-interactive run only reports, and nothing outside the approved items is changed.

## When the backlog can take task items

The backlog directory is `backlog/` at the repo root, unless a `backlog.config.yml` there names another with `backlog_directory`. Propose task items only when it exists. Its settings are in `config.yml` inside it (or in `backlog.config.yml`).

Propose no task item, and run no `backlog` command at all, when the settings don't set `remote_operations: false`, or set `auto_commit: true`: Backlog.md then runs `git fetch --prune` before every command, `search` included, and commits what it creates, both of which the git rule forbids. Search the task files as text instead, keep the loose ends as a plain list, and, when a loose end would otherwise have become a task item, say why in the report. Say the same, that the repo has no backlog, when there is no backlog directory.

## Which loose ends become task items

A loose end that names work for someone to do later, such as a promise not kept, a deferred fix, a parked question, an issue to file, or a draft the developer still needs, is proposed as a task item. Choosing the item records the work; it doesn't start it.

Never a task item:
- `Commit` and `Send` loose ends, background jobs, and the lists of uncommitted files: they are this session's own housekeeping;
- a loose end that only a compaction summary suggests: it stays a question.

A loose end you couldn't check against the current state is still proposed, and the task's description says it wasn't checked.

An inference (a conclusion you drew without checking it or hearing it from the developer) that passes the filter becomes one task item per inference, unless the instruction files name another pending queue: a `decision` task for `human`, labelled `inference`, so the developer rules on it before anyone acts on it. If that item isn't applied, the closing report lists the inference with the dropped lessons, not as a loose end.

A loose end that another repo owns becomes an outbox-draft item instead (see Outbox drafts), never a task in this repo.

## Search first

After checking the loose end against the current state, search the backlog's tasks, archived ones included, for one that covers the same work. Search with a query, not by listing every task: a text search of the backlog directory's `tasks/`, `archive/tasks/` and `completed/` (`grep -ril "<words>" <backlog>/tasks <backlog>/archive/tasks <backlog>/completed`, with the backlog directory's real path). Don't rely on `backlog search` alone: it searches only `tasks/`, never the archive, and it creates Backlog.md's empty folders (`decisions/`, `docs/`, `drafts/`, `milestones/`) where they're missing, which a report-only run must not do. An **open** task is one in `tasks/` whose `status` isn't `Done`.
- No task covers it: the item creates one.
- An open task covers it, and the session adds a fact that isn't already in its description, acceptance criteria, notes or comments (an observation, a new trigger, the problem happening again): the item adds a comment to that task.
- An open task already records everything: propose nothing, don't list the loose end, and name the task, by ID, under Skipped.
- A task that is `Done` or archived doesn't cover open work: the new task names it, by ID, in `references`.
- The open task that covers it lacks a required key (`title`, `status`, `priority`, `performer` or `effort`, and `agent_tier` on an agent task): the item adds the missing keys, by editing that task's file.

A loose end with a task item is listed only as the item. Search again before re-listing a task item carried from an earlier report: another session may have recorded the work since. A task item the developer declined isn't offered again in later runs, unless later evidence changes it; its loose end stays a plain loose end.

## What a task item records

| Loose end | `type` | `performer` |
|---|---|---|
| A `Decide` loose end, a parked question, an inference | `decision` | `human` |
| Other work only the developer can do or arrange, another person's review included | the type that fits, `chore` when none fits better | `human` |
| Work an agent could do | the type that fits | `agent`, with an `agent_tier` (`fast`, `moderate`, `strong`) |

A loose end that names both a step for the developer and a step for an agent is one item that creates two tasks: the developer's first, then the agent's. The agent's task's `dependencies` names the developer's only when the agent's step waits on it ("once I've decided, update the docs"); two steps that can go in either order get no dependency.

Every task the item creates also gets `effort` (`S`, `M` or `L`), a `priority` (`high`, `medium`, `low`), the milestone whose description covers the work (by its ID, or none), `priority_set_by` (`human` if the developer set or changed the priority at confirmation, otherwise `agent`), the label `loose-end` (or `inference` instead, for an inference), and, only where the harness exposes a session ID (in Claude Code, `CLAUDE_CODE_SESSION_ID`), a `sessions` record:

```yaml
sessions:
  - agent: claude-code
    id: <the session ID>
    role: created
    date: '<today>'
```

The description gives the problem or trigger and the context a reader can't recover from the code; acceptance criteria state testable behaviour. Screen the text as a draft is screened, to what the host repo can hold given its visibility and the instruction files' privacy rules: name no person, and give no private record or hint of one: not "once she's back from leave" but "once the reviewer is available". Text the host repo can't hold goes to the private outbox (below), not into the task.

## Showing and applying a task item

In the proposal, a task item's line gives the task's title, type, performer, priority and effort, and its destination: the backlog's `tasks/` directory for a new task, or the task's file for a comment or a key repair. A task item that records a `decision` task isn't a `Decide` item: don't ask for the decision's answer.

At confirmation, show every key the task will carry, those added after creation included, with "none" for an empty one: title, type, status, priority, `priority_set_by`, milestone, performer, effort, `agent_tier`, labels, references, dependencies and the `sessions` record; and its description and acceptance criteria. For an existing task, show the comment or the keys to add.

To apply:
1. Create the task with `backlog task create "<title>" -d "<description>" --ac "<criterion>" --priority <p> --type <t> [-m <milestone ID>] [--ref <ID>] [--dep <ID>]`, which assigns the ID and names the file: `--ref` for a `Done` or archived task the work follows from, `--dep` for the agent's task of a pair whose step waits on the developer's, naming the developer's task created just before; leave out `-m` when no milestone covers the work. For a description of several lines, put the line breaks inside the quoted text. Never write a task file yourself or choose an ID.
2. Edit the new file's frontmatter to add `performer`, `effort`, `agent_tier` for an agent task, `priority_set_by`, the label, and the `sessions` record. Creating and editing are one item.
3. Add a comment with `backlog task edit <ID> --comment "<text>" --comment-author "<the session ID, or session-wrap-up where the harness exposes none>"`. Add missing keys to an existing task by editing its file.
4. If the `backlog` CLI is missing, crashes or exits with an error, write no task file, leave the item open, and report the error. If the key edit fails after the task was created, report the item as part-applied, name the file, and leave it in place. A part-applied item counts as applied for later runs: their search finds the file and completes its keys.
5. After applying at least one task item, where the repo has a `tasks` mise task, run `mise run tasks -- check`. Report each finding about a task the run created or edited, with a proposed fix as text in the report, and change nothing to fix it.

Where the task-tracker skill says otherwise, the wrap-up's rules here win: it fixes no `check` finding itself, and `priority_set_by` is `human` when the developer changed the priority at confirmation.

Once the skill offers capturing items in an issue (not yet), the issue holds each task's keys, title, description and acceptance criteria, with no ID, and says the task is to be created with `backlog task create`.

## Outbox drafts

Work or feedback that another repo owns is an outbox draft in this repo's backlog directory, at `outbox/<receiving repo's name>/<slug>.md` (in the default layout, `backlog/outbox/…`). Search the outbox for a draft of the same work first; if one exists, propose no new draft, name the existing one under Skipped, and keep its `Send` loose end. A draft has a task's keys except `id` and `dependencies`, which the receiving repo assigns, plus `target`, the receiving repo's forge path (`<host>/<owner>/<repo>`, such as `github.com/example/csv-utils`):

```markdown
---
title: <what to change>
status: To Do
priority: medium
type: bug
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
labels:
  - loose-end
target: github.com/example/csv-utils
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
<One line stating the subject.>

What and why: <what to change, and why>.

Sources: <what to read: this repo's files by URL at its default branch, such as https://github.com/<owner>/<repo>/blob/main/<path> (take the host and owner from the instruction files, or by reading the `origin` URL in the repo's `.git/config`: the git rule allows no `git remote` or `git config` command), or by path when not yet pushed; its tasks and specs by forge path; the receiving repo's own files by path>.

Report back: <what the receiver should tell the developer when it's done. Ask for nothing this session was refused or the instruction files forbid (a release, a publish, a push): say instead that it's the developer's call>.
<!-- SECTION:DESCRIPTION:END -->
```

- Never ask the receiver to do something this session was refused (by a permission check, a hook or the developer) or that the instruction files forbid an agent to do; address that part to the developer instead.
- Screen the draft before showing it: leave out what the instruction files mark private, secrets and personal data, and restate each lesson as a general rule that names no particular user.
- Give the draft's full text in the report's Drafts section, so it can be judged before it is chosen.
- Write the draft as an approved item, after checking its path is free. Don't deliver it: send no message and file no issue for it. In the closing report, list each draft written, by path, with one `Send` loose end for it; a draft an earlier run wrote that is still in the outbox stays a `Send` loose end.
- With no backlog directory, the draft goes in the report's Drafts section for the developer to deliver, as an item that can't be applied in this run.

## The private outbox

Text that its destination repo can't hold, given that repo's visibility and the instruction files' privacy rules, goes to the private outbox as a draft, whether it is work for this repo or another. The private outbox is the first of these that exists; create neither:
1. the private coordination repo's `backlog/outbox/`, where the per-machine task-tracker settings (`$XDG_CONFIG_HOME/task-tracker/config.yml`, or `~/.config/task-tracker/config.yml` when that variable is unset) set `private_root` to a checkout with a backlog directory;
2. `backlog/private/outbox/` in this repo's main checkout, where `backlog/private/` exists.

With neither, the draft goes in the report. A private draft for this repo's own work goes in an outbox folder named for this repo. A draft for the private outbox is held to that repo's own privacy rules, with secrets always left out. Writing there is the one write outside this repo the skill makes, and only as an approved item whose full text the developer has seen, after checking its path is free. In a private repo, nothing its own rules allow is diverted.
