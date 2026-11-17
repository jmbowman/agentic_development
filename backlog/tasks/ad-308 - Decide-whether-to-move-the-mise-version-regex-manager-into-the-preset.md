---
id: AD-308
title: Decide whether to move the mise-version regex manager into the preset
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - surfaced
milestone: m-9
dependencies: []
references:
  - >-
    docs/intent/repo-setup/repo-setup-design.md#Open Questions & Future
    Decisions
  - copier-python:docs/intent/cloud-sessions/cloud-sessions-design.md:91
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's repo-setup LLD defers moving its session hook's mise-version regex manager into the shared Renovate preset 'when the template ships a hook of its own'; copier-python now ships one (cloud-sessions LLD), but its own deferred item uses a different trigger: 'if several templates ship the hook'. The two docs disagree on when to act. Decide the trigger and record it in both. Done when the two deferred items agree.

**Why it matters:** Avoids two Renovate rules drifting for the same mise pin.

**Why the developer:** chooses between two recorded readings of intent
<!-- SECTION:DESCRIPTION:END -->
