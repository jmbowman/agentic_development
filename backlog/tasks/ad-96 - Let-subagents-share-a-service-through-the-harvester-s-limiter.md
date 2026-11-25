---
id: AD-96
title: Let subagents share a service through the harvester's limiter
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T06:10:00Z'
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

## Comments

<!-- COMMENTS:BEGIN -->
author: claude-code:7491ae04
created: 2026-11-24T04:00:00Z

---

From AD-92 (2026-11-23): AD-92 leaves full-text reads from arxiv.org with the agent (AD-65 owns them), so after it only OpenAlex and Semantic Scholar are harvester-only; arXiv joins them when AD-65 lands.

---

author: claude-code:7491ae04
created: 2026-11-24T06:10:00Z

---

From the AD-92 review wave (2026-11-24): the block SKILL.md has the main agent paste into subagent prompts lists the harvester actions for all three services, but never tells a subagent to keep to the services it was assigned (PRIOR-SRCH-014 is stated only where a subagent cannot see it). Settle that when this rule is relaxed.

---
<!-- COMMENTS:END -->
