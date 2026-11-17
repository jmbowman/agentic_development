---
id: AD-30
title: Decide on job timeout and concurrency limits for the check workflow
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/check-workflow/check-workflow-design.md:118
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The check workflow design defers job timeout and concurrency limits, with no stated trigger. Decide whether to add them and with what values. Done when recorded in the check-workflow design.

**Why it matters:** Bounds runaway CI minutes.

**Why the developer:** a policy choice with no stated trigger
<!-- SECTION:DESCRIPTION:END -->
