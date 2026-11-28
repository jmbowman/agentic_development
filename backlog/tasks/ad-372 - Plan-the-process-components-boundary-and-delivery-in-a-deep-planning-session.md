---
id: AD-372
title: Plan the process component's boundary and delivery in a deep-planning session
status: To Do
assignee: []
created_date: '2026-11-27T21:43:20Z'
labels: []
milestone: m-6
dependencies:
  - AD-371
references:
  - docs/high-level-design.md
  - docs/decisions/review-wave-stopping.md
priority: high
type: decision
ordinal: 59000
performer: human
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
    role: created
    date: '2026-11-27'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HLD plans review-wave orchestration, a spec-review loop and other process guardrails as separate components, and says process guidance ships as skills in the skills package. The synthesis treats spec review, edge audit, tests first, fix loops, review waves, triage, the ledger and commit gates as one connected process whose parts feed each other (findings routed back up the arrow, the ledger feeding the stop check and the merge gate), so one process component with a single entry point may fit better than a skill per stage. How its guidance reaches template consumers and gets used by default is also unsettled. Using AD-371's results, choose the component boundary and the delivery and loading mechanism through LID Phase 1 (options sketched, the developer selects), then update the HLD and re-scope the tasks that build process pieces (AD-163, AD-164, AD-175, AD-177, AD-178, AD-180, AD-193, AD-199, AD-214, AD-215). Done when the developer has ruled and the HLD records it.

**Why it matters:** Every process slice depends on where its guidance lives and how agents find it.

**Why the developer:** an HLD-level choice between options; suited to a deep-planning session
<!-- SECTION:DESCRIPTION:END -->
