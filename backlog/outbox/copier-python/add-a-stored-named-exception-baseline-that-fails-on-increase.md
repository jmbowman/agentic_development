---
title: Add a stored named-exception baseline that fails on increases
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/strict-profile/strict-profile-design.md:75
- docs/high-level-design.md:241
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's HLD success metric 'Shrinking divergence' says each repo's named-exception count never rises without a recorded reason; copier-python's strict-profile LLD defers a stored per-repo baseline, with `check` failing when the count rises, until two repos are onboarded. Build it then, on top of the existing `mise run exceptions` task. Done when a rendered consumer's check fails on an unexplained increase.

**Why it matters:** Makes a system-level success metric enforceable.

**Why an agent:** a design-then-build slice with a clear trigger

**Also waits on (not tracked as a task):** Two repos onboarded to copier-python

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
