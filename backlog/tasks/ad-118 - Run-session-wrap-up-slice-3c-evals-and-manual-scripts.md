---
id: AD-118
title: Run session-wrap-up slice 3c evals and manual scripts
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - spec
milestone: m-4
dependencies:
  - AD-117
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:35
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:237-254
  - evals/session-wrap-up/manual.md
priority: medium
type: eval
performer: human
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once slice 3c is built, run its eval case for WRAP-GATE-034 with `mise run eval` and the manual scripts for the *(manual)* issue-capture and fast-check specs (WRAP-GATE-024 to -030, -037 to -039, -011, -012, -032, -033) in a live Claude Code session, then paste the output for triage. Done when each has a dated result and a review-log row exists.

**Why it matters:** Verifies the first slice in which the skill files issues in the developer's name.

**Why the developer:** paid eval runs and live interactive sessions are run by the developer
<!-- SECTION:DESCRIPTION:END -->
