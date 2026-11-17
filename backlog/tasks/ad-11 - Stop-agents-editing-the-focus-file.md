---
id: AD-11
title: Stop agents editing the focus file
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-1
dependencies:
  - AD-2
references:
  - backlog/focus.yml
  - docs/task-tracking-pilot.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The pilot keeps the developer's decisions (pins, ranking weights) in `backlog/focus.yml` so that protecting them is a path rule rather than a per-field diff check. Add the rule: a Claude Code permission that denies Edit and Write on that file, and a check (prek and CI) that fails when a commit carrying the agent trailer touches it. Done when an agent's attempt to edit the file is refused and the check has a test.

**Why it matters:** Turns human authority over priority from a convention into something enforced.
<!-- SECTION:DESCRIPTION:END -->
