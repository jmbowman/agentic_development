---
id: AD-76
title: Run the prior-art full-method online eval cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:58-70
  - docs/intent/prior-art-search/prior-art-search-specs.md:82-83
  - evals/prior-art-search/shared-config-full/case.yaml
  - evals/prior-art-search/lock-refresh-full/case.yaml
  - PRIOR-SRCH-008
  - PRIOR-SRCH-010
  - PRIOR-SRCH-018
  - PRIOR-SRCH-019
  - PRIOR-SRCH-020
  - PRIOR-SRCH-021
  - PRIOR-CLS-009
  - PRIOR-CLS-010
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run with `mise run eval` the online full-method cases shared-config-full and lock-refresh-full (both never run), which cover the open eval-only search-tactics specs PRIOR-SRCH-008, PRIOR-SRCH-010, PRIOR-SRCH-017, PRIOR-SRCH-018, PRIOR-SRCH-019, PRIOR-SRCH-020, PRIOR-SRCH-021, PRIOR-SRCH-022, PRIOR-CLS-009 and PRIOR-CLS-010. Paste the output for triage.

**Why it matters:** Shows the new GitHub topic and sort tactics actually find more candidates.

**Why the developer:** the developer runs paid evals

**Status when filed (partly-done):** skill text carries them (commit 2d835c7, `search/topics` and `pushed:>` in references/sources.md); cases never run
<!-- SECTION:DESCRIPTION:END -->
