---
id: AD-369
title: >-
  Rule on whether the developer reads the artifact before the findings at each
  stop
status: Done
assignee: []
created_date: '2026-11-26T14:09:25Z'
updated_date: '2026-11-27T21:43:46Z'
labels: []
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#4. Spec
    and plan review
priority: medium
type: decision
ordinal: 56000
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
    role: created
    date: '2026-11-26'
  - agent: claude-code
    id: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
    role: finished
    date: '2026-11-27'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis stage 4 recommends that at each LID stop the developer reads the artifact first and sees the reviewers' findings after, that the stop summary not lead with an agent's summary, and that a clean wave not be grounds for a lighter read (evidence: a crossover study found students who started with an assistant improved about half as much). AD-242 records the related general habit (a reviewer forms their own view before reading AI review) from the review-and-comprehension note; rule with it in view. The synthesis bundled this into its Decision 1, but the ruling on review stopping (docs/decisions/review-wave-stopping.md) covers only when waves stop, so this needs its own ruling. Done when the developer has ruled and the ruling is recorded in the document it governs, or in this task's final summary until AD-180 writes it into AGENTS.md and the HLD.

**Why it matters:** Unblocks AD-180 and decides how every stop summary is ordered.

**Why the developer:** it governs how the developer reviews
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ruled: while a review loop is running, a question to the developer leads with the finding and only the context needed to answer it; the developer is not expected to read intermediate artifacts, because forks arrive throughout the loop and re-reading changing specs or code before each answer has little value. Once the loop has stopped, the final stop summary leads with the artifact (what changed and where to read it), with the per-wave findings after it as a record, so the findings do not frame the developer's one read of the finished artifact. No document governs this yet: AD-199 writes it into this repo's AGENTS.md as an interim rule, and AD-180 carries the portable form, which waits on AD-372.
<!-- SECTION:FINAL_SUMMARY:END -->
