---
id: AD-5
title: Walk LID's arrow for the task tracker, starting from the pilot
status: In Progress
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-20'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-20: the HLD, LLD, EARS and edge-audit stops are done and approved by the developer. The HLD has the task backlog's subsection, tenet 10 and the Task tracker component; the LLD is docs/intent/task-tracker/task-tracker-design.md; the specs are docs/intent/task-tracker/task-tracker-specs.md (222, all `[ ]`). The carried-over items in the description are settled in the LLD.

Next: Phase 5, tests first. Read the LLD, the specs, scripts/tasks.py and tests/test_tasks_pilot.py first. The proposed plan, which the developer hasn't yet approved, is three slices, each with failing tests first, then code, a review wave and a commit:
1. The data layer and lint: move the tool into skills/task-tracker/ and cover the LAYOUT, FILE, MS, FOCUS and XREPO facets, LINT (except the GitHub findings), the schemas, and the REPO specs.
2. Readiness, ranking, the GitHub lookup and its two lint findings, and the commands (READY, RANK, GH, CMD).
3. SKILL.md, the format reference, the structure tests and the four evals (SKILL), then the data migration and the close-out: remove backlog/BOARD.md; fill the milestone descriptions (the agent drafts, the developer writes each Importance); add `target` to every outbox draft and make cross-repo references forge-qualified (the private draft's `agentic_development#AD-5` blocker included); move `session:` entries in references into `sessions`; retype the search tasks from `spike` to `search`; merge AD-230 into AD-270 and AD-189 into AD-147, and split AD-189's agent drafting out; fix AD-31's label and AD-308's milestone; fix references to ignored `tmp/` files (AD-7, AD-147, AD-219); update the copier-python outbox draft "Ship the backlog scaffolding through the template"; update backlog/README.md, CLAUDE.md's Tasks rule and README.md; reduce docs/task-tracking-pilot.md to history.

First step of the next session: confirm the slicing with the developer, then write slice 1's failing tests, annotated with @spec IDs. AD-332 (whether Backlog.md rewrites config.yml) must be done before slice 1 writes the consumer wiring. Under this repo's policy the review wave, not the developer, inspects the tests stop and the code sign-off.
<!-- SECTION:NOTES:END -->
