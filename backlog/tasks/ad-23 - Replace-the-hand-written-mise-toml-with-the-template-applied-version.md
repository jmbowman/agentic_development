---
id: AD-23
title: Replace the hand-written mise.toml with the template-applied version
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - loose-end
milestone: m-2
dependencies: []
references:
  - mise.toml:1
priority: medium
type: chore
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
mise.toml's first line says it is 'hand-written until a template applies itself here'. When copier-python can apply itself to this repo, regenerate mise.toml from the template, keeping this repo's own tools (lidc, apm, renovate) and tasks (skills, eval), and check `mise run check` still passes with no virtualenv active. Done when the header comment is gone and the file is template-managed.

**Why it matters:** Keeps this repo's tooling in step with the template it dogfoods.

**Why an agent:** mechanical once the template can self-apply

**Also waits on (not tracked as a task):** copier-python template that can apply itself to this repo
<!-- SECTION:DESCRIPTION:END -->
