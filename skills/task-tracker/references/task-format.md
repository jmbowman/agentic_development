# Task file format

The format of a repo's backlog: what each file holds, every key the task tool reads, and the forms references take. It is [Backlog.md](https://github.com/MrLesk/Backlog.md)'s file format with a few custom keys, which Backlog.md keeps when it rewrites a file.

## The backlog directory

The backlog directory is `backlog/` at the repo root, unless a `backlog.config.yml` there names another with `backlog_directory`. Paths below are relative to it.

| Path | Holds | Written by |
|---|---|---|
| `config.yml` | Backlog.md's settings; the tool reads `project_name`, `task_prefix`, `statuses` and `types` | The developer |
| `tasks/` | Open and recently finished tasks, `<id> - <Title>.md` with the ID lower-cased | Agents and the developer, through `backlog task create` and edits |
| `archive/tasks/`, `completed/` | Tasks Backlog.md has archived, taken off its board whether finished or dropped | Backlog.md |
| `milestones/` | The workstreams tasks are grouped under, one file each | The developer, or an agent drafting for review |
| `focus.yml` | The developer's pins and ranking weights | The developer only |
| `outbox/<repo>/<slug>.md` | Drafts of tasks for another repo | Agents draft; the developer delivers |
| `.cache/` | The GitHub lookup cache, gitignored | The task tool |

The tool never reads Backlog.md's `drafts/`, `docs/` or `decisions/` folders, and nothing should be put there.

## A task file

YAML frontmatter between two `---` lines, then a Markdown body in the sections Backlog.md writes (`## Description`, `## Acceptance Criteria`, `## Implementation Plan`, `## Implementation Notes`, `## Comments`, `## Final Summary`). A key whose value is null, an empty string or an empty list counts as absent.

**Backlog.md's keys:**

| Key | Values | Meaning |
|---|---|---|
| `id` | `<PREFIX>-<n>`, with `.<n>` per level of subtask (`AD-12`, `AD-12.1`) | Assigned by `backlog task create`; never chosen by hand |
| `title` | Text | Required |
| `status` | One of `config.yml`'s `statuses`: `To Do`, `In Progress`, `Done` | Required. Anything but `Done` is open |
| `priority` | `high`, `medium`, `low` | Required |
| `type` | One of `config.yml`'s `types` (below) | What kind of work it is. Required when `config.yml` lists types |
| `labels` | A list | Where the task came from, such as `issue`, `loose-end` or `prior-art`; never a restatement of `type` |
| `milestone` | A milestone's ID, such as `m-1` | The workstream the task belongs to. Never its title or a bare number |
| `dependencies` | Task IDs in this backlog | The task isn't ready until each is `Done` |
| `parent_task_id` | A task ID | Makes this a subtask. A parent isn't ready while a subtask is open |
| `created_date` | A date | Set by `backlog task create` |
| `due_date` | A date | A deadline; how firm it is comes from `deadline_kind` |
| `references` | A list of URLs, paths in the repo, and the reference forms below | Everything a reader should open. The only list of links: Backlog.md's `documentation` key isn't used |

The types: `bug`, `chore`, `decision` (a ruling only the developer makes), `docs`, `eval`, `feature`, `review`, `search` (its main output is a research record, normally a prior-art search note), `spike` (a hands-on trial or probe) and `upstream` (feedback for a tool someone else maintains).

**Custom keys:**

| Key | Values | Meaning |
|---|---|---|
| `performer` | `human`, `agent` | Required. Who does the task. Work needing both is two tasks linked by `dependencies` |
| `agent_tier` | `fast`, `moderate`, `strong` | Required on an agent task: the weakest model class suited to it |
| `effort` | `S`, `M`, `L` | Required. Well under an hour; about a session; several sessions |
| `external_blockers` | A list in the forms below | Blockers outside this backlog |
| `deadline_kind` | `hard`, `soft`, `target` | How firm `due_date` is; `soft` when absent |
| `defer_until` | A date | The task isn't ready before this date |
| `waiting` | Text | Who is waiting for the task to be done |
| `priority_set_by` | `agent`, `human` | Who last set `priority`; `agent` when absent. Agents never change a priority set by `human` |
| `sessions` | A list of session records (below) | The agent sessions that created, worked on and finished the task |
| `target` | A forge path, `<host>/<owner>/<repo>` | Drafts only: the repo the draft is for |

A date is an ISO date, optionally with a time: `2026-12-01`, `2026-12-01 09:00` or `2026-11-17T12:18:00Z`. A task file never carries `onStatusChange`: Backlog.md runs its value as a shell command.

**Session records.** Each entry of `sessions` is a mapping with `agent` (the harness, such as `claude-code`), `id` (its session ID), `role` (`created`, `worked` or `finished`) and `date`. A session appears once per role. Records are added, never edited:

```yaml
sessions:
  - agent: claude-code
    id: 0b5c3f7e-1d2a-4c8b-9e6f-123456789abc
    role: created
    date: '2026-11-20'
```

## References between tasks and repos

A repo is named by its forge path, `<host>/<owner>/<repo>` (`github.com/jmbowman/agentic_development`). `external_blockers` takes three forms:

| Form | Names | Closed when |
|---|---|---|
| `gh:<owner>/<repo>#<number>` | A GitHub issue or pull request | The issue is closed as completed, or the pull request merged. One closed any other way still blocks |
| `<host>/<owner>/<repo>#<ID>` | A task in that repo's backlog, such as `github.com/jmbowman/copier-python#CP-12` | That task is `Done` on the repo's default branch |
| `<outbox folder>/<slug>` | A draft in this backlog's outbox, such as `copier-python/add-the-backlog-scaffolding` | Never: delivering the draft replaces the reference with the new task's forge-qualified ID |

A blocker the tool can't read (another repo's backlog it doesn't reach, a failed lookup) counts as open, so nothing starts by mistake; `why <ID>` shows it as unreadable. A public repo's tasks never name a private repo or reference a private draft.

A path in `references` must be tracked by git, or at least not ignored, so a reader of the repo on its forge can open it. Scratch files may be named in the body as local to a session.

## Outbox drafts

Work for another repo is a draft in `outbox/<outbox folder>/<slug>.md`, where the outbox folder is a short name for the repo (`outbox/copier-python/`) and the slug names the work. A draft has the keys of a task, plus `target`, and without `id` or `dependencies`, which the receiving repo assigns. Every draft in one folder has the same `target`. Its `priority` and `milestone` are proposals for the receiving repo.

A path or spec ID means nothing in the receiving repo, so a draft names this repo's files by URL and its tasks and specs by forge path (`github.com/jmbowman/agentic_development#AD-5`), in `references` and in its body alike.

## Milestones

A milestone file in `milestones/` has Backlog.md's frontmatter (`id`, `title`, optional `due_date`) and a body of up to four sections: `## Description` (what the workstream is for and what done looks like), `## Importance` (why it matters now; the developer's alone), `## Related` (one bullet per related milestone, its ID and how they relate) and `## References` (links to context outside the backlog). It never lists tasks or their status: the tool computes them.

## Other writers

Backlog.md's CLI is one way to write these files, and the one agents following the task-tracker skill use. Any tool or skill that follows this reference may write task files directly, for example one that must run with no dependencies. Such a writer assigns IDs itself, in the form above and not already used in `tasks/` or the archive folders, and so can collide with an ID made on another branch; `check` reports a collision when the branches meet.

## The focus file

`focus.yml` holds the developer's rulings, and only the developer edits it: `pins` (task IDs in the order they should be done), `weights` (overrides of the ranking weights), `milestones` (a ranking term per milestone ID) and `github_cache_hours`.
