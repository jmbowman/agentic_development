---
id: AD-123
title: Verify whether SubagentStop fires when a subagent is interrupted or killed
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies: []
references:
  - docs/intent/subagent-notes/subagent-notes-design.md:164
priority: medium
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The subagent notes design says it is unverified whether Claude Code fires SubagentStop when a subagent run is interrupted or killed; if not, its `.state` stays `running` and it isn't asked for notes until a later message runs it to a normal stop. Probe it in a scratch session (not this repo) and record the answer, with Claude Code version, in the Deferred entry or as a design change. Done when the entry says verified, with the result.

**Why it matters:** Shows whether interrupted subagents silently lose their notes.

**Why an agent:** a scripted probe an agent can run
<!-- SECTION:DESCRIPTION:END -->
