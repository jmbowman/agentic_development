---
id: AD-238
title: Design slice review grouped by EARS ID on lidc's spec-to-test-to-code links
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-7
dependencies:
  - AD-236
references:
  - https://github.com/jmbowman/agentic_development/issues/89
  - https://github.com/jmbowman/agentic_development/issues/91
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue #89: show each slice's diff grouped by EARS ID (spec line diff, tests citing it, code under its @spec annotation, then a bucket for changes tied to no spec). Build on lidc's links, after the musthold and Shallnot evaluation, walking LID (HLD, LLD, EARS) and checking whether it should be a LID enhancement upstream. The 2026-10-30 comment on #91 also suggests a rendered changed-sections-only view with a heading breadcrumb overlaps this. Done means a reviewed design.

**Why it matters:** Reviewers see each requirement with its tests and code together.

**Why an agent:** LID design drafting with developer review at stops
<!-- SECTION:DESCRIPTION:END -->
