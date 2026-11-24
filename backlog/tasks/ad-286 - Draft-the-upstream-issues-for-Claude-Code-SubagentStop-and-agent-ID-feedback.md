---
id: AD-286
title: Draft the upstream issues for Claude Code SubagentStop and agent-ID feedback
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T00:01:00Z'
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

## Comments

<!-- COMMENTS:BEGIN -->
author: 27e13044-1d02-40c4-90d7-0134d1214b1d
created: 2026-11-24T00:01:00Z

---

Entry 5 joins this: a PreToolUse hook's "ask" prompt doesn't show its permissionDecisionReason (2.1.331, found with Clash 0.2.0 on 2026-11-23). Before drafting, check whether Claude Code's hooks docs promise to show the reason for "ask"; the issue is a bug if they do, a request if not.

---
<!-- COMMENTS:END -->
