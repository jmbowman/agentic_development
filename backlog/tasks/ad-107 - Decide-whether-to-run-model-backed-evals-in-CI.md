---
id: AD-107
title: Decide whether to run model-backed evals in CI
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-3
dependencies: []
references:
  - docs/intent/prior-art-search/prior-art-search-design.md:532
  - docs/intent/prior-art-search/prior-art-search-design.md#Testing
priority: low
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The prior-art-search LLD defers model-backed evals in CI; today evals run by hand because each run costs model calls. Decide whether any subset (for example cheap trigger cases on release tags) should run in CI. Done when recorded in the LLD's Decisions table or left deferred with a reason.

**Why it matters:** Would catch skill regressions without relying on hand runs.

**Why the developer:** a cost decision with credentials in CI
<!-- SECTION:DESCRIPTION:END -->
