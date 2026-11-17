---
id: AD-29
title: Cache uv and pytest caches in the check workflow
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/check-workflow/check-workflow-design.md:117
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The check workflow (`.github/workflows/check.yml`) defers caching uv and pytest caches across runs, to add when CI time matters. When it does, add caching with new CHECK specs and release tests. Done when cached runs are measurably faster.

**Why it matters:** Faster CI for every consumer.

**Why an agent:** workflow change once triggered

**Also waits on (not tracked as a task):** CI time starts to matter
<!-- SECTION:DESCRIPTION:END -->
