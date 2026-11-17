---
id: AD-124
title: Research tracking subagents in `--agent` sessions and Workflow scripts
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies: []
references:
  - docs/intent/subagent-notes/subagent-notes-design.md:167-168
priority: medium
type: spike
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The subagent notes hooks track nothing in sessions run with `--agent` (the main agent's hooks receive an `agent_id`, so main-agent-only steps don't run) and miss agents started by a Workflow script (which don't use the `Agent` tool). Find out whether either case can be told apart or hooked (a workflow-runtime hook, another input field), and record the findings in the subagent-notes design. Done when each Deferred entry states a feasible approach or that none exists.

**Why it matters:** Extends notes collection to workflow-driven sessions, where many subagents run.

**Why an agent:** a docs-and-probe investigation
<!-- SECTION:DESCRIPTION:END -->
