---
id: AD-329
title: Lint stray files in Backlog.md's docs and decisions folders
status: To Do
assignee: []
created_date: '2026-11-19T12:54:00Z'
labels: []
milestone: m-1
dependencies:
  - AD-5
references:
  - docs/intent/task-tracker/task-tracker-design.md
priority: low
type: feature
ordinal: 16000
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The task tracker doesn't read Backlog.md's docs/ and decisions/ folders: reference knowledge lives in the repo's docs/, and decisions live in the arrow of intent (docs/intent/task-tracker/task-tracker-design.md, Decisions & Alternatives). A file created there, for example by running backlog doc create or backlog decision create despite the skill's rules, would sit in a store that no view reads. Add a check finding for any file in the backlog directory's docs/ or decisions/ (and their archive folders), naming where the content belongs instead, as the tool already does for Backlog.md's drafts/. Done when the finding has an EARS spec in the task-tracker segment, a test, and the code.
<!-- SECTION:DESCRIPTION:END -->
