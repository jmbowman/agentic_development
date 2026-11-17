---
id: AD-6
title: Make session-wrap-up write loose ends as tasks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies:
  - AD-5
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
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The wrap-up skill reports loose ends as prose, which nothing then tracks; 29 untracked ones had to be recovered from session transcripts for this pilot. Change the skill so each confirmed loose end becomes a task file in `backlog/tasks/` (or a draft under `backlog/outbox/<repo>/` when it belongs elsewhere), with performer, effort and source set, after the developer confirms the text as the skill already requires. Goes through LID in the session-wrap-up segment. Done when a wrap-up in a scratch repo produces task files and an eval case covers it.

**Why it matters:** Closes the largest leak that made the backlog chaotic.
<!-- SECTION:DESCRIPTION:END -->
