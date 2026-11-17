---
id: AD-224
title: Re-probe the Claude Code behaviors doctrine reports
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - docs/prior-art/2026-11-13-doctrine.md#Claude Code behaviors it reports
priority: low
type: spike
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Doctrine's field notes (citing 2.1.198) report: PreToolUse hooks fail open and only exit 2 blocks; SubagentStop fires before the worktree is removed; a hooks edit in settings.local.json takes effect without restart; Workflow agent steps have the Agent tool removed; and its notes contradict each other on which base `isolation: worktree` uses. Re-probe each on the current Claude Code before any design here relies on it, and record results in docs/tool-feedback/claude-code.md or the relevant LLD.

**Why it matters:** Hook design depends on how hooks actually fail.

**Why an agent:** local probes
<!-- SECTION:DESCRIPTION:END -->
