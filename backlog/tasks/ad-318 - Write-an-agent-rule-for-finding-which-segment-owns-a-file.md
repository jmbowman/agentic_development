---
id: AD-318
title: Write an agent rule for finding which segment owns a file
status: Done
assignee: []
created_date: '2026-11-18T04:30:00Z'
updated_date: '2026-11-18T05:04:00Z'
labels: []
milestone: m-8
dependencies: []
references:
  - docs/prior-art/2026-11-17-in-repo-architecture-maps.md#Verdict
priority: low
type: docs
ordinal: 5000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 2026-11-17 architecture-maps note (docs/prior-art/2026-11-17-in-repo-architecture-maps.md, Verdict) keeps LID's design tree as the map agents read, plus a lookup rule. Write that rule into AGENTS.md: a file's owner is the segment its @spec IDs point to (git grep -n @spec <file>, then grep the ID under docs/intent/); for files with no @spec line, the HLD's Components table (Lives in column), then a grep of the path in docs/intent/*/*-design.md. Note that some LLDs name related segments in prose, but nothing records neighbours systematically yet. Done when the rule is in AGENTS.md and checks pass.

**Why it matters:** Covers the note's first common use (an agent looks up a file's owner) with no new tool.

**Why an agent:** the rule's content is stated in the note
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the 'Which segment owns a file' working rule to AGENTS.md: @spec lines, then the HLD Components table, then a path grep of the design docs; unowned files are named shared infrastructure. Tried on skills/session-wrap-up/SKILL.md, scripts/tasks.py, .github/workflows/check.yml and tests/conftest.py.
<!-- SECTION:FINAL_SUMMARY:END -->
