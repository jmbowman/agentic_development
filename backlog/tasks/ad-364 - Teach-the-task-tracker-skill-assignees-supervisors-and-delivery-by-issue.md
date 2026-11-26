---
id: AD-364
title: Teach the task-tracker skill assignees, supervisors and delivery by issue
status: To Do
assignee: []
created_date: '2026-11-25T18:49:55Z'
updated_date: '2026-11-26T13:02:35Z'
labels: []
milestone: m-1
dependencies:
  - AD-5.3
references:
  - docs/intent/task-tracker/task-tracker-design.md
  - docs/intent/task-tracker/task-tracker-specs.md
priority: medium
type: feature
ordinal: 53000
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
The task-tracker design now covers several developers sharing a repo (AD-336): an assignee is the person who does a human task or supervises an agent task, session records carry a supervisor handle, agents learn the current user from the task tool and take work from the queue narrowed to that user, and a draft for a GitHub repo with no backlog is delivered by filing an issue. The skill text and its format reference still tell agents to leave assignee empty and describe one way of delivering a draft. Specs in scope: TASK-SKILL-004, TASK-SKILL-012, TASK-SKILL-017, TASK-SKILL-019, TASK-SKILL-034 to TASK-SKILL-044 and TASK-REPO-015. TASK-SKILL-035 and TASK-SKILL-044 are worded as skill-text rules because a test requires an eval case for every spec marked (eval); when this task adds the case, they become agent-behaviour specs with that marker, as the design's Testing section expects. The rules name the tool commands user and next --mine, which AD-5.3 builds. The handle form needs quoting in YAML, which the format reference must say. backlog/README.md lists the next options and needs the same update.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The skill and its format reference state each rule the specs in scope give, and the structure tests that cite those specs pass
- [ ] #2 An eval case covers an agent taking up an unassigned agent task: it adds the current user as assignee and supervisor, and never its own name
- [ ] #3 The contract test assigns a task with the pinned Backlog.md and passes
- [ ] #4 backlog/README.md lists the next options for narrowing to a person and the user command, and the root README mentions team use and the per-machine user setting
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: a20b213e-9cc5-4bd1-8407-62658bae5e42
created: 2026-11-26T13:02:35Z

---

From AD-336's edge audit and review wave (2026-11-25). Forks left in TASK-SKILL-019 for this task's own edge audit: how an agent tells that the receiving repo has a backlog (a local clone, the forge, or asking the developer); who creates the receiving task (the delivering agent, or a session or person in that repo); and whether "each reference" means only the blockers of open tasks and drafts or every mention in the backlog. Two facts for the contract test (TASK-REPO-015), found by running Backlog.md 1.57.2: `task edit` moves custom keys below `ordinal`, so compare parsed values, not text; and `-a "@alex, sam"` trims the space after the comma, so "as typed" holds only for names with no spaces around them.

---
<!-- COMMENTS:END -->
