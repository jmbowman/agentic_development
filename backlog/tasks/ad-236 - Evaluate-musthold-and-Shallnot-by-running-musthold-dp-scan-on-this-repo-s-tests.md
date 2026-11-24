---
id: AD-236
title: >-
  Evaluate musthold and Shallnot by running musthold-dp scan on this repo's
  tests
status: Done
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-24T04:28:00Z'
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
sessions:
  - agent: claude-code
    id: 5129029a-6c2e-4c0b-bd91-f3da2e301b01
    role: worked
    date: '2026-11-23'
  - agent: claude-code
    id: 5129029a-6c2e-4c0b-bd91-f3da2e301b01
    role: finished
    date: '2026-11-23'
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #89 asks to evaluate Shallnot and musthold before designing slice review grouped by spec ID: run musthold-dp scan on this repo's tests (read the sections musthold and Shallnot in depth in docs/prior-art/2026-10-27-review-and-comprehension-burden.md) and report whether its per-test kill data is usable. Treat the tool as untrusted: run only a pinned release in a sandbox per the global prior-art rules. Done means a short result added to the note or a tool-feedback page.

**Why it matters:** Unblocks both the spec-grouped review and test right-sizing (#90).

**Why an agent:** sandboxed tool run and write-up
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ran musthold-dp 0.1.1 (release discpower/v0.1.1, checksum and attestation verified) on this repo at 08d178f in a bubblewrap sandbox with no network. Result recorded in docs/prior-art/2026-10-27-review-and-comprehension-burden.md, section "musthold-dp scan trial (2026-11-23)": the kill data is readable but covers too little of this repo to build on, so the verdict stays borrow ideas. The quick scan ran no mutant (reference runs outlast its budget); the full scan judged 9 of 40 sampled tests, and the other 31 own no mutable line (non-Python files, subprocess-run scripts, logic under tests/). Verified by one review wave that recomputed every number from the scan statement (docs/review-log/2026-11-23-prior-art-review-burden.md). Not tried: --base, --host, --sample, --workers. Risk: the reasons tests went unjudged are read from the tests, since the scan writes no per-test coverage.
<!-- SECTION:FINAL_SUMMARY:END -->
