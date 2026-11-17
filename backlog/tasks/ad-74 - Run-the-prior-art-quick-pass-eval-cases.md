---
id: AD-74
title: Run the prior-art quick-pass eval cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:42
  - docs/intent/prior-art-search/prior-art-search-specs.md:45
  - docs/intent/prior-art-search/prior-art-search-specs.md:52-53
  - docs/intent/prior-art-search/prior-art-search-specs.md:246-249
  - docs/intent/prior-art-search/prior-art-search-specs.md:283
  - evals/prior-art-search/latest-results.md
  - PRIOR-EFF-005
  - PRIOR-EFF-008
  - PRIOR-SRCH-017
  - PRIOR-SRCH-022
  - PRIOR-LIC-007
  - PRIOR-LIC-009
  - PRIOR-LIC-010
  - PRIOR-RPT-003
  - session:83baf9d8 2026-11-16
  - session:f4b2080f 2026-11-16
  - evals/README.md
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run with `mise run eval` the cases quick-pass-escalates, quick-pass-close-candidates, quick-pass-gap, quick-pass-small-extension and quick-pass-small-library (all never run), which cover the open eval-only specs PRIOR-EFF-005, PRIOR-EFF-008, PRIOR-SRCH-017, PRIOR-SRCH-022, PRIOR-LIC-007, PRIOR-LIC-009, PRIOR-LIC-010 and PRIOR-RPT-003. The skill text already carries these specs; only the eval verification is missing. Paste the output for triage.

**Why it matters:** Verifies that quick passes escalate when they should, the commonest path through the skill.

**Why the developer:** the developer runs paid evals

**Status when filed (partly-done):** skill text carries the specs (commits 2d835c7, 02137cf); latest-results.md shows every case 'never run'
<!-- SECTION:DESCRIPTION:END -->
