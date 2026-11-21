---
title: Move commit hooks to staged files if whole-project runs pass 10 seconds
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/local-checks/local-checks-design.md:104
- docs/high-level-design.md:242
priority: medium
type: feature
performer: agent
agent_tier: moderate
effort: M
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
agentic_development's success metric 'Fast hooks' wants commit-time checks under 10 seconds (tenet 5). copier-python's hooks run whole-project tasks and defer staged-file hooks until a repo grows past that. Measure hook time in the first real consumer and add staged-file mode if needed. Done when a measurement is recorded or the change is made.

**Why it matters:** Protects a system success metric.

**Why an agent:** measurement and a config change

**Also waits on (not tracked as a task):** A consumer's whole-project hooks exceed 10 seconds

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
