---
title: Decide how the template brings inline-snapshot and its test guidance
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- issue
references:
- https://github.com/jmbowman/copier-python/issues/48
- copier-python:docs/high-level-design.md:13
- copier-python:docs/intent/baseline-files/baseline-files-design.md:209
- docs/high-level-design.md:61
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue copier-python#48 wants `inline-snapshot` as the default for new output-shaped tests, paired with test-authoring guidance agents follow. Two choices block it: the template never rewrites `pyproject.toml` (copier-python HLD Approach), so it can't add a dev dependency itself; and the guidance has no home yet (template AGENTS.md fragments are deferred, and path-scoped rule files are a planned, undesigned agentic_development component). Decide where the dependency and the guidance live. Done when the choice is recorded.

**Why it matters:** Cuts review burden for output-shaped tests in every consumer.

**Why the developer:** chooses between design options across two repos

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
