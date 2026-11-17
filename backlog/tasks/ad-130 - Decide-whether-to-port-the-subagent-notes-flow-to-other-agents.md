---
id: AD-130
title: Decide whether to port the subagent notes flow to other agents
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies: []
references:
  - docs/intent/subagent-notes/subagent-notes-design.md:170
priority: low
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The subagent-notes design notes that other agent tools with hooks and resumable subagents could run the same flow, since nothing depends on Claude Code beyond event names and inputs. Decide whether that's worth doing (HLD tenet on portability). Done when recorded.

**Why it matters:** Would bring notes collection to non-Claude agents.

**Why the developer:** a scope decision
<!-- SECTION:DESCRIPTION:END -->
