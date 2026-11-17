---
id: AD-40
title: Support the cloud-session hook on platforms beyond Linux x86-64
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-2
dependencies: []
references:
  - docs/intent/repo-setup/repo-setup-design.md:128
priority: low
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The repo-setup design defers other platforms for the SessionStart hook, if cloud sessions ever run on anything but Linux x86-64. Done when the hook installs tools on the new platform.

**Why it matters:** Only matters if the cloud platform changes.

**Why an agent:** hook change once triggered

**Also waits on (not tracked as a task):** cloud sessions run on another platform
<!-- SECTION:DESCRIPTION:END -->
