---
id: AD-71
title: Re-pin the harvester when upstream merges a fork proposal
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - process
milestone: m-3
dependencies:
  - AD-309
references:
  - pyproject.toml:12
  - skills/prior-art-search/scripts/harvest.py:5
  - paper-search-mcp:AGENTS.md#Branches
  - docs/tool-feedback/paper-search-mcp.md#Upstream context for the proposal
priority: medium
type: chore
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development pins the fork's integration commit 155f360 in `pyproject.toml:12` and in `skills/prior-art-search/scripts/harvest.py:5`. When upstream merges a proposal, the fork drops that branch from integration (fork AGENTS.md); update both pins to the new integration commit (or to upstream, if nothing fork-only remains) and rerun the harvester's tests. Done when both pins match and tests pass.

**Why it matters:** Keeps the harvester on maintained code and the two pins in step.

**Why an agent:** a pin bump with tests
<!-- SECTION:DESCRIPTION:END -->
