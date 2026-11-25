---
id: AD-322
title: Add a newest-first sort to the harvester's arXiv search
status: Done
assignee: []
created_date: '2026-11-18T04:30:00Z'
updated_date: '2026-11-24T06:12:00Z'
labels: []
milestone: m-3
dependencies: []
references:
  - docs/prior-art/2026-11-17-in-repo-architecture-maps.md#Coverage ledger
priority: low
type: feature
ordinal: 9000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 7491ae04-e559-4545-95a8-b20f528642de
    role: finished
    date: '2026-11-24'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The search behind docs/prior-art/2026-11-17-in-repo-architecture-maps.md had to send its last-12-months arXiv queries itself (sortBy=submittedDate), because skills/prior-art-search/scripts/harvest.py has no sort option, which bypasses the harvester's limiter. Add one, with specs, tests and skill text. Related: AD-92. Done when the skill's recent-preprints step runs through the harvester.

**Why it matters:** One limiter for every arXiv request, and the snowball's last step stops being manual.

**Why an agent:** a small LID build change
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Done as part of AD-92: harvest.py takes --sort submitted for an arXiv search (PRIOR-SCR-129), and the skill text sends the recent-preprints step through it. Verified by tests/test_harvester.py and a live newest-first cat:cs.SE search.
<!-- SECTION:FINAL_SUMMARY:END -->
