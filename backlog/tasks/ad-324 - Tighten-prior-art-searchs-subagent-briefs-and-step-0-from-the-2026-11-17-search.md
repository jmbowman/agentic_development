---
id: AD-324
title: >-
  Tighten prior-art-search's subagent briefs and step 0 from the 2026-11-17
  search
status: To Do
assignee: []
created_date: '2026-11-18T12:43:00Z'
labels: []
milestone: m-3
dependencies: []
references:
  - docs/prior-art/2026-11-17-in-repo-architecture-maps.md
priority: low
type: feature
ordinal: 11000
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The in-repo architecture-maps search (docs/prior-art/2026-11-17-in-repo-architecture-maps.md) showed five gaps in skills/prior-art-search:
- A harvesting subagent stopped after one snowball round "for budget" though its brief set none. Briefs should state that no token budget applies beyond the skill's own limits.
- Subagents recorded `read_depth: full` for READMEs they fetched whole but read as head plus keyword greps. Say what `full` requires of the reading itself, not just of the fetch.
- Step 0 missed an earlier note's rulings on candidates found later (LikeC4, CodeBoarding, Mermaid in LLDs). Once serious candidates are found, grep the earlier notes for their names.
- Cloned candidate repos carry their own CLAUDE.md or AGENTS.md, which the harness surfaces to a subagent as if they were instructions. The pasted rules block should name this case.
- A truncated listing (`| head`) nearly supported a false absence claim. An absence claim needs an untruncated listing.

Walk LID's arrow for the skill: specs, then skill text, then evals where they cover it. Done when the skill covers all five and checks pass.

**Why it matters:** Each gap cost a review finding or a re-run in the search.

**Why an agent:** LID build work with the gaps stated
<!-- SECTION:DESCRIPTION:END -->
