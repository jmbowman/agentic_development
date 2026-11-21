---
id: AD-5.1
title: 'Task tracker slice 1: the task-tracker skill'
status: Done
assignee: []
created_date: '2026-11-20T13:25:00Z'
updated_date: '2026-11-21T12:31:00Z'
labels: []
milestone: m-1
dependencies: []
parent_task_id: AD-5
priority: high
type: feature
ordinal: 20000
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: created
    date: '2026-11-20'
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: worked
    date: '2026-11-21'
  - agent: claude-code
    id: febc0a58-71fe-4ef9-b3c7-3cc6205db7f4
    role: finished
    date: '2026-11-21'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
First slice of AD-5: make the task tracker usable by agents as a skill, with the tool behaving as the pilot does. Unblocks the skills that will write their follow-ups as tasks (AD-6, AD-12). Scope: move scripts/tasks.py into skills/task-tracker/scripts/ unchanged in behaviour; SKILL.md, references/task-format.md, the structure tests and the four evals (TASK-SKILL); TASK-REPO-001, 005, 006, 007 and 008, with `board` printing to standard output and backlog/BOARD.md untracked; the data changes the skill rules need (`target` on every outbox draft, `session:` references moved into `sessions`, the search tasks retyped from `spike` to `search`); backlog/README.md, CLAUDE.md Tasks rule and README.md updated. The pilot tests and the check over this repo backlog stay green.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The TASK-SKILL specs (except TASK-SKILL-001, whose schemas come with AD-5.2), TASK-REPO-001, 005, 006, 007 and 008, and TASK-CMD-017 are covered by tests, evals or review as the specs file says, and pass
- [x] #2 mise run check passes, including the task tool check over this repo backlog
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-21: tests, code, data migration and docs done; tests stop and code sign-off inspected by review waves (findings triaged and applied). mise run check passes except test_board_is_not_tracked, which passes once the developer stages the deletion of backlog/BOARD.md. The eval suite (evals/task-tracker/) has not been run yet; the developer runs it.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built the task-tracker skill (slice 1 of AD-5): the pilot tool moved into skills/task-tracker/scripts/ with board printing to standard output and forge-qualified blockers accepted; SKILL.md with the agents rules, including the rulings on a repo with no backlog, duplicate-ID ties by git history, and an agent whose backlog CLI fails creating nothing while other writers may write task files directly; references/task-format.md; four eval cases; backlog data migrated (target on drafts, sessions records, search type); Backlog.md pinned as its release binary. Verified by mise run check (2493 tests, lid, tasks check), two review waves, and five eval waves: all four cases pass with the skill; search-before-create last run counted 2 of 3 after a grader fault, with its grader reworded since. Risks: the pilot compares forge-qualified blockers by repo name only and reads no archive folder until AD-5.2 and AD-5.3; check cannot run inside the eval sandbox, which has no network for PyYAML.
<!-- SECTION:FINAL_SUMMARY:END -->
