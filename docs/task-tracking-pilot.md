# Task tracking pilot (2026-11-16)

A working pilot of the task tracker that [the task-management note](prior-art/2026-11-12-task-management-for-humans-and-agents.md) and [the cross-repo coordination note](prior-art/2026-11-16-cross-repo-task-coordination.md) sketched: this repo's whole backlog as files in [`backlog/`](../backlog/README.md), and a tool, then `scripts/tasks.py` and now [the task-tracker skill's](../skills/task-tracker/SKILL.md) `scripts/tasks.py`, that lints, ranks and displays them. It is a prototype built to settle the notes' open decisions on real data. It started outside the arrow of intent, and [AD-5](../backlog/tasks/ad-5%20-%20Walk-LID-s-arrow-for-the-task-tracker-starting-from-the-pilot.md) is the task that walks the arrow for it.

## What the pilot is

| Part | What it is | Size |
|---|---|---|
| Store | [Backlog.md](https://github.com/MrLesk/Backlog.md) 1.55.3's file format, unchanged: one Markdown file per task under `backlog/tasks/`, with its native status, priority, type, milestone, dependencies, parent, due date and references | Adopted |
| Eight custom keys | `performer`, `agent_tier`, `effort`, `external_blockers`, `deadline_kind`, `defer_until`, `waiting`, `priority_set_by`, as frontmatter Backlog.md preserves | A convention |
| Focus file | `backlog/focus.yml`: the developer's pins and ranking weights, the one file agents don't edit | One file |
| Outbox | `backlog/outbox/<repo>/<slug>.md`: task drafts for other repos, without an ID; `backlog/private/` (gitignored) for what can't be public | A convention |
| Tool | `scripts/tasks.py`: `check` (lint), `next` and `why` (ranked ready queues with every score term shown), `board` (the generated `BOARD.md`), `brief` (for a session-start hook) | About 700 lines of Python, PyYAML only, with tests, including one that runs Backlog.md |

The tool reads task files and never writes one. Backlog.md's own board and web view work over the same files.

## What it found

The backlog was populated from seven sources: 21 open GitHub issues, the `[ ]` and `[D]` EARS specs and design-doc open questions, 20 prior-art notes, 15 tool-feedback pages with the review log and eval results, the loose ends of past session wrap-ups (recovered from session transcripts), three neighbouring repos, and the pilot's own next steps.

- **About 480 raw items became 385 tasks** after 90 duplicates across sources were merged and 7 dropped: 315 for this repo, 51 drafted for four other public repos, and 19 kept private.
- **The 21 open issues hold about a seventh of the work.** The largest untracked sources were the prior-art notes (about 160 items: verdicts with nothing built and no issue) and the design docs' deferred lists.
- **The developer is the bottleneck.** 110 of this repo's 315 tasks are the developer's, 47 of them decisions, and 64 are ready now. 85 of the 205 agent tasks are blocked, most of them behind a decision.
- **A few decisions gate most of the blocked work.** The ruling on how review waves stop (AD-140) has 20 tasks waiting on it; test-first policy (AD-141) has 10; the pin for the interactive-eval plugin (AD-132) and the sandbox settings (AD-143) five each.
- **Two done issues are still open** (#167, #98), and a release is overdue: about 157 commits since v0.3.1, which the template still pins (AD-22).
- **25 tasks were written nowhere before**, labelled `surfaced`: stale statements in design docs, a spec-marker convention that makes `[ ]` unreliable as a gap list (AD-144), and the three changes that would stop the backlog scattering again (below).

**Why the backlog scattered, and the fix.** Work was recorded wherever the session that found it happened to write: an issue, a spec marker, a note's last section, a wrap-up report. Three tasks close the leaks at their sources: session wrap-up writes loose ends as task files (AD-6), prior-art search writes its open decisions and next steps as tasks (AD-12), and `check` requires every open or deferred spec to be cited by a task (AD-13).

## How it combines the prior art

The notes name the custom parts they propose by letter. Those cited here: piece B, a check that protects the developer's decisions; piece C, a lint for task granularity and readiness; piece F, a push-only sync to GitHub; piece G, work filed for another repo.

| Idea | From | In the pilot |
|---|---|---|
| File format, board, web view, readiness within a repo | Backlog.md (adopted) | Used as is |
| Unknown frontmatter keys preserved | Backlog.md | The extension point for every custom key; nothing forked |
| A decision is the human's; other work defaults to agents | [pm-cli](https://github.com/unbraind/pm-cli)'s `execution_role` | `type: decision` must have `performer: human` (lint) |
| Only leaves are actionable; a parent can't close over open children | pm-cli, [treadling](https://github.com/Abhijeet34/treadling) | Readiness and lint rules |
| Required fields before a task counts | treadling's definition of ready | `check` |
| No agent work stranded in a human task | The task note's piece C | A human task with an `[agent]` checklist item fails lint |
| Capability tier, not a model name | [beadhive](https://github.com/beadhive/beadhive), [ADLC](https://github.com/voodootikigod/adlc) | `agent_tier` |
| `priority_set_by` | [ravenseat](https://github.com/vegardjorg/ravenseat) | Every pilot priority is marked `agent` |
| Tiers, then a weighted score, with each term printed | [work-plan-toolkit](https://github.com/stylusnexus/work-plan-toolkit), [Taskwarrior](https://github.com/GothenburgBitFactory/taskwarrior) | `next`, `why`; the weights for priority, unblocking, deadline, work in progress and age start from Taskwarrior's, and those for effort and someone waiting are the pilot's own |
| Unblocking value from the graph | [bones](https://github.com/bobisme/bones) | The `unblocks` term, counted through the whole chain (a parent waits on its subtasks), with the number that are agents' shown |
| A small pinned set | ['Stick to' Three](https://doi.org/10.1145/3715336.3735792), [lodestar](https://github.com/AustinGailey/lodestar) | `pins` in `focus.yml` |
| Deadline hardness | [htm](https://github.com/MilesCranmer/htm) | `deadline_kind` |
| External blockers that fail closed | [relevo](https://github.com/elalfner/relevo), [claude-zamu](https://github.com/dhh1128/claude-zamu) | `external_blockers`; unreadable counts as open |
| Readiness from the blocker's own state | work-plan-toolkit | GitHub issue state read through `gh`, cached six hours |
| Cross-repo work arrives as a file the receiver accepts | The cross-repo note's piece G | The outbox |
| No LLM ranks the list | The cross-repo note's papers | Agents propose attributes; arithmetic ranks |

**Where the pilot departs from the notes.** The task note's piece B protects human decisions field by field, with a check that compares each commit's protected fields against its base. The pilot instead puts the developer's decisions in one file that only the developer edits. Protection becomes a path rule (a permission deny and a one-line commit check, AD-11) instead of a medium-sized diff checker, and the weekly ranking is one small edit. Task files keep facts and estimates, which agents may propose.

## The notes' open decisions, as the pilot took them

The developer reviewed the table on 2026-11-17 and accepted the pilot's answers for now (AD-2), so the LID pass (AD-5) starts from them. Two rows hold no answer and stay open as their own decisions: X5 (AD-4) and X8 (AD-316). The developer also ruled that the backlog is this repo's record of outstanding work (AD-14): GitHub issues stay as the public way in, linked from the tasks made from them and closed when those tasks are done. T = task note, X = cross-repo note.

| # | Decision | The pilot's answer | Note's recommendation? |
|---|---|---|---|
| T1 | Store | Backlog.md's format | Yes |
| T2 | Role of the authority check today | A convention plus lint now; a path rule on `focus.yml` next | Changed: path rule, not field diffs |
| T3 | Where agent proposals show | In the task itself, marked `priority_set_by: agent`; pins stay the developer's | Changed: no `proposals.md` |
| T4 | Claiming | Not built; status and assignee by convention until agents pick their own work (AD-19) | Deferred |
| T5 | Model hint | `agent_tier` only | The alternative (no `suggested_model`) |
| T6 | What is protected | Pins and weights (the focus file); `priority` once `priority_set_by: human` | Narrower |
| T7 | Spotting agent work in a human task | `[agent]` marker on checklist items, linted | Yes |
| T8 | Collaborator edits on GitHub | No sync built; issues are linked from tasks | Deferred with piece F |
| X1 | Is merging an incoming task its acceptance | Yes; a draft stays in the sender's outbox until delivered | Yes |
| X2 | Naming across repos | Drafts are named by slug; the receiver assigns the ID; refs are `repo#ID`, `repo/slug` or `gh:owner/repo#N`. Each repo's ID prefix is distinct (`AD-` here) | Yes, plus the prefix |
| X3 | Cross-repo view | The generated `BOARD.md`, for this repo and its outbox only; reading other repos' backlogs is AD-16 | Partly; the cross-repo part is deferred |
| X4 | How the rank is computed | Pins, then imminent hard deadlines, then a weighted score with terms shown | Yes |
| X5 | Where pins and rules live | In each repo's `focus.yml` for now; a private coordination root is the open question (AD-4) | Open |
| X6 | Template follow-ups | Not built; filed as a draft for copier-python | Deferred |
| X7 | GitHub's native blocked-by | Not used; readiness is computed from files and issue state | Yes; mirroring them is deferred with piece F |
| X8 | Auto-merge of template updates | Not touched. The note's recommendation (turn it off for Copier) conflicts with HLD tenet 6 and needs a ruling (AD-316) | Open |
| X9 | Who opens cross-repo pull requests | The agent drafts into the outbox; the developer delivers (AD-15) | Yes |
| X10 | Which ranking fields are protected | The focus file | Narrower: the note also protects the developer's recorded decisions |
| X11 | Rank versus Backlog.md's own fields | The rank is computed on read and never written back; `priority` is one input | Yes |
| X12 | Which agent-proposed attributes need confirming | None before ranking; all are marked agent-set, and AD-17 reviews how well that worked | Changed: lighter |

## Extending to personal tasks

The tool knows nothing about software: a task needs a title, a performer, an effort and a priority, and `due_date`, `deadline_kind`, `defer_until` and `waiting` already cover deadlines, date windows and obligations. A personal backlog is another root in the same format, kept private, with the developer as performer of most tasks. What it would add:

- **Several roots** read as one portfolio (AD-16), with the private root's location decided first (AD-4).
- **Recurrence and refresh triggers**: a task that reopens on a schedule or when an external event fires. Nothing in the pilot does this.
- **Effort in two units**: an agent's cost and a person's attention are different budgets.
- **A context key** (at the computer, at home, with someone else) to filter the developer's queue, and a life-area grouping, which milestones or labels can carry.
- **A privacy tier** per task, so a private task can never be written to a public repo or sent to a hosted model. The pilot's only mechanism is the gitignored `backlog/private/`.
- **Blockers that are people or events**, not only tasks: today `waiting` is display text.

## Verification and gaps

- **Backlog.md loads these files, checked by the developer on 2026-11-17 (AD-1, done).** The terminal board and the web view (`backlog browser`) both show the tasks correctly, and the extra files in `backlog/` cause no trouble. The agent session wasn't permitted to run the binary, so the files follow the format read from its source at v1.55.3 and its own repo's task files. The developer opened the board over them, and a status change made by editing a task file directly moved the card to the next column without a reload. A status change made in the terminal board kept every custom key in the task's file; it also added `updated_date` and `ordinal`, re-indented the YAML lists, and wrote an `ordinal` into the other task in the same column. Every file under `backlog/tasks/` has since been re-serialized by Backlog.md itself (a status change and its reverse through the CLI), so a later edit through the tool changes only what was edited; the outbox drafts are still in the YAML style they were first written in. One display problem: Backlog.md's terminal task view moves backticked paths out of their sentences to the end of the paragraph, which garbles descriptions that name several files ([tool feedback](tool-feedback/backlog-md.md)); the task files are left as written, since the web view, GitHub and `--plain` output aren't affected.
- **Every priority, effort, tier and performer is an agent's proposal.** Subagents harvested each source and proposed them; duplicates were merged by hand from titles. Some tasks will be wrong, stale or already done; 27 carry a `maybe-done`, `partly-done` or `stale` label from the harvest.
- **Session loose ends were recovered by text search** of transcripts ("loose end", "next session", and each session's last messages), so some were missed, and loose ends noted outside the repo and its sessions weren't read.
- **Not built:** the session-start hook (AD-10), protection of the focus file (AD-11), claiming (AD-19), reading sibling repos' backlogs (AD-16), template follow-ups, and any sync to GitHub.

## Composition techniques

Notes on combining existing software and ideas into something small, kept as a seed for a prior-art search on doing this better (AD-151).

1. **Adopt a format, not a runtime.** The pilot depends on Backlog.md's file layout and one documented behaviour (unknown keys survive), not on its code. It worked without running the tool, and the tool can be swapped while the files stay.
2. **Find the extension point before sizing the gaps.** Preserved unknown keys turned five "custom pieces" into conventions plus a linter. The question to ask of any candidate first: where can data or behaviour be added without a fork?
3. **Borrow a rule, not its implementation.** Most of the tools in the table above contributed one sentence each (fail closed; only leaves are actionable; show every score term). A rule costs a few lines and a test; a dependency costs upkeep.
4. **Move protection from fields to files.** A guarantee that needs a diff-aware checker inside shared files may need only a path rule once the protected data has its own file.
5. **Compute, don't store, what can be derived.** Readiness, rank and what a task unblocks are computed on read, so nothing drifts and no tool has to write another tool's fields.
6. **Start from borrowed defaults that explain themselves.** Weights taken mostly from Taskwarrior were good enough to rank 300 tasks sensibly on the first run because every score prints its terms; the terms, not the numbers, are what gets reviewed.
7. **Pin the contract with a test.** The one behaviour borrowed from the adopted tool (key preservation) needs a test that runs the tool, so an upgrade can't remove it silently (AD-9).
8. **Fill it with real data before designing it.** The harvest changed the design three times in an afternoon: outbox drafts needed their own identity, private items needed a separate root, and a square-root curve replaced a capped count once one decision turned out to gate twenty tasks.
9. **Keep a list of what each borrowed idea replaced.** The table above is the record a later reader needs to ask "why not X?", and it shows which borrowed ideas were never exercised.

Open questions for that search: tools that detect when an adopted tool's file format changes; methods for deciding compose versus build that account for upkeep; contract-test generators for CLI tools; and measures of "minimal" that a check can enforce.
