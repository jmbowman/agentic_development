---
id: AD-363
title: Re-run the harvester-literature eval case after the round rules
status: To Do
assignee: []
created_date: '2026-11-25T18:43:04Z'
labels:
  - spec
milestone: m-3
dependencies:
  - AD-82
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md
  - docs/review-log/2026-11-25-prior-art-search-harvester.md
  - evals/prior-art-search/harvester-literature
  - PRIOR-SCR-102
  - PRIOR-SCR-103
  - PRIOR-SCR-104
  - PRIOR-SCR-106
  - PRIOR-SCR-107
  - PRIOR-SCR-109
  - PRIOR-SCR-136
  - PRIOR-SCR-137
  - PRIOR-SCR-138
  - PRIOR-SCR-139
  - PRIOR-SCR-140
  - PRIOR-SCR-141
  - PRIOR-SCR-142
  - PRIOR-SCR-143
  - PRIOR-SCR-144
  - PRIOR-SCR-145
  - PRIOR-SCR-146
priority: medium
type: eval
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 6becb69f-47c5-4e32-b087-a3ab5e8fc7dd
    role: created
    date: '2026-11-25'
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-25 run of `harvester-literature` showed a subagent rerunning throttled arXiv queries under a higher `--round` number. The skill text, specs and grader now say what makes a round later (PRIOR-SCR-136 to PRIOR-SCR-146, and the narrowed PRIOR-SCR-107). No run has exercised them, and PRIOR-SCR-102, PRIOR-SCR-103, PRIOR-SCR-104, PRIOR-SCR-106, PRIOR-SCR-107 and PRIOR-SCR-109 are still open from earlier: the 2026-11-25 run never reached the conditions they describe. Re-run the case with `mise run eval` (with `TMPDIR` outside `/tmp` and `--keep-temp`), and paste the output for triage against the full trace, since the judges see only its first 100,000 characters.

**Why it matters:** the new round rules are verified only by this eval.

**Why the developer:** the developer runs paid evals
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The case has been run once on the changed skill text and its output triaged against the kept trace
- [ ] #2 The review log and latest-results rows are updated, and each of the cited specs the run exercised and passed is marked
<!-- AC:END -->
