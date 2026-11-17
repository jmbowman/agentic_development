---
id: AD-83
title: Run the prior-art source-reading and links eval cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:86-87
  - docs/intent/prior-art-search/prior-art-search-specs.md:246-247
  - docs/intent/prior-art-search/prior-art-search-specs.md:260-268
  - docs/intent/prior-art-search/prior-art-search-specs.md:288-289
  - PRIOR-SRC-011
  - PRIOR-SRC-012
  - PRIOR-SRC-014
  - PRIOR-CLS-013
  - PRIOR-CLS-014
  - PRIOR-LIC-008
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run with `mise run eval` the cases offline-local-candidates, snippet-reads, links-in-report and privacy-public (never run). They cover the open eval-only specs PRIOR-SRC-011, PRIOR-SRC-012, PRIOR-SRC-013, PRIOR-SRC-014, PRIOR-SRC-016, PRIOR-CLS-013, PRIOR-CLS-014, PRIOR-LIC-007, PRIOR-LIC-008, PRIOR-RPT-008, PRIOR-RPT-009 and PRIOR-SRC-007. Paste the output for triage.

**Why it matters:** Verifies that snippet reads and lookalike copies can't produce a false 'verified' or adopt verdict.

**Why the developer:** the developer runs paid evals

**Status when filed (partly-done):** skill text carries them ('possible copy', 'Commons Clause' in SKILL.md and references/verification.md); cases never run
<!-- SECTION:DESCRIPTION:END -->
