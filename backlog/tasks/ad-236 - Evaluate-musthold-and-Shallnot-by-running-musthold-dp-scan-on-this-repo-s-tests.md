---
id: AD-236
title: >-
  Evaluate musthold and Shallnot by running musthold-dp scan on this repo's
  tests
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-7
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/89
  - https://github.com/jmbowman/agentic_development/issues/90
  - docs/prior-art/2026-10-27-review-and-comprehension-burden.md
priority: medium
type: spike
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #89 asks to evaluate Shallnot and musthold before designing slice review grouped by spec ID: run musthold-dp scan on this repo's tests (read the sections musthold and Shallnot in depth in docs/prior-art/2026-10-27-review-and-comprehension-burden.md) and report whether its per-test kill data is usable. Treat the tool as untrusted: run only a pinned release in a sandbox per the global prior-art rules. Done means a short result added to the note or a tool-feedback page.

**Why it matters:** Unblocks both the spec-grouped review and test right-sizing (#90).

**Why an agent:** sandboxed tool run and write-up
<!-- SECTION:DESCRIPTION:END -->
