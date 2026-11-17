---
id: AD-126
title: Decide whether to filter which subagents get the notes question
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies: []
references:
  - docs/intent/subagent-notes/subagent-notes-design.md:166
  - docs/intent/subagent-notes/subagent-notes-design.md:169
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every tracked subagent is asked the notes question, and one already asked isn't asked again after later work. The design defers an opt-out filter (skip agents with no tool calls, or a brief marker) until replies of `none` are shown to cost more than they save, and leaves re-asking after later work open. Gather the ratio of `none` replies from notes directories and decide. Done when recorded in the subagent-notes design.

**Why it matters:** Trims housekeeping turns and permission prompts if most replies are empty.

**Why the developer:** a cost-versus-value judgment

**Also waits on (not tracked as a task):** evidence on the cost of `none` replies
<!-- SECTION:DESCRIPTION:END -->
