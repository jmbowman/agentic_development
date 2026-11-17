---
id: AD-56
title: Write the one-search-at-a-time rule into prior-art-search and sources.md
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
  - skills/prior-art-search/references/sources.md
priority: medium
type: docs
performer: agent
agent_tier: fast
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comment on #155: route rate limits are shared by every session on the machine (arXiv says so), so two concurrent searches can exceed a limit each respects alone. Add to SKILL.md's Working in parallel section and to sources.md's Rate limits: run one prior-art search at a time across sessions, not just one subagent per service within a search. Done means both texts say it and a check or spec covers it.

**Why it matters:** Prevents rate-limit violations from concurrent searches.

**Why an agent:** small text edit
<!-- SECTION:DESCRIPTION:END -->
