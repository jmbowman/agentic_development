---
id: AD-80
title: Run the prior-art access-settings eval cases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
  - partly-done
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:64
  - docs/intent/prior-art-search/prior-art-search-specs.md:66
  - docs/intent/prior-art-search/prior-art-search-specs.md:111-125
  - docs/intent/prior-art-search/prior-art-search-specs.md:260
  - docs/intent/prior-art-search/prior-art-search-specs.md:269
  - PRIOR-ACC-001
  - PRIOR-ACC-015
  - PRIOR-SRCH-014
  - PRIOR-SRC-010
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run with `mise run eval` the cases settings-canary (last run once on 2026-11-09, before later spec changes), settings-not-ignored and settings-required-missing (never run). They cover the open eval-only specs PRIOR-ACC-001 to PRIOR-ACC-009, PRIOR-ACC-012, PRIOR-ACC-013, PRIOR-ACC-015, PRIOR-SRCH-014, PRIOR-SRCH-016, PRIOR-SRC-007 and PRIOR-SRC-010. Paste the output for triage.

**Why it matters:** Verifies that API keys never leak into notes, prompts or commands.

**Why the developer:** the developer runs paid evals and holds the keys

**Status when filed (partly-done):** settings-canary passed 1 run on 2026-11-09; the other two never run; specs still `[ ]`
<!-- SECTION:DESCRIPTION:END -->
