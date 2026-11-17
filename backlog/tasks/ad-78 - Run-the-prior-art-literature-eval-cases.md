---
id: AD-78
title: Run the prior-art literature eval cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:34
  - docs/intent/prior-art-search/prior-art-search-specs.md:63
  - docs/intent/prior-art-search/prior-art-search-specs.md:65
  - docs/intent/prior-art-search/prior-art-search-specs.md:91-107
  - docs/intent/prior-art-search/prior-art-search-specs.md:116
  - docs/intent/prior-art-search/prior-art-search-specs.md:124
  - docs/intent/prior-art-search/prior-art-search-specs.md:264
  - docs/intent/prior-art-search/prior-art-search-specs.md:281-289
  - docs/intent/prior-art-search/prior-art-search-specs.md:301
  - PRIOR-TRIG-004
  - PRIOR-LIT-001
  - PRIOR-LIT-017
  - PRIOR-SAVE-009
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run with `mise run eval` the cases approach-need-literature, approach-only-findings, quick-pass-approach, paper-supplied-update and approach-question-asks-first (all never run). They cover the open eval-only specs PRIOR-TRIG-004, PRIOR-LIT-001 to PRIOR-LIT-014, PRIOR-LIT-016, PRIOR-LIT-017, PRIOR-SRCH-013, PRIOR-SRCH-015, PRIOR-ACC-006, PRIOR-ACC-014, PRIOR-SRC-015, PRIOR-RPT-001, PRIOR-RPT-002, PRIOR-RPT-008, PRIOR-RPT-009 and PRIOR-SAVE-009. Paste the output for triage.

**Why it matters:** The literature half of the skill has never been checked by an eval at all.

**Why the developer:** the developer runs paid evals

**Status when filed (partly-done):** skill text carries the literature specs (commit 02137cf, 'Worth retrieving manually' in SKILL.md); cases never run
<!-- SECTION:DESCRIPTION:END -->
