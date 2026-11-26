---
id: AD-82
title: Triage the harvester-literature run and mark the PRIOR-SCR agent-use specs
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-25T19:00:08Z'
labels:
  - spec
milestone: m-3
dependencies:
  - AD-43
references:
  - docs/intent/prior-art-search/prior-art-search-specs.md:236-261
  - docs/review-log/README.md
priority: medium
type: review
performer: agent
agent_tier: strong
effort: S
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 6becb69f-47c5-4e32-b087-a3ab5e8fc7dd
    role: worked
    date: '2026-11-25'
  - agent: claude-code
    id: 6becb69f-47c5-4e32-b087-a3ab5e8fc7dd
    role: finished
    date: '2026-11-25'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Triage the harvester-literature re-run, fix skill or grader faults, append the review-log row, update latest-results, and mark PRIOR-SCR-100 to -110, -120 and -121 `[x]` once they pass.

**Why it matters:** Closes the harvester agent-use spec gaps.

**Why an agent:** triage and doc updates are agent work
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Triaged the 2026-11-25 run of `harvester-literature` against its full trace, because the judges saw only the first 100,024 characters. Every grader condition held except one: after arXiv rate-limited round 1, the arXiv subagent reran the same queries three minutes later under `--round 2`. The developer ruled that a skill failure. Marked `[x]` on the trace: PRIOR-SCR-100, 101, 105, 108, 110, 120, 121 and 134. Left open: 102, 103, 104, 106, 107 and 109, whose conditions the run never reached or failed. The fix says what makes a round later: PRIOR-SCR-136 to 146 and a narrowed 107, the design paragraph under "Running a query again" with its Decisions row, the pasted rules block and `references/harvester.md`, and the `harvester-output` grader. Two review waves (20 and 8 findings) and an edge audit (12) are in `docs/review-log/2026-11-25-prior-art-search-harvester.md`. Verified by `mise run check`, `mise run lid` and the task check; the new rules themselves are verified only by the eval, so AD-363 re-runs it. Risk: several grader conditions are judgment calls a judge cannot decide mechanically, and the judges still cannot see past the start of the trace.
<!-- SECTION:FINAL_SUMMARY:END -->
