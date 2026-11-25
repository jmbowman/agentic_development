---
id: AD-360
title: Check that `@spec` annotations sit above the code they annotate
status: To Do
assignee: []
created_date: '2026-11-25T04:19:00Z'
labels:
  - loose-end
milestone: m-6
dependencies: []
references:
  - AD-354
priority: low
type: chore
ordinal: 50000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 3db836d3-b908-46e0-9723-e32403b8aa4e
    role: created
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
LID places a `@spec` annotation at the entry point of the behaviour it annotates: on the line above the function, class or decorator, or among a module's opening lines for a whole-module behaviour. During AD-354 three annotations in `tasks.py` sat inside function bodies, and nothing caught them. Three more sit inside bodies today: `scripts/run_evals.py:199`, and `skills/prior-art-search/scripts/harvest.py:1233` and `:1661`. Those files belong to other segments, so confirm with the developer before moving them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A test fails when a `@spec` line in a tracked Python file (outside `_vendor/`) is neither among the module's opening lines nor directly above a `def`, `class` or decorator, possibly after other comment lines
- [ ] #2 Every existing `@spec` annotation passes that test, and `mise run check` passes
<!-- AC:END -->
