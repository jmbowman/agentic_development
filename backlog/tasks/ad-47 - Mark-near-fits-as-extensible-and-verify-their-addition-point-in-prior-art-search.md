---
id: AD-47
title: >-
  Mark near-fits as extensible and verify their addition point in
  prior-art-search
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
  - partly-done
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/191
  - skills/prior-art-search/SKILL.md:86
  - docs/prior-art/2026-11-07-search-harvest-pipeline.md
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #191: a candidate that fails a hard criterion only because a small addition could fix it is excluded before step 10, so the blend is never weighed (harvest-pipeline search: 15 multi-service clients were dismissed, then a second pass found several with one request chokepoint). Change steps 7-9 of skills/prior-art-search/SKILL.md so such candidates get support value extensible with the addition's size, the top near-fits in each class are verified for the addition point, and the report lists class-level options (wrap, extend, contribute upstream, fork) with rough size. Note `extensible` already exists as a support value (SKILL.md line 86); the procedure must make the agent test for it. LID pass with specs, tests and an eval case.

**Why it matters:** Prevents wrongly dismissing a whole class of tools that one small wrapper would fix.

**Why an agent:** skill and spec edits following a written proposal

**Status when filed (partly-done):** the extensible value exists in SKILL.md and verification.md, but the test-for-it procedure and class-level options are not there
<!-- SECTION:DESCRIPTION:END -->
