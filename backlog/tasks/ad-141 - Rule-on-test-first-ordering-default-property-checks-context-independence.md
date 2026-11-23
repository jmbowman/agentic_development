---
id: AD-141
title: 'Rule on test-first: ordering default, property checks, context independence'
status: To Do
assignee: []
created_date: '2026-11-16'
updated_date: '2026-11-23T11:17:00Z'
labels:
  - open-question
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#Tensions
    and open questions for the developer
  - >-
    https://github.com/stablyai/orca/blob/main/docs/agents-md-refs/test-antipatterns.md
  - docs/wiki/success-stories/orca.md
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

## Comments

<!-- COMMENTS:BEGIN -->
author: 27e13044-1d02-40c4-90d7-0134d1214b1d
created: 2026-11-23T11:17:00Z

---

Prior art for the property checks: Orca keeps a test only if it fails when the change is reverted, hardcodes its expected values (never computed by production code), and runs at the one layer that owns the behavior, and bans a list of anti-patterns (docs/wiki/success-stories/orca.md, practice 4). Its default of adding no tests conflicts with LID's tests-first rule, so the criteria are what carry over.

---
<!-- COMMENTS:END -->
