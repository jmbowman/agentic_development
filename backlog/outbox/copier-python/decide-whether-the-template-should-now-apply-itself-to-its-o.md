---
title: Decide whether the template should now apply itself to its own repo
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/baseline-files/baseline-files-design.md:208
- copier-python:docs/high-level-design.md:108-110
- docs/high-level-design.md:235
priority: medium
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
copier-python's baseline-files LLD defers applying the template to its own repo 'until the first release is stable', and both HLDs say the tooling repos' own hand-written CI and config change 'once the template applies itself to its own repo'. copier-python is now at v0.3.1 with three minor releases. Decide whether the trigger has fired, and whether agentic_development would follow. Done when the deferred item is either scheduled as a slice or given a concrete new trigger.

**Why it matters:** Removes the hand-maintained duplicate config in the tooling repos.

**Why the developer:** judging release stability is the developer's call

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
