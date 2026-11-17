---
id: AD-95
title: Remove the fallback to the agent's own literature requests
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies:
  - AD-94
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:526
  - PRIOR-SCR-102
  - PRIOR-SCR-108
  - PRIOR-SCR-109
  - README.md#What's in this repo
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the harvester is verified, remove the rule that lets the agent send the harvester's requests itself (PRIOR-SCR-102, -108, -109 and related skill text in 'When the harvester can't run'), so the skill needs `uv` and has one way to send each request. Update specs, tests, SKILL.md and the README's 'Without uv' sentence. Done when `mise run check` passes.

**Why it matters:** Simplifies the skill and removes a second, unpaced request path.

**Why an agent:** spec and skill-text edits once decided
<!-- SECTION:DESCRIPTION:END -->
