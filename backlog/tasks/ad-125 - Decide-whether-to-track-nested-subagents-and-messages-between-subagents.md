---
id: AD-125
title: Decide whether to track nested subagents and messages between subagents
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies: []
references:
  - docs/intent/subagent-notes/subagent-notes-design.md:162
  - docs/intent/subagent-notes/subagent-notes-design.md:165
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The subagent notes hooks don't track subagents launched by subagents, and a run started by another subagent's `SendMessage` neither opens nor closes the capture window. Decide whether these gaps matter enough to design for. Done when they're kept as accepted limits with a reason or moved into a design change.

**Why it matters:** Clarifies how much of a session's friction the notes can ever see.

**Why the developer:** scope judgment
<!-- SECTION:DESCRIPTION:END -->
