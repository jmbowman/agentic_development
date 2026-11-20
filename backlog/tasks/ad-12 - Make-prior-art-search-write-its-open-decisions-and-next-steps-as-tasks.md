---
id: AD-12
title: Make prior-art-search write its open decisions and next steps as tasks
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-1
dependencies:
  - AD-5
references:
  - skills/prior-art-search/SKILL.md
  - docs/task-tracking-pilot.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prior-art notes end with open decisions, suggested orders and leads that nothing tracks; this pilot found about a hundred such items across twenty notes. Change the skill so that, when a note is saved, each open decision becomes a human task and each next step an agent task, linked from the note. Goes through LID in the prior-art-search segment. Done when a search in a scratch repo produces the task files and an eval case covers it.

From the task-tracker LLD (AD-5, *Other skills*): the skill tells the agent to create the tasks using the task-tracker skill's rules when that skill is installed, and its own short description of a task otherwise. A search task is `type: search`.

**Why it matters:** Stops research verdicts becoming orphaned work.
<!-- SECTION:DESCRIPTION:END -->
