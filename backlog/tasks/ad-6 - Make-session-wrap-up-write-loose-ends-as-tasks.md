---
id: AD-6
title: Make session-wrap-up write loose ends as tasks
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-21T23:08:00Z'
labels:
  - surfaced
milestone: m-1
dependencies:
  - AD-5.1
references:
  - skills/session-wrap-up/SKILL.md
  - docs/intent/session-wrap-up/session-wrap-up-specs.md
  - docs/task-tracking-pilot.md
priority: high
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: worked
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The wrap-up skill reports loose ends as prose, which nothing then tracks; 29 untracked ones had to be recovered from session transcripts for this pilot. Change the skill so each confirmed loose end becomes a task file in `backlog/tasks/` (or a draft under `backlog/outbox/<repo>/` when it belongs elsewhere), with performer, effort and source set, after the developer confirms the text as the skill already requires. Goes through LID in the session-wrap-up segment. Done when a wrap-up in a scratch repo produces task files and an eval case covers it.

From the task-tracker LLD (AD-5, *Other skills*): the wrap-up tells the agent to create the tasks using the task-tracker skill's rules when that skill is installed, and its own short description of a task otherwise; the wrap-up's own confirmation step governs these writes. For work belonging to another repo, the outbox draft is the record, and a message to a session there or an issue on it is a way of delivering the draft (see AD-121).

**Why it matters:** Closes the largest leak that made the backlog chaotic.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-21: LID walk done through code. LLD revised (task items, Tasks, Cross-repo work; slice 5 replaces cross-repo routing), specs WRAP-TASK-001 to 030, WRAP-XREPO-001, 007-009, 013-017, WRAP-RPT-016, WRAP-GATE-049; edge audit with 14 rulings; tests (six eval cases, manual scripts, structure tests) and skill text (references/tasks.md, SKILL.md) each through a review wave. AD-121 and AD-122 closed as superseded. Waiting on: the developer reviewing the six eval prompts and the HLD line 53 wording, then the eval run; the manual scripts are unrun.

2026-11-21: five eval rounds on the six slice-5 cases. Latest runs (Sonnet 5.5 agent and judge, three runs each): outbox-draft-other-repo, tasks-existing-work, tasks-backlog-would-fetch, tasks-no-backlog and tasks-repeat-run passed every run; tasks-new-work passed two of three (one review task hinted at a colleague on leave; tasks.md now gives that as the example to avoid). Remaining for Done: the manual scripts in evals/session-wrap-up/manual.md (from "Setting up the task runs"), which show a wrap-up writing real task files in a scratch repo, the other half of the acceptance criterion.

2026-11-21: the remaining verification (the manual scripts, and the acceptance criterion half about task files in a scratch repo) is AD-6.1, blocked on AD-138 and through it the pinned pytest-claude-code-evals plugin. AD-6 waits on that subtask; status set back to To Do, since no work on it can proceed until then.
<!-- SECTION:NOTES:END -->
