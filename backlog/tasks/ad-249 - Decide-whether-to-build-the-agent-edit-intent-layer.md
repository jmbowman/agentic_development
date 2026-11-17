---
id: AD-249
title: Decide whether to build the agent-edit intent layer
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-7
dependencies:
  - AD-248
references:
  - docs/prior-art/2026-10-30-change-presentation.md#Verdict
  - docs/prior-art/2026-10-30-change-presentation.md#Refresh trigger
  - >-
    docs/prior-art/2026-10-30-change-presentation.md#Limitations checked in
    source
priority: low
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verdict's one build: capture each agent edit (old and new text, file, slice) from a PostToolUse hook on Edit and Write, group edits by purpose and EARS ID (#89), let the agent declare mechanical changes as replayable rules and show the unexplained residue next to the full diff, with intent shown as a claim, never in place of the diff. Decide whether and when to start it. Before designing, re-run the prior-art search (the note's refresh trigger) including a pass for Rust unified-diff parser crates. Done when the decision is recorded.

**Why it matters:** Gates the largest custom piece in the change-presentation verdict.

**Why the developer:** Choosing to commit to a new component through LID's HLD stop
<!-- SECTION:DESCRIPTION:END -->
