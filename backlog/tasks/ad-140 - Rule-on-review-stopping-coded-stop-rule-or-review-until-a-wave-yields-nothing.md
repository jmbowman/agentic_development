---
id: AD-140
title: 'Rule on review stopping: coded stop rule or review until a wave yields nothing'
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-26T18:12:39Z'
labels:
  - open-question
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
  - docs/prior-art/2026-11-10-agentic-development-process-synthesis.md
  - '#98'
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Build
    order
  - docs/high-level-design.md:59-63
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 4c452121-b77a-43b0-830c-8909ca64d653
    role: created
    date: '2026-11-11'
  - agent: claude-code
    id: 291b3b59-617c-4179-adfc-3ebe1bfe3b37
    role: finished
    date: '2026-11-26'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 1 asks whether review waves continue until a wave 'yields nothing worth implementing' or follow a coded stop: one wide wave per phase, a further pass only after a verified high-severity fix or large rewrite, scoped to the change, capped at three, computed from a ledger. The note recommends the coded rule and recording a fix-caused flag so thresholds can be tuned from data. Done when the developer has ruled and the ruling is recorded in a decision doc.

**Why it matters:** Unblocks the ledger, stop-rule and orchestrator slices.

**Why the developer:** chooses between two readings of the process's intent
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ruled: review waves use fresh reviewers over the whole change as it stands, and a separate triage agent rules each finding fix now, backlog task or not worth it. Any accepted fix means another wave; the loop stops at the first wave that accepts nothing, once no fork is open. Only accepted findings are applied. It escalates to the developer, with that wave's fixes unapplied, instead of a sixth wave or when at least two and over 30% of accepted findings were introduced by the previous wave's fixes; a ruling to patch or rework restarts the count. Recorded in docs/decisions/review-wave-stopping.md and linked from the HLD Key Design Decisions. The synthesis coded rule (diff-only, capped at three) was rejected because later full-scope waves find defects in the original change. Cascade: AD-164 rescoped to the stop and escalation check; AD-199 rescoped to write the procedure; AD-163, AD-177, AD-178, AD-193, AD-200, AD-214, AD-215, AD-219, AD-226 and AD-155, AD-159 updated; AD-369 (stop-summary ordering, split from AD-180) and AD-370 (threshold revisit) created; docs/process-lessons.md points at the decision. Verified by running the rule on its own record: ten fresh full-scope review waves with separate triage (docs/review-log/2026-11-26-review-wave-stopping.md), two escalations (one by the fix-caused trigger under a broader definition, since narrowed, and one at the five-wave limit), until both reviewers found nothing worth fixing. Risk: both escalation thresholds are untested guesses (AD-370).
<!-- SECTION:FINAL_SUMMARY:END -->
