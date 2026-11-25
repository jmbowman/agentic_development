---
id: AD-359
title: >-
  Decide how an agent's own arXiv full-text reads are paced against the
  harvester
status: To Do
assignee: []
created_date: '2026-11-25T03:57:00Z'
labels:
  - loose-end
milestone: m-3
dependencies: []
references:
  - PRIOR-SCR-110
  - AD-92
  - AD-65
priority: low
type: decision
ordinal: 49000
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 7491ae04-e559-4545-95a8-b20f528642de
    role: created
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agents still read an arXiv paper's full text from `arxiv.org` themselves, outside the harvester's limiter. PRIOR-SCR-110 has them wait out arXiv's interval after their last harvester run for arXiv before such a read, and 15 seconds between reads. Two points are open. Nothing says whether the next harvester run for arXiv should wait after a full-text read, though arXiv counts both as one client. And the spec doesn't say whether the interval runs from the harvester invocation's end or from its last request. AD-65 would make both moot by moving the reads into the harvester.

**Why it matters:** the skill's own requests to arXiv stay within its stated limits.

**Why the developer:** it chooses between adding a rule now and leaving the gap until AD-65.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The ruling is recorded in the Harvester section of the prior-art-search design, with PRIOR-SCR-110 and the skill text changed to match, or the gap is recorded there as accepted until AD-65.
<!-- AC:END -->
