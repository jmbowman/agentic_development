---
id: AD-131
title: Support issue capture and routing on forges other than GitHub
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - open-question
milestone: m-4
dependencies:
  - AD-117
references:
  - docs/intent/session-wrap-up/session-wrap-up-design.md:331
  - docs/high-level-design.md#Non-Goals
priority: low
type: feature
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The session-wrap-up design defers issue capture and issue routing on forges such as GitLab; until then a host repo `gh` can't reach takes the no-issue route. HLD non-goals keep other forges out for now. Implement when a host repo on another forge needs it. Done when the wrap-up can file on that forge.

**Why it matters:** Only matters once a non-GitHub repo is in use.

**Why an agent:** build work once triggered

**Also waits on (not tracked as a task):** a host repo on a non-GitHub forge needs it
<!-- SECTION:DESCRIPTION:END -->
