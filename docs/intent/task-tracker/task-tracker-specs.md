# Task tracker specs

Design: [task-tracker-design.md](task-tracker-design.md). The terms below are used as follows:
- **The task tool:** the `task-tracker` skill's `scripts/tasks.py`, run through a repo's `tasks` mise task.
- **The backlog directory:** the directory TASK-LAYOUT-001 and TASK-LAYOUT-002 select. **The repo** is the git repository that holds it, and **the main checkout** is the repo's working tree that holds its `.git` directory, as opposed to a linked worktree.
- **The settings file:** the Backlog.md configuration TASK-LAYOUT-003 selects.
- **A task:** a `.md` file directly in the backlog directory's `tasks/` folder. **A draft:** a `.md` file directly in an outbox folder, `outbox/<outbox folder>/<slug>.md` or, with `--private`, `private/outbox/<outbox folder>/<slug>.md`. A spec that says "a task or draft" covers both; one that says only "a task" doesn't cover drafts. **An archived task:** a `.md` file in `completed/` or `archive/tasks/`. **A loaded task:** a task or draft the task tool has read and parsed.
- **An ID:** a task ID in the form TASK-LAYOUT-013 gives. **A forge path:** `<host>/<owner>/<repo>`, such as `github.com/jmbowman/agentic_development`.
- **A number:** a YAML integer or decimal, not a boolean, a quoted string, NaN or an infinity.
- **Open, ready, blocked:** open as TASK-LAYOUT-016 defines it; ready as TASK-READY-001 defines it; blocked means open and not ready, and "what it waits on" is the list TASK-READY-010 gives.
- **The developer's** and **agents'** tasks are those whose `performer` is `human` and `agent`.
- **The per-machine settings file:** `task-tracker/config.yml` under `$XDG_CONFIG_HOME`, or under `~/.config` when that variable is unset or empty.
- **Today:** the local date where the task tool runs.
- **The skill:** `skills/task-tracker/` in this repo (agentic_development), and **the agent** is an agent following it.

Lint findings for the data these specs describe are in the Lint section.

Specs marked *(eval)* describe the agent's behavior, and the skill's behavior evals verify them. Structure tests verify the other specs in the Skill section by checking that the skill's files name the specific commands, options, keys and values each rule depends on, not its wording; a rule that names none is verified by review. Tests of the task tool and of this repo's setup verify the rest.

## Layout

- [ ] **TASK-LAYOUT-001**: Where the repo's root holds a `backlog.config.yml` that sets `project_name` and a relative `backlog_directory`, the task tool shall use the directory `backlog_directory` names, relative to the repo's root, as the backlog directory; otherwise it shall use `backlog/` at the repo's root.
- [ ] **TASK-LAYOUT-002**: When the command line gives `--root <dir>`, the task tool shall use `<dir>` as the backlog directory, whatever TASK-LAYOUT-001 would select.
- [ ] **TASK-LAYOUT-003**: The task tool shall read Backlog.md's settings (`project_name`, `task_prefix`, `statuses`, `types` and the others the Lint section checks) from the repo root's `backlog.config.yml` when that file sets `project_name` and the command line gives no `--root`, and from `config.yml` in the backlog directory otherwise.
- [ ] **TASK-LAYOUT-004**: If the backlog directory or the settings file doesn't exist, or the settings file isn't a YAML mapping, then every task tool command except `help` shall print one line to standard error naming the path and the problem, and exit with status 2.
- [ ] **TASK-LAYOUT-005**: The task tool shall load every `.md` file directly in the backlog directory's `tasks/` folder as a task, and every `.md` file directly in `outbox/<outbox folder>/` as a draft, without descending into subfolders, and shall treat a missing folder as empty.
- [ ] **TASK-LAYOUT-006**: When the command line gives `--private`, the task tool shall also load every `.md` file directly in the backlog directory's `private/outbox/<outbox folder>/` as a draft; without `--private`, it shall not read that folder.
- [ ] **TASK-LAYOUT-007**: When a dependency, a blocker, a parent or a pin names an ID that no task has, the task tool shall look the ID up among the archived tasks, in `completed/` and then in `archive/tasks/`, by the `id` in each file's frontmatter.
- [ ] **TASK-LAYOUT-008**: The task tool shall show an archived task only where TASK-LAYOUT-007 looked it up (a blocker, a dependency, a lint finding, or `why` for its ID), never in a queue, on the board or in the brief.
- [ ] **TASK-LAYOUT-009**: The task tool shall not read a file in the backlog directory's `drafts/`, `decisions/` or `docs/` folder as a task or a draft.
- [ ] **TASK-LAYOUT-010**: The task tool shall not create, modify, rename or delete any file except files under the backlog directory's `.cache/` folder, including the temporary files it writes there.
- [ ] **TASK-LAYOUT-011**: The task tool shall take the repo's forge path from the URL of its `origin` remote, in HTTPS form, SSH form or `git@<host>:<owner>/<repo>` form, by removing the scheme, any user name and any port, writing the `:` after the host as `/`, and removing a trailing `.git` and a trailing `/`.
- [ ] **TASK-LAYOUT-012**: If the backlog directory isn't in a git repository, the repo has no `origin` remote, or `origin` is a local path or a `file:` URL, then the task tool shall treat the repo as having no forge path, so that no forge-qualified reference resolves to the repo's own tasks.
- [ ] **TASK-LAYOUT-013**: The task tool shall read an ID in the repo's own backlog as the settings file's `task_prefix`, matched as written but without regard to letter case and hyphens included (or, where it sets none, any run of letters), then a hyphen, a run of letters and digits, and zero or more parts each made of `.` and digits (`AD-12`, `AD-12.1`); an ID in another repo's reference may have any run of letters as its prefix.
- [ ] **TASK-LAYOUT-014**: The task tool shall compare IDs without regard to letter case, and shall show every ID as written but in upper case.
- [ ] **TASK-LAYOUT-015**: The task tool shall compare the numeric parts of IDs as numbers, so that `AD-01` and `AD-1` are the same ID.
- [ ] **TASK-LAYOUT-016**: The task tool shall treat a task or a draft as open when its `status`, compared without regard to letter case, isn't `Done`, including a missing `status` and a status a repo adds to its settings file.
- [ ] **TASK-LAYOUT-017**: The task tool shall treat an archived task as not open, whatever its `status`.
- [ ] **TASK-LAYOUT-018**: If the repo root's `backlog.config.yml` can't be parsed as a YAML mapping, or its `backlog_directory` is absolute or leads outside the repo, then every task tool command except `help` shall print one line to standard error naming the file and the problem, and exit with status 2.
- [ ] **TASK-LAYOUT-019**: The task tool shall compare forge paths without regard to letter case.

## Task files

- [ ] **TASK-FILE-001**: The task tool shall read a task or draft file as YAML frontmatter, between a first line `---` and the next line `---`, followed by a Markdown body, ignoring a byte-order mark and accepting CRLF line ends.
- [ ] **TASK-FILE-002**: The task tool shall read these keys of Backlog.md's from the frontmatter of a task or a draft: `id`, `title`, `status`, `priority`, `type`, `labels`, `milestone`, `dependencies`, `parent_task_id`, `created_date`, `due_date` and `references`.
- [ ] **TASK-FILE-003**: The task tool shall read these custom keys from the frontmatter of a task or a draft: `performer`, `agent_tier`, `effort`, `external_blockers`, `deadline_kind`, `defer_until`, `waiting`, `priority_set_by` and `sessions`, and, from a draft's, `target`.
- [ ] **TASK-FILE-004**: The task tool shall ignore Backlog.md's `updated_date`, `reporter`, `project`, `ordinal`, `subtasks`, `assignee` and `documentation` keys when computing readiness, rank and views.
- [ ] **TASK-FILE-005**: The task tool shall take a task's subtasks to be the tasks whose `parent_task_id` names its ID, and shall not read the task's own `subtasks` list.
- [ ] **TASK-FILE-006**: When a date value (`created_date`, `due_date` or `defer_until`) holds no time zone, the task tool shall read the ISO date it starts with as written; a time may follow the date after `T` or a space, with or without seconds.
- [ ] **TASK-FILE-007**: When a date value holds a time with a time zone (`Z` or a numeric offset), the task tool shall convert that time to the local date where the task tool runs.
- [ ] **TASK-FILE-008**: The task tool shall count days between dates in whole calendar days.
- [ ] **TASK-FILE-009**: The task tool shall treat a task without `priority_set_by` as having `priority_set_by: agent`.
- [ ] **TASK-FILE-010**: The task tool shall treat a task that has a `due_date` and no `deadline_kind`, or a `deadline_kind` other than `hard`, `soft` and `target`, as having `deadline_kind: soft`.
- [ ] **TASK-FILE-011**: The task tool shall treat a task's `waiting` as set only when it holds text other than white space.
- [ ] **TASK-FILE-012**: The task tool shall read an entry of `external_blockers` in one of three forms: `gh:<owner>/<repo>#<number>` (a GitHub issue or pull request), `<host>/<owner>/<repo>#<ID>` (a task in that repo's backlog) and `<outbox folder>/<slug>` (a draft in the repo's own outbox).
- [ ] **TASK-FILE-013**: When a `<host>/<owner>/<repo>#<ID>` blocker's forge path is the repo's own (TASK-LAYOUT-011, TASK-LAYOUT-019), the task tool shall resolve it to the task, or failing that the archived task, with that ID, and shall count it as closed only when that task's `status` is `Done`.
- [ ] **TASK-FILE-014**: The task tool shall count an `<outbox folder>/<slug>` blocker as open whether or not that draft exists in a loaded outbox folder, since delivering a draft replaces the blocker rather than closing it.
- [ ] **TASK-FILE-015**: If the task tool can't read an external blocker (a forge path with no usable clone, an ID its repo lacks, a failed GitHub lookup, a GitHub lookup skipped by `--offline`), then it shall count the blocker as open and show it with the reason it couldn't be read.
- [ ] **TASK-FILE-016**: The task tool shall take a task's links only from `references`.
- [ ] **TASK-FILE-017**: The task tool shall read each entry of a task's `sessions` as a mapping of `agent`, `id`, `role` and `date`.
- [ ] **TASK-FILE-018**: The task tool shall identify a draft as `<outbox folder>/<slug>`, where `<slug>` is its file name without `.md`, and shall take the repo it belongs to from its `target`.
- [ ] **TASK-FILE-019**: The task tool shall treat a key whose value is null, an empty string or an empty list as absent.
- [ ] **TASK-FILE-020**: The task tool shall read a single value given for `labels`, `dependencies`, `external_blockers` or `references` as a list holding that one value.
- [ ] **TASK-FILE-021**: The task tool shall compare `status` and `priority` values with the settings file's lists and with `Done`, `In Progress`, `high`, `medium` and `low` without regard to letter case, as Backlog.md does, and every other enumerated value exactly.
- [ ] **TASK-FILE-022**: The task tool shall never treat a draft as a subtask, and shall ignore a draft's `dependencies` and `parent_task_id` when computing readiness.

## Milestones

- [ ] **TASK-MS-001**: The task tool shall load each `.md` file directly in the backlog directory's `milestones/` folder as a milestone, reading `id`, `title` and `due_date` from its frontmatter and the sections `## Description`, `## Importance`, `## Related` and `## References` from its body.
- [ ] **TASK-MS-002**: The task tool shall resolve a task's `milestone` only as a milestone's frontmatter `id`, compared without regard to letter case, never as a milestone's title or as a bare number.
- [ ] **TASK-MS-003**: When a task's `milestone` names no milestone loaded from `milestones/`, the task tool shall look the ID up among the files in the backlog directory's `archive/milestones/` folder, by their frontmatter `id`.
- [ ] **TASK-MS-004**: The task tool shall read each bullet of a milestone's `## Related` section as the milestone ID it starts with, ending at the first character that is neither a letter, a digit nor a hyphen, followed by a phrase describing the relationship.
- [ ] **TASK-MS-005**: The task tool shall take a milestone's tasks, and their counts, from the tasks (not drafts) whose `milestone` is its ID, and shall not read progress from the milestone file.
- [ ] **TASK-MS-006**: The task tool shall treat a milestone's description as unfilled when its `## Description` section is missing, holds only white space, or holds only Backlog.md's placeholder `Milestone: <title>`.
- [ ] **TASK-MS-007**: The task tool shall take a milestone's first description sentence to be the text of its `## Description` section up to and including the first `.`, `!` or `?` that is followed by white space or ends the section, or the whole section's text when it has none.
- [ ] **TASK-MS-008**: If a milestone file's frontmatter can't be parsed as a YAML mapping, then the task tool shall leave it out of every view and computation (TASK-LINT-048 reports it).

## Focus file

- [ ] **TASK-FOCUS-001**: The task tool shall read `focus.yml` in the backlog directory as a mapping with four optional keys: `pins`, `weights`, `milestones` and `github_cache_hours`.
- [ ] **TASK-FOCUS-002**: If `focus.yml` doesn't exist, can't be parsed, or isn't a mapping, then the task tool shall use no pins, the default weights, no milestone weights and a 24-hour GitHub cache.
- [ ] **TASK-FOCUS-003**: The task tool shall read a `pins` value that is a single ID or draft name as a list holding that one entry, and shall count a pin listed more than once only at its first position.
- [ ] **TASK-FOCUS-004**: The task tool shall read each pin as an ID (TASK-LAYOUT-014) or, when it contains `/` and no `#`, as a draft named `<outbox folder>/<slug>`, compared as written; it shall ignore a pin containing `#`.
- [ ] **TASK-FOCUS-005**: When a `weights` entry names a ranking weight (the Ranking section) and its value is a number, the task tool shall use that number in place of the weight's default, negative numbers included.
- [ ] **TASK-FOCUS-006**: If a `weights` entry names no ranking weight, or its value isn't a number, then the task tool shall ignore the entry, so the weight it names, if any, keeps its default.
- [ ] **TASK-FOCUS-007**: When a `milestones` entry names a milestone ID loaded by TASK-MS-001 and its value is a number, the task tool shall use that number as the milestone ranking term for every task in that milestone.
- [ ] **TASK-FOCUS-008**: If a `milestones` entry names no loaded milestone, or its value isn't a number, then the task tool shall ignore the entry.
- [ ] **TASK-FOCUS-009**: When `github_cache_hours` is a positive number, the task tool shall keep GitHub answers in its cache for that many hours; otherwise it shall keep them for 24 hours.

## Other repos

- [ ] **TASK-XREPO-001**: The task tool shall read the per-machine settings file as a mapping with three optional keys: `private_root`, a path; `clone_roots`, a list of paths; and `repos`, a mapping from forge paths to paths; each path absolute or starting with `~/`.
- [ ] **TASK-XREPO-002**: The task tool shall expand a leading `~/` in every path in the per-machine settings file to the home directory.
- [ ] **TASK-XREPO-003**: If the per-machine settings file doesn't exist, then the task tool shall use no private root, no clone roots and no repo paths.
- [ ] **TASK-XREPO-004**: If the per-machine settings file can't be parsed, or one of its keys doesn't have the shape TASK-XREPO-001 gives, then every task tool command except `help` and `brief` shall print one line to standard error naming the file and the key, `brief` shall include that line in its own output, and the task tool shall ignore that key, or the whole file when it can't be parsed.
- [ ] **TASK-XREPO-005**: When resolving a forge path `<host>/<owner>/<repo>` other than the repo's own, the task tool shall try as its clone first the path the `repos` mapping gives for that forge path (TASK-LAYOUT-019), if any, and then `<root>/<repo>` under each of `clone_roots` in their order.
- [ ] **TASK-XREPO-006**: The task tool shall use a candidate directory from TASK-XREPO-005 as a clone only when it is a git repository whose `origin` remote, normalized as in TASK-LAYOUT-011, is the forge path being resolved, and shall otherwise try the next candidate.
- [ ] **TASK-XREPO-007**: The task tool shall read another repo's backlog from the commit that its clone's `refs/remotes/origin/HEAD` names, using `git show`, and never from that clone's working tree.
- [ ] **TASK-XREPO-008**: The task tool shall find another repo's backlog directory and settings by applying TASK-LAYOUT-001 and TASK-LAYOUT-003 to the files at the commit TASK-XREPO-007 names.
- [ ] **TASK-XREPO-009**: When reading another repo's backlog for a `<host>/<owner>/<repo>#<ID>` blocker, the task tool shall look for the task in `tasks/`, then `completed/`, then `archive/tasks/` at that commit, among the files whose names start with an ID equal to it (TASK-LAYOUT-014, TASK-LAYOUT-015) followed by ` - `, using a file only when its frontmatter `id` is also that ID, and shall count the blocker as closed only when that task's `status` is `Done`.
- [ ] **TASK-XREPO-010**: The task tool shall not fetch, pull, or change any file or ref in another repo's clone.
- [ ] **TASK-XREPO-011**: If no candidate directory is a usable clone, the clone has no `refs/remotes/origin/HEAD`, the commit has no backlog directory, or no task with the ID exists at that commit, then the task tool shall count the `<host>/<owner>/<repo>#<ID>` blocker as open and show it as unreadable with that reason; a task found only in `completed/` or `archive/tasks/` whose `status` isn't `Done` shall be shown as `archived without being done`.
- [ ] **TASK-XREPO-012**: The task tool shall read other repos' clones whether or not the command line gives `--offline`.

## Readiness

- [ ] **TASK-READY-001**: The task tool shall treat a task or draft as ready only when it is open (TASK-LAYOUT-016) and TASK-READY-002 to TASK-READY-005 all hold for it.
- [ ] **TASK-READY-002**: The task tool shall treat a task's dependencies as satisfied only when every ID in its `dependencies` names a task, or failing that an archived task, whose `status` is `Done`; a dependency that names nothing is never satisfied.
- [ ] **TASK-READY-003**: The task tool shall treat a task's external blockers as satisfied only when every entry of its `external_blockers` counts as closed under TASK-FILE-013, TASK-FILE-014, TASK-XREPO-009 and the GitHub lookup section.
- [ ] **TASK-READY-004**: The task tool shall treat a task as not deferred only when its `defer_until` is absent or is a date on or before today; a `defer_until` that isn't a date (TASK-FILE-006, TASK-FILE-007) defers the task indefinitely.
- [ ] **TASK-READY-005**: The task tool shall treat a task as free of subtasks only when none of its subtasks (TASK-FILE-005) is open.
- [ ] **TASK-READY-006**: The task tool shall give a task or draft that isn't open no blockers, and shall never look up its external blockers.
- [ ] **TASK-READY-007**: The task tool shall take an open task or draft to wait on each of its open dependencies, each open task or draft that one of its external blockers names in the repo's own backlog (TASK-FILE-013, or a draft named by an `<outbox folder>/<slug>` blocker), and each of its open subtasks.
- [ ] **TASK-READY-008**: The task tool shall count, as the tasks a task or draft unblocks, every other open task or draft that waits on it directly or through a chain of others under TASK-READY-007, counted over all loaded tasks and drafts before any queue's filters.
- [ ] **TASK-READY-009**: The task tool shall take a task to be in a cycle when it waits on itself through a chain under TASK-READY-007.
- [ ] **TASK-READY-010**: For a blocked task or draft, the task tool shall give as what it waits on every reason it isn't ready: each dependency that is open, names nothing, or names an archived task that isn't `Done`; each external blocker counted as open, with its reason; a deferral, with its `defer_until`; and each open subtask.

## Ranking

- [ ] **TASK-RANK-001**: The task tool shall build a queue from the ready tasks and drafts (TASK-READY-001) that match the queue's performer, repo and type, where the repo's own queue holds its tasks and no drafts, and an outbox folder's queue holds that folder's drafts.
- [ ] **TASK-RANK-002**: The task tool shall order a queue in three tiers: first the tasks and drafts named in the focus file's `pins`, in pin order (TASK-FOCUS-003); then those with `deadline_kind: hard` whose `due_date` is today, past, or at most seven days after today; then every other one.
- [ ] **TASK-RANK-003**: The task tool shall not add a pinned task to a queue whose performer, repo or type it doesn't match, and shall not treat a pinned task as ready unless TASK-READY-001 holds for it.
- [ ] **TASK-RANK-004**: Within the second and third tiers, the task tool shall order tasks and drafts by score, highest first, comparing scores before any rounding, and those with equal scores by ID, or for drafts by `<outbox folder>/<slug>`, in natural order (TASK-RANK-005).
- [ ] **TASK-RANK-005**: The task tool shall order IDs and draft names naturally: splitting each into runs of digits and runs of other characters, comparing run by run, digit runs as numbers and other runs as text without regard to letter case, a digit run before a text run, and a name before every longer name it begins (`AD-2` before `AD-12`, `AD-12` before `AD-12.1`).
- [ ] **TASK-RANK-006**: The task tool shall compute a task's or draft's score as the sum of the eight terms TASK-RANK-007 to TASK-RANK-014 give, each using its default weight unless the focus file overrides it (TASK-FOCUS-005).
- [ ] **TASK-RANK-007**: The priority term shall be the weight `priority_high` (default 6.0), `priority_medium` (3.9) or `priority_low` (1.8) matching the task's `priority` (TASK-FILE-021), and zero when `priority` is absent or none of `high`, `medium` and `low`.
- [ ] **TASK-RANK-008**: The unblocks term shall be the weight `unblocks` (default 8.0) times the smaller of 1 and the square root of n / 16, computed without integer division, where n is the number of tasks the task unblocks (TASK-READY-008).
- [ ] **TASK-RANK-009**: Where a task has a `due_date`, the deadline term shall be the weight `due` (default 12.0) times nearness times firmness, where nearness is 1 − 0.8 × (d + 7) / 21 limited to the range 0.2 to 1, d is the number of days from today to the `due_date` (negative when past), and firmness is 1.0 for `hard`, 0.6 for `soft` and 0.3 for `target` (TASK-FILE-010).
- [ ] **TASK-RANK-010**: The in-progress term shall be the weight `active` (default 4.0) when the task's `status` is `In Progress` (TASK-FILE-021), and zero otherwise.
- [ ] **TASK-RANK-011**: The effort term shall be the weight `effort_S` (default 2.0) when the task's `effort` is `S`, the weight `effort_M` (default 1.0) when it is `M`, and zero otherwise.
- [ ] **TASK-RANK-012**: The waiting term shall be the weight `waiting` (default 3.0) when the task's `waiting` is set (TASK-FILE-011), and zero otherwise.
- [ ] **TASK-RANK-013**: Where a task has a `created_date` on or before today, the age term shall be the weight `age` (default 2.0) times the smaller of 1 and the number of days since `created_date` divided by 365; for a `created_date` after today it shall be zero.
- [ ] **TASK-RANK-014**: The milestone term shall be the number the focus file's `milestones` mapping gives the task's milestone (TASK-FOCUS-007), and zero when it gives none.
- [ ] **TASK-RANK-015**: If a date a term uses (`due_date` for the deadline term, `created_date` for the age term) is absent or isn't a date, then that term shall be zero.
- [ ] **TASK-RANK-016**: Wherever the task tool shows a score, it shall show the score and each term whose value isn't zero with its label and its value rounded to one decimal place, in the order TASK-RANK-007 to TASK-RANK-014 give: `priority <priority>`, `unblocks <n> (<k> for agents)` where k counts the unblocked tasks and drafts whose `performer` is `agent`, `<deadline_kind> deadline in <d>d` (or `<deadline_kind> deadline overdue <d>d` when past, with d positive), `in progress`, `effort <effort>`, `<waiting> is waiting`, `age <days>d` and `milestone <ID>`.
- [ ] **TASK-RANK-017**: Wherever the task tool shows a pinned task's score, it shall show `pinned #<n>` before the terms, where n is the pin's first position in `pins`, counting from 1.

## GitHub lookup

- [ ] **TASK-GH-001**: When running `next`, `why`, `milestone`, `board` or `brief`, the task tool shall look up every `gh:` blocker of every open task and draft whose answer isn't fresh in the cache (TASK-GH-007).
- [ ] **TASK-GH-002**: The task tool shall look up the `gh:` blockers of one run that need it with `gh api graphql`, each distinct reference once, in as few requests as possible, each carrying at most 100 references and reading each one's state, whether a pull request was merged, and an issue's close reason.
- [ ] **TASK-GH-003**: If a lookup request hasn't finished 15 seconds after it started, then the task tool shall stop it and treat that request as failed (TASK-GH-008).
- [ ] **TASK-GH-004**: The task tool shall count a `gh:` blocker as closed only when GitHub reports the issue closed as completed, or closed with no close reason recorded, or the pull request merged.
- [ ] **TASK-GH-005**: When GitHub reports a blocker's issue closed with a recorded reason other than completed, or its pull request closed without being merged, the task tool shall count the blocker as open and show it as `closed without its work done`.
- [ ] **TASK-GH-006**: When GitHub reports a blocker's issue or pull request as not found or not accessible, the task tool shall count that blocker as open and show it as `not found`, and shall keep the answers the same request gave for every other blocker.
- [ ] **TASK-GH-007**: The task tool shall store each answer from GitHub, with the time it was received, in the backlog directory's `.cache/github.json`, and shall treat an answer as fresh while it is younger than the number of hours TASK-FOCUS-009 gives.
- [ ] **TASK-GH-008**: If a lookup request fails as a whole (no `gh` command, no network, not logged in, a timeout, or a response that isn't valid), then the task tool shall record every blocker the request carried as unreadable, fresh for ten minutes, except a blocker whose earlier answer is still fresh, which it shall keep.
- [ ] **TASK-GH-009**: When the command line gives `--offline`, the task tool shall send no request to GitHub, shall use whatever is still fresh in the cache (an unreadable record included), and shall count every other `gh:` blocker as open, shown as `not looked up`.
- [ ] **TASK-GH-010**: The task tool shall write the cache file by writing a new file in full in the `.cache/` folder and then renaming it over the old one, so that another run never reads a partly written cache.
- [ ] **TASK-GH-011**: If the cache file is missing or can't be parsed, then the task tool shall treat the cache as empty.
- [ ] **TASK-GH-012**: The task tool shall keep, for each blocker, the most recent answer GitHub gave for it, even after a failed request records the blocker as unreadable, so that TASK-LINT-043 and TASK-LINT-044 can read it.
- [ ] **TASK-GH-013**: A command that looks up blockers and reports the number of lint findings (TASK-CMD-016, TASK-CMD-022) shall count the findings after the lookup.

## Lint

- [ ] **TASK-LINT-001**: The `check` command shall lint the loaded tasks and drafts (private drafts only with `--private`), the archived tasks, the settings file, the focus file, the milestone files and the repo's schema file against TASK-LINT-002 to TASK-LINT-051, where the rules about one file's keys and values (TASK-LINT-006, TASK-LINT-007, TASK-LINT-009 to TASK-LINT-019, TASK-LINT-028, TASK-LINT-030 to TASK-LINT-033, TASK-LINT-045) apply to tasks and drafts only, the rules about links (TASK-LINT-020 to TASK-LINT-027) apply to open tasks and drafts only, and archived tasks get only TASK-LINT-005 and TASK-LINT-008.
- [ ] **TASK-LINT-002**: The `check` command shall print each finding on its own line as `<ID>: <problem>` for a task, `<outbox folder>/<slug>: <problem>` for a draft, and `<path>: <problem>` for any other file or for a task with no readable ID, with the path relative to the repo's root, and shall print the findings sorted by file path.
- [ ] **TASK-LINT-003**: When `check` finds no problem, it shall print `<n> task(s), no problems`, with `task` for one and `tasks` otherwise, where n is the number of loaded tasks and drafts, and exit with status 0; when it finds any, it shall exit with status 1.
- [ ] **TASK-LINT-004**: The `check` command shall not contact GitHub or any other network service.
- [ ] **TASK-LINT-005**: If a task's, draft's or archived task's frontmatter isn't valid YAML, or isn't a mapping, then `check` shall report it, and the task tool shall leave the file out of every view and computation.
- [ ] **TASK-LINT-006**: If a task has no `id`, then `check` shall report it.
- [ ] **TASK-LINT-007**: Where the settings file sets `task_prefix`, if a task's `id` doesn't have the form TASK-LAYOUT-013 gives, then `check` shall report it.
- [ ] **TASK-LINT-008**: If two tasks, or a task and an archived task, have the same ID (TASK-LAYOUT-014, TASK-LAYOUT-015), then `check` shall report the ID and both files.
- [ ] **TASK-LINT-009**: If a task's file name doesn't start with an ID equal to the task's own (TASK-LAYOUT-014, TASK-LAYOUT-015) followed by ` - `, then `check` shall report it.
- [ ] **TASK-LINT-010**: If a task or draft lacks `title`, `status`, `priority`, `performer` or `effort`, or a task or draft whose `performer` is `agent` lacks `agent_tier` (TASK-FILE-019), then `check` shall report each missing key.
- [ ] **TASK-LINT-011**: If a task's or draft's `status` isn't one of the settings file's `statuses`, `priority` isn't `high`, `medium` or `low` (both without regard to letter case, TASK-FILE-021), `performer` isn't `human` or `agent`, `effort` isn't `S`, `M` or `L`, `agent_tier` isn't `fast`, `moderate` or `strong`, or `priority_set_by` isn't `agent` or `human`, then `check` shall report each such key and its value.
- [ ] **TASK-LINT-012**: Where the settings file lists `types`, if a task's or draft's `type` isn't one of them, then `check` shall report it.
- [ ] **TASK-LINT-013**: If a task's or draft's `created_date`, `due_date` or `defer_until` isn't a date in the form TASK-FILE-006 and TASK-FILE-007 give, then `check` shall report each such key.
- [ ] **TASK-LINT-014**: If a task's or draft's `deadline_kind` isn't `hard`, `soft` or `target`, or it has a `deadline_kind` and no `due_date`, then `check` shall report it.
- [ ] **TASK-LINT-015**: If an entry of a task's or draft's `sessions` lacks `agent`, `id`, `role` or `date`, or its `role` isn't `created`, `worked` or `finished`, then `check` shall report it.
- [ ] **TASK-LINT-016**: If a task or draft of `type: decision` has a `performer` other than `human`, then `check` shall report it.
- [ ] **TASK-LINT-017**: If a task, a draft or the settings file has an `onStatusChange` or `on_status_change` key, then `check` shall report it, since Backlog.md runs its value as a shell command.
- [ ] **TASK-LINT-018**: If a task or draft whose `performer` is `human` has a body line that is a checklist item (`- [ ]` or `- [x]`) containing `[agent]`, then `check` shall report it.
- [ ] **TASK-LINT-019**: If a task whose `status` is `Done` has an open subtask, then `check` shall report it.
- [ ] **TASK-LINT-020**: If an ID in an open task's `dependencies` names no task and no archived task, then `check` shall report it.
- [ ] **TASK-LINT-021**: If an open task's `dependencies` name an archived task whose `status` isn't `Done`, then `check` shall report it as `archived without being done`.
- [ ] **TASK-LINT-022**: If a `<host>/<owner>/<repo>#<ID>` blocker of an open task or draft, whose forge path is the repo's own, names no task and no archived task, then `check` shall report it.
- [ ] **TASK-LINT-023**: If an `<outbox folder>/<slug>` blocker of an open task or draft names no draft in a loaded outbox folder, then `check` shall report it with the advice `if delivered, replace it with the receiving task's forge-qualified ID`.
- [ ] **TASK-LINT-024**: If an `external_blockers` entry of an open task or draft has none of the three forms TASK-FILE-012 gives, then `check` shall report it.
- [ ] **TASK-LINT-025**: If an open task's `parent_task_id` names no task and no archived task, then `check` shall report it.
- [ ] **TASK-LINT-026**: If an open task is in a cycle (TASK-READY-009), then `check` shall report it.
- [ ] **TASK-LINT-027**: If an open task or a public draft has a `references` entry that is neither a URL, nor a `gh:` or forge-qualified reference, nor an `<outbox folder>/<slug>` naming a draft in a loaded outbox folder, and git ignores it as a path in the repo, then `check` shall report it; outside a git repository, `check` shall skip this rule.
- [ ] **TASK-LINT-028**: If a task or draft has a `documentation` key, then `check` shall report it with the advice `move these links into references`.
- [ ] **TASK-LINT-029**: If the backlog directory's `drafts/` folder holds a file, then `check` shall report the file, since the task tool never reads it (TASK-LAYOUT-009).
- [ ] **TASK-LINT-030**: If a draft has an `id`, a non-empty `dependencies` or a `parent_task_id`, then `check` shall report each such key.
- [ ] **TASK-LINT-031**: If a draft has no `target`, or a `target` that isn't a forge path, then `check` shall report it.
- [ ] **TASK-LINT-032**: If the drafts in one outbox folder don't all have the same `target` (TASK-LAYOUT-019), then `check` shall report the folder and its targets.
- [ ] **TASK-LINT-033**: If a draft's `references` entry is neither a URL nor a forge-qualified reference (`gh:<owner>/<repo>#<number>` or `<host>/<owner>/<repo>#<ID>`), then `check` shall report it.
- [ ] **TASK-LINT-034**: If the focus file exists and can't be parsed or isn't a mapping, then `check` shall report it.
- [ ] **TASK-LINT-035**: If the focus file has a key other than `pins`, `weights`, `milestones` and `github_cache_hours`, a `weights` or `milestones` entry ignored under TASK-FOCUS-006 or TASK-FOCUS-008, a pin ignored under TASK-FOCUS-004, or a `github_cache_hours` that isn't a positive number, then `check` shall report each such key or entry.
- [ ] **TASK-LINT-036**: If a pin names no open task or draft, then `check` shall report it.
- [ ] **TASK-LINT-037**: If a task's `milestone` isn't the ID of a milestone in `milestones/` or `archive/milestones/` (TASK-MS-002, TASK-MS-003), then `check` shall report it.
- [ ] **TASK-LINT-038**: If an open task's `milestone` names a milestone found only in `archive/milestones/`, then `check` shall report it.
- [ ] **TASK-LINT-039**: If a bullet of a milestone's `## Related` section names no milestone in `milestones/` or `archive/milestones/`, then `check` shall report it.
- [ ] **TASK-LINT-040**: If a milestone that an open task names has an unfilled description (TASK-MS-006), then `check` shall report it.
- [ ] **TASK-LINT-041**: If the settings file's `statuses` lacks `To Do`, `In Progress` or `Done`, or lists `Done` anywhere but last, then `check` shall report it, since Backlog.md treats the last status as finished.
- [ ] **TASK-LINT-042**: If the settings file sets `default_assignee`, `default_reporter` or `definition_of_done`, sets `filesystem_only` to `true`, or lists `priorities` other than `high`, `medium` and `low`, then `check` shall report each such key.
- [ ] **TASK-LINT-043**: If the most recent answer GitHub gave for a `gh:` blocker of an open task or draft (TASK-GH-012), fresh or not, is that it was closed without its work done (TASK-GH-005), then `check` shall report it with the advice `check it and re-point or drop the blocker`.
- [ ] **TASK-LINT-044**: If the most recent answer GitHub gave for a `gh:` blocker of an open task or draft (TASK-GH-012), fresh or not, is that it was not found (TASK-GH-006), then `check` shall report it as `deleted, transferred or not visible to you: check it and re-point or drop the blocker`.
- [ ] **TASK-LINT-045**: The `check` command shall check each task's frontmatter against the skill's task schema and each draft's against its draft schema (JSON Schema, draft 2020-12, with format assertions on), together with the repo's own `schema.json` in the backlog directory when it exists, where the skill's schemas carry the rules of TASK-LINT-010 to TASK-LINT-016 and TASK-LINT-030 to TASK-LINT-031; it shall report each problem once, naming the key, however many of these specs and schemas describe it.
- [ ] **TASK-LINT-046**: If the repo's `schema.json` isn't valid JSON or isn't a valid JSON Schema, then `check` shall report it and check the other files against the skill's schemas alone.
- [ ] **TASK-LINT-047**: If the backlog directory's `outbox/` or `private/outbox/` folder holds a `.md` file directly, outside any outbox folder, then `check` shall report the file.
- [ ] **TASK-LINT-048**: If a milestone file's frontmatter can't be parsed as a YAML mapping (TASK-MS-008), then `check` shall report the file.
- [ ] **TASK-LINT-049**: If, with `--private`, a public draft and a private draft have the same `<outbox folder>/<slug>`, then `check` shall report both files.
- [ ] **TASK-LINT-050**: If, with `--private`, a task or public draft names a private draft in its `external_blockers` or `references`, then `check` shall report it.
- [ ] **TASK-LINT-051**: If a milestone has a frontmatter `id` that another milestone in `milestones/` also has (TASK-MS-002), then `check` shall report the ID and both files.

## Commands

- [ ] **TASK-CMD-001**: The task tool shall offer the commands `check`, `next`, `why`, `milestone`, `board`, `brief` and `help`, and the options `--offline`, `--private` and `--root <dir>`, given before the command.
- [ ] **TASK-CMD-002**: When run as `help`, the task tool shall print every command, every option of the task tool and of each command, each with a one-line description, without reading the backlog directory or the per-machine settings file, and exit with status 0.
- [ ] **TASK-CMD-003**: When run as `next`, the task tool shall print a ranked queue (TASK-RANK-001 to TASK-RANK-005), each task or draft as a row (its ID or draft name, its score, its `agent_tier` for an agent task, `human` for a human one or `-` otherwise, its `effort` and its `title`) followed at once by a line of its score's terms (TASK-RANK-016, TASK-RANK-017).
- [ ] **TASK-CMD-004**: The `next` command shall default to the repo's own queue, for every performer and type, and shall print its first ten tasks unless `-n` is given.
- [ ] **TASK-CMD-005**: When `next` is given `--for human` or `--for agent`, the queue shall hold only tasks with that `performer`; `--for all` shall keep every performer.
- [ ] **TASK-CMD-006**: When `next` is given `--type <type>`, the queue shall hold only tasks whose `type` is exactly `<type>`.
- [ ] **TASK-CMD-007**: If `next` is given a `--type` that the settings file's `types` doesn't list, while it lists any, then the task tool shall print one line to standard error naming the type and exit with status 2.
- [ ] **TASK-CMD-008**: When `next` is given `-n <n>`, the task tool shall print the queue's first n tasks, or every task when n is 0; if n is negative, it shall print one line to standard error and exit with status 2.
- [ ] **TASK-CMD-009**: When `next` is given `--repo <outbox folder>`, the queue shall be that outbox folder's drafts, and when it is given `--repo all`, the queue shall hold the repo's own tasks and every draft; if no loaded outbox folder has that name, the task tool shall print one line to standard error and exit with status 2.
- [ ] **TASK-CMD-010**: When run as `why <ID>` for a task or draft (a draft named `<outbox folder>/<slug>`), the task tool shall print its title, `performer`, `status`, its repo (the repo's forge path for a task, the outbox folder and `target` for a draft) and milestone title, then for an open one its ranking tier and score with its terms, marked `not ready` when it is blocked, then what it waits on (TASK-READY-010), each task it unblocks (TASK-READY-008), and each of its session records; for a task that isn't open it shall print no tier or score.
- [ ] **TASK-CMD-011**: When `why` shows a session record whose `agent` is `claude-code`, it shall also show the command `claude --resume <id>` that reopens the session.
- [ ] **TASK-CMD-012**: When run as `why <ID>` for an ID that only an archived task has, the task tool shall print the task's title and `status`, marked as archived, with no tier or score.
- [ ] **TASK-CMD-013**: If `why` is given an ID that names no task, draft or archived task, then the task tool shall print `no task <ID>`, with the ID in upper case, to standard error and exit with status 1.
- [ ] **TASK-CMD-014**: When run as `milestone <ID>`, the task tool shall print the milestone's title and whole body, marked as archived when it was found in `archive/milestones/`, then the counts of its open tasks that are ready and blocked, for the developer and for agents, then its ready tasks ranked as `next` ranks them, then its blocked tasks, each with what it waits on (TASK-READY-010); drafts are not counted or listed.
- [ ] **TASK-CMD-015**: If `milestone` is given an ID that names no milestone in `milestones/` or `archive/milestones/`, then the task tool shall print `no milestone <ID>` to standard error and exit with status 1.
- [ ] **TASK-CMD-016**: When `next`, `why`, `milestone` or `board` runs while `check` would report findings (counted over the same loaded files, so private drafts only with `--private`), the task tool shall print its output and then the line `<n> problem(s): run check`, with `problem` for one and `problems` otherwise, on standard error, whatever its exit status.
- [x] **TASK-CMD-017**: When run as `board`, the task tool shall print one Markdown page to standard output, and write no file other than the GitHub lookup cache (TASK-LAYOUT-010).
- [ ] **TASK-CMD-018**: The board shall show, in order: the numbers of ready, blocked and open tasks for the developer and for agents, and the number of drafts, which aren't counted for the developer or agents; the open pinned tasks and drafts in pin order, each blocked one marked `(blocked)`; the developer's ready queue (first 25 tasks); the agents' ready queue (first 30 tasks); a Bottlenecks table of the open tasks and drafts that unblock at least one other (TASK-READY-008), the 15 that unblock the most, ties in natural order, with whether each is ready and what it waits on; every blocked task with what it waits on; each outbox folder's drafts; and every open task (not draft), grouped by milestone in natural order of milestone ID, with tasks that name no milestone last under `No milestone`.
- [ ] **TASK-CMD-019**: The board shall head each milestone group with the milestone's title, its first description sentence (TASK-MS-007) and the bullets of its `## Related` section.
- [ ] **TASK-CMD-020**: The board shall link each task ID and draft name to its file by a path relative to the directory the task tool was started in.
- [ ] **TASK-CMD-021**: The board and the brief shall count and list a task under the developer when its `performer` is `human`, under agents when it is `agent`, and under neither otherwise.
- [ ] **TASK-CMD-022**: When run as `brief`, the task tool shall print, each only when it isn't empty and in this order: the open tasks (not drafts) with `status: In Progress`; the other open pinned tasks; the other ready tasks in the second tier (TASK-RANK-002); the first five other rows of the agents' ready queue; the number of rows in the developer's ready queue with the first three not already shown; the number of findings `check` would report; and any per-machine settings problem (TASK-XREPO-004), each task appearing only in the first part it fits.
- [ ] **TASK-CMD-023**: The `brief` command shall exit with status 0, and while every part TASK-CMD-022 lists is empty, it shall print nothing.
- [ ] **TASK-CMD-024**: The `brief` command shall print no line to standard error for lint findings or per-machine settings problems, since TASK-CMD-022 includes them in its output.
- [ ] **TASK-CMD-025**: If the task tool is run with no command, an unknown command, or an option or option value it doesn't accept, then it shall print a usage message to standard error and exit with status 2.

## Skill

- [ ] **TASK-SKILL-001**: The skill shall hold at least `SKILL.md`, `scripts/tasks.py` (the task tool), `references/task-format.md`, `schemas/task.schema.json` and `schemas/draft.schema.json`.
- [x] **TASK-SKILL-002**: The skill's `SKILL.md` frontmatter shall use only the Agent Skills fields `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
- [x] **TASK-SKILL-003**: The skill's `scripts/tasks.py` shall be a PEP 723 script whose inline metadata pins every dependency with `==` to an exact version, so that `uv run --script` runs it with no project environment.
- [x] **TASK-SKILL-004**: The skill's `references/task-format.md` shall describe every key the task tool reads, with its values and meaning, the three blocker forms, the outbox draft form, session records, and labels as recording where a task came from.
- [x] **TASK-SKILL-005**: The skill shall tell the agent to create a task for work left outstanding beyond the current request, and none for work done in the session that found it.
- [x] **TASK-SKILL-006**: Before creating a task, the agent shall search the backlog, with `backlog search` or a text search of the task files, using a query for the work, for a task covering the same work, and shall extend or link an existing one instead of creating a duplicate. *(eval)*
- [x] **TASK-SKILL-007**: The skill shall tell the agent to size a task to what one focused pull request would finish, to use subtasks for parts of one goal in one area and `dependencies` for work across components, and to split agent-doable work out of a task that waits on the developer.
- [x] **TASK-SKILL-008**: The skill shall tell the agent that a description gives the problem or trigger and context the code can't recover, that acceptance criteria state testable behaviour, and that the plan is left to whoever starts the task.
- [x] **TASK-SKILL-009**: When creating a task, the agent shall run `backlog task create`, then edit the task file to add `performer`, `effort`, `priority_set_by: agent`, `agent_tier` for an agent task, and a session record with role `created` where the harness exposes a session ID, and then run the repo's `tasks check` and fix any finding it reports about that task. *(eval)*
- [x] **TASK-SKILL-010**: The skill shall tell the agent to add a session record with role `worked` when starting a task and `finished` when finishing it, taking the ID from the harness (in Claude Code, `CLAUDE_CODE_SESSION_ID`), and none where the harness exposes no ID.
- [x] **TASK-SKILL-011**: The skill shall tell the agent that labels don't restate a task's type.
- [x] **TASK-SKILL-012**: The skill shall tell the agent to take the top of `next --for agent` unless the developer names a task, to read the task, its `## Comments` included, before changing it, and to set `status: In Progress` when starting.
- [x] **TASK-SKILL-013**: The skill shall tell the agent to use comments for guidance, review remarks and questions that don't stop the work, to turn a blocking question into a `decision` task the work depends on, and to record progress in notes.
- [x] **TASK-SKILL-014**: The skill shall tell the agent to record extra work it finds as a new task or a question rather than widening the task, and to finish a parent only when its subtasks are done.
- [x] **TASK-SKILL-015**: The skill shall tell the agent to tick an acceptance criterion only on evidence that the behaviour works, to write a final summary of what changed, why, how it was verified and any risks before setting `status: Done`, and to record a `decision` task's ruling in the document it governs, linked from the summary.
- [x] **TASK-SKILL-016**: The skill shall tell the agent to name a task's milestone by ID, never to change a milestone's `## Importance`, to draft other milestone sections only for the developer's review, and to leave adding, renaming, archiving and removing milestones to the developer.
- [x] **TASK-SKILL-017**: The skill shall tell the agent to write work for another repo as an outbox draft with a `target`, naming this repo's files by URL and its tasks and specs by forge path.
- [x] **TASK-SKILL-018**: The skill shall tell the agent to write work that can't be public as a draft in the outbox of the private coordination repo that the per-machine settings' `private_root` names, when that is set and that repo has a backlog directory; otherwise, where the repo's main checkout has a `backlog/private/` folder, in that folder's outbox in the main checkout; and otherwise to write none and tell the developer.
- [x] **TASK-SKILL-019**: The skill shall give the steps for delivering a draft: the receiving repo creates the task and, unless the sending repo is private and the receiving one public, references the sending task by forge path; the sending repo replaces each `<outbox folder>/<slug>` reference with the new task's forge-qualified ID, deletes the draft and runs `check`.
- [x] **TASK-SKILL-020**: The skill shall tell the agent never to name a private repo, or reference a private draft, in a public repo's tasks, drafts or references.
- [x] **TASK-SKILL-021**: The agent shall never edit the focus file, even when the developer asks it to; it shall show the developer the exact edit to make instead. *(eval)*
- [x] **TASK-SKILL-022**: The skill shall tell the agent not to change a `priority` whose `priority_set_by` is `human` but to propose the change to the developer, and to leave `assignee` empty.
- [x] **TASK-SKILL-023**: The skill shall tell the agent to edit tasks through Backlog.md's CLI or directly in the file, never by moving cards in Backlog.md's terminal board, and never to add `onStatusChange`.
- [x] **TASK-SKILL-024**: The skill shall tell the agent which `task edit` options replace a whole list (`--acceptance-criteria`, `--dep`, `--ref`, `-l`, `--notes`, `-a`) and which add to one (`--add-ref`, `--add-label`, `--append-notes`), how to quote text containing backticks, how to build multi-line text without heredocs, and to quote file names, which contain spaces.
- [x] **TASK-SKILL-025**: The agent shall never set a task's `status` to `Draft` or run `backlog task demote`. *(eval)*
- [x] **TASK-SKILL-026**: The skill shall give the steps for a duplicate ID that `check` reports: the task whose file the repo's git history (`git log --diff-filter=A`) shows was added later takes a new ID, or the one the developer chooses when that history doesn't settle it; its file is renamed and its `id` changed, and every reference to the old ID that its own branch added, in tasks, docs, notes and specs, is updated.
- [x] **TASK-SKILL-027**: The skill shall state that when another skill's workflow creates tasks, that skill's approval steps apply to them.
- [x] **TASK-SKILL-028**: The skill shall state each place its rules replace Backlog.md's own agent instructions: task files may be edited by hand; Backlog.md's overview isn't read at each session start; commits follow the repo's own policy; agents don't assign themselves; work is found with `next`; outstanding work is recorded without asking unless the workflow in use asks first; links go only in `references`; and agents never use Definition of Done checklists, Backlog.md's drafts, `backlog doc`, `backlog decision`, its MCP tools, `task delete`, `doctor --fix`, `board export` or `agents --update-instructions`.
- [x] **TASK-SKILL-029**: The skill shall tell the agent that, in a repo with no backlog directory, it shall not create one or run `backlog init`, but shall tell the developer the repo has no backlog and leave the outstanding work in its reply.
- [x] **TASK-SKILL-030**: The skill shall tell the agent that, when the `backlog` CLI won't run, it shall not write the task file itself or choose an ID, but shall tell the developer the CLI failed and leave the outstanding work in its reply.
- [x] **TASK-SKILL-031**: The skill's `references/task-format.md` shall state that any tool or skill following it may write task files directly, and that such a writer assigns IDs itself, which `check` reports when they collide.

## This repo

- [x] **TASK-REPO-001**: This repo's `tasks` mise task shall run the skill's `scripts/tasks.py` with `uv run --script`, passing on every argument given after `mise run tasks --`.
- [ ] **TASK-REPO-002**: This repo's `mise run check` shall run the task tool's `check` over this repo's backlog, and fail when it reports a finding.
- [ ] **TASK-REPO-003**: This repo's `backlog/README.md` shall point readers to the skill's `references/task-format.md` and to the `tasks` commands, and add only what is particular to this repo.
- [ ] **TASK-REPO-004**: This repo's `backlog/schema.json` shall require a task or draft whose `labels` include `open-question` to have `type: decision`.
- [x] **TASK-REPO-005**: This repo's `mise.toml` shall pin the `gh` CLI and Backlog.md, and schematter where it is the schema engine, each to an exact version.
- [x] **TASK-REPO-006**: A test shall run the pinned Backlog.md CLI in a scratch git repo on a task carrying every custom key (a `sessions` list and a draft's `target` included), change its status with `backlog task edit`, and fail if any custom key's parsed value changed or was dropped; the test shall be skipped where `backlog` isn't on `PATH`.
- [x] **TASK-REPO-007**: In this repo, `git check-ignore` shall report `backlog/.cache/`, `backlog/.locks/` and `backlog/private/` as ignored.
- [x] **TASK-REPO-008**: This repo shall not track `backlog/BOARD.md`.
