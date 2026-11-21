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
  - evals/README.md
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 83baf9d8-f511-40e3-875d-3d561ab7a7c4
    role: created
    date: '2026-11-16'
  - agent: claude-code
    id: f4b2080f-847f-4a0d-a503-34339722eeb7
    role: worked
    date: '2026-11-16'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run with `mise run eval` the cases quick-pass-escalates, quick-pass-close-candidates, quick-pass-gap, quick-pass-small-extension and quick-pass-small-library (all never run), which cover the open eval-only specs PRIOR-EFF-005, PRIOR-EFF-008, PRIOR-SRCH-017, PRIOR-SRCH-022, PRIOR-LIC-007, PRIOR-LIC-009, PRIOR-LIC-010 and PRIOR-RPT-003. The skill text already carries these specs; only the eval verification is missing. Paste the output for triage.

**Why it matters:** Verifies that quick passes escalate when they should, the commonest path through the skill.

**Why the developer:** the developer runs paid evals

**Status when filed (partly-done):** skill text carries the specs (commits 2d835c7, 02137cf); latest-results.md shows every case 'never run'
<!-- SECTION:DESCRIPTION:END -->
