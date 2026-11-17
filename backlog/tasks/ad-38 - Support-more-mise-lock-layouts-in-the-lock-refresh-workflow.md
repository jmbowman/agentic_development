---
id: AD-38
title: Support more mise lock layouts in the lock-refresh workflow
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/lock-refresh/lock-refresh-design.md:85
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The lock-refresh workflow supports only `mise.lock` and `.config/mise/mise.lock`; `.mise.lock`, `.config/mise.lock` and environment-specific lock files are deferred until a consumer needs one. Done when the needed layout is supported with specs and tests.

**Why it matters:** Only matters for consumers with other layouts.

**Why an agent:** workflow change once triggered

**Also waits on (not tracked as a task):** a consumer needs another lock layout
<!-- SECTION:DESCRIPTION:END -->
