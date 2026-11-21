---
id: AD-3
title: Pin a first focus set and correct the agent-proposed priorities
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies: []
references:
  - backlog/focus.yml
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every priority, effort and performer in the pilot backlog was proposed by an agent. Read the two ready queues (`mise run tasks -- next --for human` and `--for agent`), change any `priority` that's wrong, and list up to three task IDs under `pins:` in `backlog/focus.yml`. Done when `focus.yml` holds the pins.

**Why it matters:** Makes the queue the developer's, which is the point of the human-authority requirement.
<!-- SECTION:DESCRIPTION:END -->
