---
id: AD-5
title: Walk LID's arrow for the task tracker, starting from the pilot
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-1
dependencies:
  - AD-2
references:
  - docs/task-tracking-pilot.md
  - scripts/tasks.py
  - https://github.com/jmbowman/agentic_development/issues/166
  - docs/prior-art/2026-11-06-federated-knowledge-and-work-items.md
  - docs/prior-art/2026-11-12-task-management-for-humans-and-agents.md
  - docs/prior-art/2026-11-16-cross-repo-task-coordination.md
priority: high
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Turn the pilot into designed, specified work: an HLD component entry for task tracking, an LLD (information model: task keys, readiness, external blockers, the focus file, ranking terms, lint rules, outbox drafts), EARS specs, then `@spec` annotations on `scripts/tasks.py` and its tests, rewriting whatever the specs change. The developer reviews the HLD, LLD, EARS and edge-audit stops. Done when `mise run lid` covers the tool and the pilot note is reduced to history.

Carried over from the pilot's review wave (2026-11-17), to settle in this walk:

- Near-duplicate tasks to merge or link: AD-189 with AD-147 (lidc proposals), and AD-230 with AD-270 (staleness beside extant and blockwatch). The design needs a rule or a check for duplicates.
- AD-189 is the developer's but includes drafting an agent could do: split it, as the granularity rule asks.
- Data that lint doesn't catch: AD-31 is typed `feature` but labelled `open-question`, and AD-308, a repo-setup decision, sits in the upstream-feedback milestone.
- An outbox draft cites this repo's files by relative path (`docs/...`, spec IDs), which won't resolve in the receiving repo. Decide the reference form for drafts: full URLs, or a repo prefix.
- AD-2, AD-7, AD-147 and AD-219 cite gitignored `tmp/` files that a reader of the public repo can't open. Decide whether a task may reference an untracked file.
- A pull request closed without merging counts as a closed blocker. Decide whether that is right.
- The GitHub lookup: a reopened issue reads as closed for up to six hours; lookups run one after another with a ten-second timeout each, and failures aren't cached, so an unreachable network slows `brief`.
- The tool loads `tasks/` and `completed/` but not `archive/`, where Backlog.md's cleanup may move tasks, so a dependency on an archived task would read as unknown.
- Editing through Backlog.md's board writes `ordinal` into a card's column neighbours and re-serializes each file it touches. Decide whether the design accepts that churn or avoids the board for edits.
- Whether `backlog/BOARD.md` is tracked. Closing a task changes it, so every status change carries a second modified file, and Backlog.md's own boards show the same data. The developer's leaning (2026-11-17) is to drop it and keep the `tasks` commands.

The pilot's scratch files are in `tmp/task-pilot/` on the machine that built it (gitignored, so they may be absent): the harvest brief and each harvester's raw inventory, the curation that merged and ranked them, the importer, and a read-only clone of Backlog.md v1.55.3.

**Why it matters:** Brings the prototype under the same intent discipline as the rest of the repo.
<!-- SECTION:DESCRIPTION:END -->
