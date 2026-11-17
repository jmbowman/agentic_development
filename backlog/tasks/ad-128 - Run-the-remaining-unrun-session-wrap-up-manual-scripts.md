---
id: AD-128
title: Run the remaining unrun session-wrap-up manual scripts
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-4
dependencies: []
references:
  - evals/session-wrap-up/manual.md:18-58
  - evals/session-wrap-up/manual.md:228-315
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Several session-wrap-up manual scripts outside the approval gate have no result lines in `evals/session-wrap-up/manual.md`: Outside a git repo (WRAP-LOOSE-003), A wrap-up request from another agent (WRAP-RUN-009), No stated memory location (WRAP-RULE-008), A real compaction (WRAP-LES-015, WRAP-LES-027), Applying items after the report (WRAP-RUN-013), Hooks check after a real compaction (WRAP-NOTES-015) and The hooks' request during a wrap-up (WRAP-NOTES-019, -020). Their specs are `[x]`. Run them (or replace them with scenarios once the harness is pinned) and append dated results.

**Why it matters:** Verifies safety-relevant behavior (other agents' requests, compaction) that no eval covers.

**Why the developer:** live interactive sessions are run by the developer
<!-- SECTION:DESCRIPTION:END -->
