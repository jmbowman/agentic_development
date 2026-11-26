---
id: AD-368
title: Fix three mismatches between the task-tracker LLD, HLD and specs
status: To Do
assignee: []
created_date: '2026-11-26T13:02:35Z'
labels:
  - loose-end
milestone: m-1
dependencies: []
references:
  - docs/intent/task-tracker/task-tracker-design.md
  - docs/intent/task-tracker/task-tracker-specs.md
  - docs/high-level-design.md
priority: low
type: docs
ordinal: 55000
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: a20b213e-9cc5-4bd1-8407-62658bae5e42
    role: created
    date: '2026-11-26'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AD-336's review wave (2026-11-25) found three places where text that change didn't touch disagrees between the task-tracker design and its specs. (1) The LLD's list of Backlog.md keys the tool reads omits `labels`, which TASK-FILE-002 lists, and its sentence on ignored keys omits `documentation`, which TASK-FILE-004 lists. (2) The LLD's focus-file sentence on pins and its Ranking prose name performer and repo as the queue filter but not type, which TASK-RANK-001, TASK-RANK-003 and the Ranking diagram include. (3) The HLD and the LLD's Layout table say only that the developer delivers an outbox draft, while the LLD's skill rule says the developer or a session in the receiving repo. They were left alone because that slice was about assignees.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The LLD's key lists, its queue-filter wording and the HLD's and Layout table's delivery wording agree with the specs and the skill rule
- [ ] #2 `mise run lid` reports no findings
<!-- AC:END -->
