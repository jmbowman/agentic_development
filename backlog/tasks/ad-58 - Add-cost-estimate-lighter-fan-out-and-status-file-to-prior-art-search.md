---
id: AD-58
title: Add cost estimate, lighter fan-out and status file to prior-art-search
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/155
  - skills/prior-art-search/SKILL.md
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #155: before fanning out subagents, estimate cost and offer a lighter fan-out; keep a status file (scope, decisions, files, next steps) so a fresh session can resume; when a usage cap forces a stop mid-round, a wrap up within about 8 calls, flush records, list what is left message worked. Add these to SKILL.md with spec and test. Round 1 on five parallel subagents cost about 1.1M tokens.

**Why it matters:** Searches become cheaper to plan and resumable.

**Why an agent:** skill text edit
<!-- SECTION:DESCRIPTION:END -->
