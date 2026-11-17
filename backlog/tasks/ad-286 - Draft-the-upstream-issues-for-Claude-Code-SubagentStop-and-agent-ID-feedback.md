---
id: AD-286
title: Draft the upstream issues for Claude Code SubagentStop and agent-ID feedback
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - tool-feedback
  - upstream
milestone: m-9
dependencies: []
references:
  - docs/tool-feedback/claude-code.md
  - docs/prior-art/2026-11-11-subagent-process-notes.md
priority: medium
type: upstream
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Draft issues for Claude Code from docs/tool-feedback/claude-code.md entries 1-4: a SubagentStop block replaces the subagent's report outside auto mode; a block after SubagentHandback is silently ignored; no agent ID in a foreground Agent result outside auto mode; a background launch result lacks agentType (2.1.323/2.1.325). Entry 1 must reference the closed, locked anthropics/claude-code#85917 and ask for the change or documentation, since a maintainer called the behavior a product decision. Done when drafts are shown inline for approval.

**Why it matters:** The subagent-notes hooks work around all four; upstream fixes would simplify them.

**Why an agent:** text from recorded probe evidence
<!-- SECTION:DESCRIPTION:END -->
