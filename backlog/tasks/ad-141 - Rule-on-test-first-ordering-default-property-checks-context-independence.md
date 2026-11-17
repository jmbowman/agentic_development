---
id: AD-141
title: 'Rule on test-first: ordering default, property checks, context independence'
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Synthesis Decision 2 asks whether test-first is an ordering rule or a property of the result. The recommendation has three parts: keep order as LID's default in prose with no edit-time enforcement; enforce properties mechanically (added tests fail on the base tree, the green survives a source-only re-run, citing tests ran and passed); get independence by context with a test-writing subagent that never sees the implementation, and trial the testable-design-then-parallel variant. Done when the developer rules on each part.

**Why it matters:** Gates the test-evidence slice and the independence-by-context work.

**Why the developer:** chooses between readings of intent
<!-- SECTION:DESCRIPTION:END -->
