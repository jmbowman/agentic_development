---
title: Split a copier-base layer when a second template layer is needed
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- open-question
references:
- copier-python:docs/intent/baseline-files/baseline-files-design.md:210
- copier-python:docs/high-level-design.md:107
- https://github.com/jmbowman/agentic_development/issues/54
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
copier-python keeps base concerns (hooks, mise base, stubs, skills pin, session hook, LID version gate) until a second language or documentation layer needs them, then splits out `copier-base` and consumers move to two answers files. agentic_development issue #54 (docs site) asks for the template to give every project the same docs-site setup, which would be the first documentation layer and so the trigger. Done when the split is designed in both HLDs and released, or #54 is placed elsewhere.

**Why it matters:** Lets a docs or second-language layer reuse the base without duplicating it.

**Why an agent:** a design-then-build slice once a second layer is decided

**Also waits on (not tracked as a task):** Decision to add a documentation template layer (agentic_development #54)

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
