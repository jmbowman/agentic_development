---
id: AD-94
title: Decide when the harvester counts as verified on real searches
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies:
  - AD-43
  - AD-363
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:526
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The design removes the agents' fallback of sending the harvester's requests themselves 'once the harvester is integrated and verified on real searches', after which the skill requires `uv`. Decide what evidence counts (for example a passing harvester-literature eval plus N real searches) and whether requiring `uv` is acceptable. Done when the criterion is recorded in the LLD.

**Why it matters:** Gates simplifying the skill to one way of sending each request.

**Why the developer:** judgment on readiness and on adding a hard dependency
<!-- SECTION:DESCRIPTION:END -->
