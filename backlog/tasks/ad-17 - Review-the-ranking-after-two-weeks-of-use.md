---
id: AD-17
title: Review the ranking after two weeks of use
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies: []
references:
  - backlog/focus.yml
  - skills/task-tracker/scripts/tasks.py
priority: medium
type: review
performer: human
effort: S
defer_until: '2026-11-30'
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Compare what was actually worked on with what the queues ranked first. Where they differ, find the term that misled (or the attribute that was missing) and change a weight in `backlog/focus.yml` or a rule in the tool. Also judge whether `effort` and `priority` proposed by agents were accurate enough to rank on without confirmation. Done when the findings are recorded in the task tracker's design.

**Why it matters:** Calibrates the ranking on real choices instead of borrowed weights.
<!-- SECTION:DESCRIPTION:END -->
