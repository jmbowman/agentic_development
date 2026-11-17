---
id: AD-96
title: Let subagents share a service through the harvester's limiter
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies:
  - AD-92
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:527
  - PRIOR-SRCH-014
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The harvester's limiter holds across processes, so subagents could share a service through it instead of the rule that gives each service to one agent at a time (PRIOR-SRCH-014). That rule stays while agents also send some requests to these services themselves. Once they don't, relax PRIOR-SRCH-014 for harvester-only services, with specs and skill text. Done when the rule is relaxed and evals still pass.

**Why it matters:** Lets literature searches parallelize across subagents.

**Why an agent:** spec and skill-text change once its prerequisite lands
<!-- SECTION:DESCRIPTION:END -->
