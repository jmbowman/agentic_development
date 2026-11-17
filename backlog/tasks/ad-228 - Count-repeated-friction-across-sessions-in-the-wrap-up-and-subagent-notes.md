---
id: AD-228
title: Count repeated friction across sessions in the wrap-up and subagent notes
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - docs/prior-art/2026-11-13-doctrine.md#Ideas worth testing
priority: low
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Doctrine's capture-by-prompt fell from 373 observations in one month to 7 two months later, and it counts repeated friction across sessions rather than merging per session. Test the same in the session-wrap-up skill: keep a count per friction item across wrap-ups so recurrence, not volume, drives promotion to a check or rule. Done when the wrap-up records a count and a spec and eval cover it.

**Why it matters:** Surfaces the lessons that keep recurring.

**Why an agent:** skill change through LID
<!-- SECTION:DESCRIPTION:END -->
