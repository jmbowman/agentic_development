---
id: AD-121
title: 'Build session-wrap-up slice 5: cross-repo routing'
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-21T19:18:00Z'
labels:
  - spec
milestone: m-4
dependencies: []
references:
  - docs/intent/session-wrap-up/session-wrap-up-specs.md:266-279
  - docs/intent/session-wrap-up/session-wrap-up-design.md:215-225
  - docs/intent/session-wrap-up/session-wrap-up-design.md:57
  - README.md#Status
  - WRAP-XREPO-001
  - WRAP-XREPO-002
  - WRAP-XREPO-003
  - WRAP-XREPO-004
  - WRAP-XREPO-005
  - WRAP-XREPO-006
  - WRAP-XREPO-007
  - WRAP-XREPO-008
  - WRAP-XREPO-009
  - WRAP-XREPO-010
  - WRAP-XREPO-011
  - WRAP-XREPO-012
  - >-
    docs/intent/session-wrap-up/session-wrap-up-specs.md#Cross-repo routing
    (slice 5)
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
sessions:
  - agent: claude-code
    id: 5af90670-4925-4893-9f63-86ccfe5510bf
    role: created
    date: '2026-11-04'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement step 7 of the session-wrap-up skill: never edit another repo, find a session rooted in the target repo by name pattern (`_` to `-`, plus `-` and two hex chars), message it, ask when several match, fall back to an issue on that repo via `gh repo view`, else put the draft in the report; screen drafts for private content and secrets; report delivery status and issue URLs. Specs: WRAP-XREPO-001 to WRAP-XREPO-012, including the new `skills/session-wrap-up/references/cross-repo.md` (WRAP-XREPO-012). Walk through LID with eval cases for the *(eval)* specs, manual scripts for the *(manual)* ones, and a structure test for the reference file. Done when cross-repo items become selectable, `mise run check` passes and the README status line is updated.

Cascade from the task-tracker LLD (AD-5): work for another repo is recorded as an outbox draft in this repo's backlog, which is the record; messaging a session there, an issue on that repo, and the report are ways of delivering the draft, not alternatives to writing it. Reconcile step 7 and the WRAP-XREPO specs with that when this slice walks the arrow.

**Why it matters:** Makes feedback for sibling repos reach a session that can act on it instead of sitting in a report.

**Why an agent:** specs are written; implementation and tests are agent work
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Superseded by AD-6 (2026-11-21). The session wrap-up now records work for another repo as an outbox draft in the host repo backlog, and delivering a draft (a message to a session there, or an issue on it) is the developer step the task tracker defines, so the wrap-up no longer matches sessions, sends messages or files issues on other repos. WRAP-XREPO-001, 007, 008 and 009 were restated for drafts in slice 5; WRAP-XREPO-002 to 006 and 010 to 012 were deleted. See docs/intent/session-wrap-up/session-wrap-up-design.md, Cross-repo work.
<!-- SECTION:FINAL_SUMMARY:END -->
