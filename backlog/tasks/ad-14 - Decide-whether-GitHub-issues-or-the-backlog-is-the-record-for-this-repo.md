---
id: AD-14
title: Decide whether GitHub issues or the backlog is the record for this repo
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-17T20:36:00Z'
labels:
  - open-question
milestone: m-1
dependencies:
  - AD-1
references:
  - https://github.com/jmbowman/agentic_development/issues/166
  - docs/task-tracking-pilot.md
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The pilot backlog now holds every open issue's work as finer-grained tasks that link back to the issue. Choose: keep issues as the public entry point and close each when its tasks are done (the pilot's assumption); close the umbrella issues now with a pointer to their tasks; or mirror tasks to issues with a push-only sync later (the task note's piece F). Done when the choice is recorded and the umbrella issues (#155-#159, #166, #260) say where their work is tracked.

**Why it matters:** Ends double bookkeeping between issues and tasks.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-17: the developer ruled that the backlog is the record. GitHub issues stay as the public way in: a task links the issue it came from, and the issue is closed when its tasks are done (the Tasks rule in AGENTS.md says so). Saying this on the umbrella issues is part of the task that reconciles them.
<!-- SECTION:NOTES:END -->
