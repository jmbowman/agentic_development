---
title: Exempt third-party skill scripts from the strict profile when needed
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/baseline-files/baseline-files-design.md:215
- docs/high-level-design.md:164
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A consumer that deploys a third-party skill with its own `apm.yml` gets that skill's scripts under `.claude/skills/`, which the strict ruff and ty profile would check. copier-python defers an exemption until the first such skill needs it (agentic_development's HLD says a skill's scripts are linted only in their own repo). Done when the first such case is handled with a spec'd exclusion, or the item is closed.

**Why it matters:** Keeps consumer checks green when they add packaged skills.

**Why an agent:** a small config change once a case exists

**Also waits on (not tracked as a task):** A consumer deploys a third-party skill with scripts

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
