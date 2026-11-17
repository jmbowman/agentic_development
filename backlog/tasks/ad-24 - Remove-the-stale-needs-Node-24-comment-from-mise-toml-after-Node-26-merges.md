---
id: AD-24
title: Remove the stale needs-Node-24 comment from mise.toml after Node 26 merges
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-2
dependencies:
  - AD-20
references:
  - mise.toml:15
  - https://github.com/jmbowman/agentic_development/pull/121
priority: medium
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
mise.toml line 15 says Renovate runs as a CLI in the preset tests and this Renovate release needs Node 24. After PR #121 moves node to 26.x this comment is false (Renovate 44.239.1 supports ^26.13.0). Update or remove the comment, and check docs for any repeated claim (grep for Node 24).

**Why it matters:** Keeps config comments true.

**Why an agent:** one-line config comment edit
<!-- SECTION:DESCRIPTION:END -->
