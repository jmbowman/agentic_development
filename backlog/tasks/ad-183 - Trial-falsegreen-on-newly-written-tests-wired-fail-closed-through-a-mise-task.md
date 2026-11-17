---
id: AD-183
title: Trial falsegreen on newly written tests, wired fail-closed through a mise task
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - prior-art
milestone: m-6
dependencies: []
references:
  - >-
    docs/prior-art/2026-11-10-agentic-development-process-synthesis.md#8.
    Verification of tests against requirements
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adopt falsegreen (MIT, pure Python) as a static check on newly written tests at the tests stop, run through this repo's own mise task so it fails closed (not its fail-open pre-commit hook), after a trial for false alarms on this repo's test files. Done when the task exists or the trial's false-alarm findings explain why not.

**Why it matters:** Finds tests that can never fail.

**Why an agent:** integration and trial
<!-- SECTION:DESCRIPTION:END -->
