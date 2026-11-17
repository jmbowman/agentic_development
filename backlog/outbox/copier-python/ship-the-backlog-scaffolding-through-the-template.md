---
title: Ship the backlog scaffolding through the template
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- https://github.com/jmbowman/agentic_development/blob/main/docs/task-tracking-pilot.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
external_blockers:
- agentic_development#AD-5
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Render `backlog/config.yml` (remote operations and auto-commit off, no status callbacks), an empty `backlog/focus.yml`, the Backlog.md pin and the `tasks` mise task into every repo generated from the template, so each consumer has the same task store and queue. Depends on the task tracker's design in agentic_development being settled and released. Done when a fresh copy passes its check with an empty backlog.

**Why it matters:** Every repo in the system gets the tracker without hand setup.

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
