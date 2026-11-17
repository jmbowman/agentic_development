---
id: AD-166
title: Build the reviewer eval corpus from this repo's escapes and seeded defects
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies:
  - AD-163
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#15.
    Evaluating the process itself
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Slice 3: mine this repo's history for defects that review missed and evals or the developer later found (escapes), add settled clean changes for false-alarm scoring, have the developer confirm each case, and add seeded defects while history is thin. Method from layered-code-review (revert-mined cases, finding classes fixed/wrong/intentional/not important) and craftsman's seeded suite. Done when a scorer reports recall and clean false-alarm rate per lens.

**Why it matters:** Every later reviewer change is judged against it.

**Why an agent:** corpus building and scorer code; the developer only confirms cases
<!-- SECTION:DESCRIPTION:END -->
