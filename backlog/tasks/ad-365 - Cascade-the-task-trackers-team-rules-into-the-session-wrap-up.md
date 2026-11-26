---
id: AD-365
title: Cascade the task tracker's team rules into the session wrap-up
status: To Do
assignee: []
created_date: '2026-11-25T18:49:56Z'
updated_date: '2026-11-26T03:02:15Z'
labels: []
milestone: m-4
dependencies:
  - AD-364
references:
  - docs/intent/session-wrap-up/session-wrap-up-design.md
  - docs/intent/task-tracker/task-tracker-specs.md
priority: medium
type: feature
ordinal: 54000
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: a20b213e-9cc5-4bd1-8407-62658bae5e42
    role: created
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The task-tracker design changed three things the session wrap-up restates (AD-336): a session record may carry a supervisor, an outbox draft has no assignee as well as no id or dependencies, and a draft for a GitHub repo with no backlog is delivered by filing an issue. The human and decision tasks the wrap-up creates stay unassigned, as TASK-SKILL-041 says of every new task (the developer's ruling, 2026-11-25), so in a shared repo they are for anyone until someone takes them; the wrap-up design should say so where it describes them. Places found by the AD-336 edge audit: WRAP-TASK-011, WRAP-TASK-013, WRAP-TASK-016, WRAP-TASK-017, WRAP-XREPO-013, WRAP-XREPO-017, the wrap-up design where it describes session records, draft keys and delivery, and the skill text in skills/session-wrap-up/references/tasks.md and SKILL.md. This is a change to another segment, so it walks that segment through LID.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The wrap-up design, specs and skill text agree with the task-tracker specs on session records, draft keys and delivery
<!-- AC:END -->
