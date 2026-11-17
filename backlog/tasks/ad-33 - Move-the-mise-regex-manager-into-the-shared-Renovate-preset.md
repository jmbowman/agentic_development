---
id: AD-33
title: Move the mise regex manager into the shared Renovate preset
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies:
  - AD-308
references:
  - docs/intent/repo-setup/repo-setup-design.md:127
  - docs/intent/repo-setup/repo-setup-design.md:121
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repo-setup design defers moving the regex manager (which keeps the cloud-session hook's mise version in step) into the shared preset, until the template ships a hook of its own. Do it then, with preset specs. Done when consumers' hooks get the same bump.

**Why it matters:** Keeps consumer hooks' mise versions current automatically.

**Why an agent:** preset change once triggered

**Also waits on (not tracked as a task):** the template ships a SessionStart hook of its own
<!-- SECTION:DESCRIPTION:END -->
